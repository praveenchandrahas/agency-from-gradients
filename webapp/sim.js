/* agency-from-gradients: browser/Node port of the Python engine (src/agency_gradients/world.py).
 * Same rules and default parameters; a different random-number generator, so runs are
 * statistically comparable to the Python ones but not bit-identical.
 * Only the "equivariant" (27-parameter) policy is ported. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AGSim = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const DEFAULTS = {
    size: 32, maxPop: 200, initPop: 60,
    metabolism: 0.10, moveCost: 0.03, investCost: 0.15, initEnergy: 8.0,
    reproThresh: 12.0, reproCost: 6.0, childShare: 0.8, eatRate: 0.5, hazard: 0.003,
    commonsCap: 1.0, commonsRegrow: 0.008, commonsRegrowAbundant: 0.08,
    patchiness: 1.0, nPatches: 18, patchSigma: 3.5,
    nTier1: 12, stock1: 150, regrow1: 0.30, lock1: 3.0, decay1: 0.02, harvest1: 1.5,
    nTier2: 4, stock2: 800, regrow2: 1.6, lock2: 25.0, decay2: 0.15, harvest2: 6.0,
    scentSigma: 4.0, reservoirLeak: 0.002, depletedAt: 1.0,
    mutSigma: 0.30, mutRate: 0.10,
    selection: "persistence", // persistence | entropy | drift
    driftRestore: 0.05, entropyReproSpent: 12.0, kappa: 3.0,
    scarcity: true, heredity: true, mortality: true, succession: true,
  };
  const NCH = 7, NG = NCH * 3 + 6;
  // N, E, S, W, stay, invest
  const DX = [-1, 0, 1, 0, 0, 0], DY = [0, 1, 0, -1, 0, 0];

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  class World {
    constructor(opts, seed) {
      const c = this.cfg = Object.assign({}, DEFAULTS, opts || {});
      this.seed = seed >>> 0;
      this._r = mulberry32(this.seed);
      const L = c.size, N = L * L;
      this.L = L;
      this.commons = new Float64Array(N).fill(c.commonsCap);
      this.ttype = new Int8Array(N);
      this.stock = new Float64Array(N);
      this.progress = new Float64Array(N);
      this.unlocked = new Uint8Array(N);
      this.scent = [new Float64Array(N), new Float64Array(N)];
      this.t2Budget = 0;
      this.field = this._makeField();
      this._placeSites();
      this._updateScent();

      const M = c.maxPop;
      this.alive = new Uint8Array(M);
      this.x = new Int16Array(M); this.y = new Int16Array(M);
      this.energy = new Float64Array(M);
      this.age = new Int32Array(M);
      this.lineage = new Int32Array(M);
      this.genome = new Float64Array(M * NG);
      this.spentAcc = new Float64Array(M);
      this.t = 0;
      this.policy = null; // optional hand-coded forager
      this.stats = { gainC: 0, gain1: 0, gain2: 0, leak: 0, heat: 0, births: 0, deaths: 0 };
      this.cum = { gainC: 0, gain1: 0, gain2: 0, leak: 0, heat: 0, births: 0, deaths: 0 };
      this.firstUnlock = { 1: null, 2: null };
      this.converted = 0;
      this.cnt = new Float64Array(N);
      for (let i = 0; i < c.initPop; i++) {
        const s = i;
        this.alive[s] = 1; this.x[s] = this.randInt(L); this.y[s] = this.randInt(L);
        this.energy[s] = c.initEnergy; this.lineage[s] = i;
        for (let k = 0; k < NG; k++) this.genome[s * NG + k] = this.randn();
      }
    }
    rand() { return this._r(); }
    randInt(n) { return Math.floor(this._r() * n); }
    randn() {
      let u = 0; while (u === 0) u = this._r();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * this._r());
    }
    gumbel() { let u = 0; while (u === 0) u = this._r(); return -Math.log(-Math.log(u)); }
    poisson(l) { const e = Math.exp(-l); let k = 0, p = 1; do { k++; p *= this._r(); } while (p > e && k < 100); return k - 1; }

    _dist(a, b) { const d = Math.abs(a - b); return Math.min(d, this.L - d); }
    _makeField() {
      const c = this.cfg, L = this.L, f = new Float64Array(L * L);
      if (c.patchiness <= 0) return f.fill(1);
      for (let p = 0; p < c.nPatches; p++) {
        const px = this.randInt(L), py = this.randInt(L);
        for (let i = 0; i < L; i++) for (let j = 0; j < L; j++) {
          const dx = this._dist(i, px), dy = this._dist(j, py);
          f[i * L + j] += Math.exp(-(dx * dx + dy * dy) / (2 * c.patchSigma * c.patchSigma));
        }
      }
      const norm = (arr) => { let m = 0; for (const v of arr) m += v; m /= arr.length; for (let i = 0; i < arr.length; i++) arr[i] /= m; };
      norm(f);
      for (let i = 0; i < f.length; i++) f[i] = (1 - c.patchiness) + c.patchiness * f[i];
      norm(f);
      return f;
    }
    _placeSites() {
      const c = this.cfg, L = this.L, N = L * L;
      const cells = []; const used = new Set();
      while (cells.length < c.nTier1 + c.nTier2) { const v = this.randInt(N); if (!used.has(v)) { used.add(v); cells.push(v); } }
      for (let i = 0; i < c.nTier1; i++) { this.ttype[cells[i]] = 1; this.stock[cells[i]] = c.stock1; }
      if (c.succession) this.t2Budget = c.nTier2;
      else for (let i = c.nTier1; i < cells.length; i++) { this.ttype[cells[i]] = 2; this.stock[cells[i]] = c.stock2; }
    }
    _updateScent() {
      const c = this.cfg, L = this.L;
      for (let k = 0; k < 2; k++) {
        const f = this.scent[k]; f.fill(0);
        for (let s = 0; s < L * L; s++) {
          if (this.ttype[s] !== k + 1) continue;
          const sx = Math.floor(s / L), sy = s % L;
          for (let i = 0; i < L; i++) for (let j = 0; j < L; j++) {
            const dx = this._dist(i, sx), dy = this._dist(j, sy);
            f[i * L + j] += Math.exp(-(dx * dx + dy * dy) / (2 * c.scentSigma * c.scentSigma));
          }
        }
        for (let i = 0; i < f.length; i++) if (f[i] > 1) f[i] = 1;
      }
    }
    openness(i) {
      const tt = this.ttype[i]; if (!tt) return 0;
      return Math.min(this.progress[i] / (tt === 1 ? this.cfg.lock1 : this.cfg.lock2), 1);
    }
    count() { let n = 0; for (let i = 0; i < this.alive.length; i++) n += this.alive[i]; return n; }

    _envUpdate() {
      const c = this.cfg, N = this.L * this.L;
      let leak = 0;
      const reg = c.scarcity ? c.commonsRegrow : c.commonsRegrowAbundant;
      for (let i = 0; i < N; i++) {
        let v = this.commons[i] + reg * this.field[i];
        if (v > c.commonsCap) { leak += v - c.commonsCap; v = c.commonsCap; }
        this.commons[i] = v;
        const tt = this.ttype[i];
        if (tt) {
          let s = this.stock[i] + (tt === 1 ? c.regrow1 : c.regrow2);
          const lk = s * c.reservoirLeak; s -= lk; leak += lk; this.stock[i] = s;
          this.progress[i] *= 1 - (tt === 1 ? c.decay1 : c.decay2);
          this.unlocked[i] = this.progress[i] >= (tt === 1 ? c.lock1 : c.lock2) ? 1 : 0;
        }
      }
      if (c.succession && this.t2Budget > 0) {
        let changed = false;
        for (let i = 0; i < N && this.t2Budget > 0; i++) {
          if (this.ttype[i] === 1 && this.stock[i] <= c.depletedAt) {
            this.ttype[i] = 2; this.stock[i] = c.stock2; this.progress[i] = 0; this.unlocked[i] = 0;
            this.t2Budget--; this.converted++; changed = true;
          }
        }
        if (changed) this._updateScent();
      }
      return leak;
    }

    _chan(cell, ch) {
      const c = this.cfg;
      switch (ch) {
        case 0: return this.commons[cell] / c.commonsCap;
        case 5: return this.scent[0][cell];
        case 6: return this.scent[1][cell];
        default: {
          const tt = this.ttype[cell];
          if (!tt || this.stock[cell] <= c.depletedAt) return 0;
          const fr = this.openness(cell);
          if (ch === 1) return tt === 1 ? 1 - fr : 0;
          if (ch === 2) return tt === 1 ? fr : 0;
          if (ch === 3) return tt === 2 ? 1 - fr : 0;
          return tt === 2 ? fr : 0;
        }
      }
    }

    _decide(a) {
      const L = this.L, c = this.cfg;
      const cells = [0, 0, 0, 0, 0];
      for (let d = 0; d < 5; d++) cells[d] = ((this.x[a] + DX[d] + L) % L) * L + ((this.y[a] + DY[d] + L) % L);
      if (this.policy) return this.policy(this, a, cells);
      const g = this.genome, o = a * NG, E = this.energy[a] / c.reproThresh;
      const lg = [0, 0, 0, 0, 0, 0];
      let stay = g[o + 3 * NCH + 1] + g[o + 3 * NCH + 4] * E;
      let inv = g[o + 3 * NCH + 2] + g[o + 3 * NCH + 5] * E;
      const bm = g[o + 3 * NCH] + g[o + 3 * NCH + 3] * E;
      for (let ch = 0; ch < NCH; ch++) {
        const wn = g[o + ch], ws = g[o + NCH + ch], wi = g[o + 2 * NCH + ch];
        for (let d = 0; d < 4; d++) lg[d] += wn * this._chan(cells[d], ch);
        const here = this._chan(cells[4], ch);
        stay += ws * here; inv += wi * here;
      }
      for (let d = 0; d < 4; d++) lg[d] += bm;
      lg[4] = stay; lg[5] = inv;
      let best = -1e9, act = 0;
      for (let k = 0; k < 6; k++) { const v = lg[k] + this.gumbel(); if (v > best) { best = v; act = k; } }
      return act;
    }

    step() {
      const c = this.cfg, L = this.L, N = L * L, M = c.maxPop;
      const leak = this._envUpdate();
      const idx = []; for (let a = 0; a < M; a++) if (this.alive[a]) idx.push(a);
      let gC = 0, g1 = 0, g2 = 0, heat = 0, births = 0, deaths = 0;
      if (idx.length) {
        const acts = new Int8Array(idx.length), cost = new Float64Array(idx.length);
        for (let k = 0; k < idx.length; k++) acts[k] = this._decide(idx[k]);
        this.cnt.fill(0);
        for (let k = 0; k < idx.length; k++) {
          const a = idx[k], act = acts[k];
          cost[k] = c.metabolism + (act < 4 ? c.moveCost : 0) + (act === 5 ? c.investCost : 0);
          this.x[a] = (this.x[a] + DX[act] + L) % L; this.y[a] = (this.y[a] + DY[act] + L) % L;
          const cell = this.x[a] * L + this.y[a];
          this.cnt[cell] += 1;
          if (act === 5 && this.ttype[cell]) this.progress[cell] += 1;
        }
        // cap progress, detect rising edges
        for (let i = 0; i < N; i++) {
          const tt = this.ttype[i]; if (!tt) continue;
          const lock = tt === 1 ? c.lock1 : c.lock2;
          if (this.progress[i] > 2 * lock) this.progress[i] = 2 * lock;
          const now = this.progress[i] >= lock ? 1 : 0;
          if (now && !this.unlocked[i] && this.firstUnlock[tt] === null) this.firstUnlock[tt] = this.t;
          this.unlocked[i] = now;
        }
        // shared eating
        const takeC = new Float64Array(N), takeR = new Float64Array(N);
        for (let i = 0; i < N; i++) {
          if (!this.cnt[i]) continue;
          takeC[i] = Math.min(c.eatRate * this.cnt[i], this.commons[i]); this.commons[i] -= takeC[i];
          const tt = this.ttype[i];
          if (tt) {
            const hr = (tt === 1 ? c.harvest1 : c.harvest2) * this.openness(i);
            takeR[i] = Math.min(hr * this.cnt[i], this.stock[i]); this.stock[i] -= takeR[i];
          }
        }
        for (let k = 0; k < idx.length; k++) {
          const a = idx[k], cell = this.x[a] * L + this.y[a], n = this.cnt[cell];
          const gc = takeC[cell] / n, gr = takeR[cell] / n, tt = this.ttype[cell];
          gC += gc; if (tt === 1) g1 += gr; else if (tt === 2) g2 += gr;
          this.energy[a] += gc + gr - cost[k];
          this.spentAcc[a] += cost[k]; this.age[a]++; heat += cost[k];
          let dead = this.energy[a] <= 0;
          if (c.mortality && !dead && this.rand() < c.hazard) dead = true;
          if (dead) {
            if (c.mortality) { this.alive[a] = 0; deaths++; } else this.energy[a] = 1.0;
          }
        }
        births = this._reproduce();
      }
      this.t++;
      const s = this.stats, cm = this.cum;
      s.gainC = gC; s.gain1 = g1; s.gain2 = g2; s.leak = leak; s.heat = heat; s.births = births; s.deaths = deaths;
      cm.gainC += gC; cm.gain1 += g1; cm.gain2 += g2; cm.leak += leak; cm.heat += heat; cm.births += births; cm.deaths += deaths;
    }

    _reproduce() {
      const c = this.cfg, M = c.maxPop;
      const a = []; for (let i = 0; i < M; i++) if (this.alive[i]) a.push(i);
      if (!a.length) return 0;
      let parents = [];
      const viable = (i) => this.energy[i] >= c.reproCost + 1.0;
      if (c.selection === "persistence") parents = a.filter((i) => this.energy[i] >= c.reproThresh);
      else if (c.selection === "entropy") parents = a.filter((i) => this.spentAcc[i] >= c.entropyReproSpent && viable(i));
      else if (c.selection === "drift") {
        const lam = c.driftRestore * Math.max(c.initPop - a.length, 0);
        let nb = Math.min(this.poisson(lam), a.length);
        const pool = a.slice();
        for (let i = pool.length - 1; i > 0; i--) { const j = this.randInt(i + 1); [pool[i], pool[j]] = [pool[j], pool[i]]; }
        parents = pool.slice(0, nb).filter(viable);
      } else throw new Error("unknown selection " + c.selection);
      if (!parents.length) return 0;
      for (let i = parents.length - 1; i > 0; i--) { const j = this.randInt(i + 1); [parents[i], parents[j]] = [parents[j], parents[i]]; }
      const free = []; for (let i = 0; i < M && free.length < parents.length; i++) if (!this.alive[i]) free.push(i);
      const k = Math.min(parents.length, free.length);
      for (let q = 0; q < k; q++) {
        const p = parents[q], s = free[q];
        for (let g = 0; g < NG; g++) {
          if (c.heredity) this.genome[s * NG + g] = this.genome[p * NG + g] + (this.rand() < c.mutRate ? c.mutSigma * this.randn() : 0);
          else this.genome[s * NG + g] = this.randn();
        }
        this.energy[p] -= c.reproCost; this.spentAcc[p] = 0;
        this.alive[s] = 1; this.x[s] = this.x[p]; this.y[s] = this.y[p];
        this.energy[s] = c.reproCost * c.childShare; this.age[s] = 0; this.spentAcc[s] = 0; this.lineage[s] = this.lineage[p];
      }
      return k;
    }
  }

  /* Hand-coded forager (positive control): follows food and glow, invests at reservoirs. */
  function oracle(world, a, cells) {
    const ch = (cell, c) => world._chan(cell, c);
    const score = cells.map((cell) => ch(cell, 0) + 2 * ch(cell, 5) + 2 * ch(cell, 6) + 4 * (ch(cell, 1) + ch(cell, 2) + ch(cell, 3) + ch(cell, 4)));
    let best = 0, bv = -1e9;
    for (let d = 0; d < 4; d++) { const v = score[d] + world.rand() * 0.05; if (v > bv) { bv = v; best = d; } }
    const here = cells[4];
    const stay = score[4] >= Math.max(score[0], score[1], score[2], score[3]) && ch(here, 0) > 0.3;
    let act = stay ? 4 : best;
    const onRes = ch(here, 1) + ch(here, 2) + ch(here, 3) + ch(here, 4) > 0;
    const open = ch(here, 2) + ch(here, 4);
    if (onRes && (open < 0.999 || world.rand() < 0.15)) act = 5;
    if (world.rand() < 0.1) act = world.randInt(6);
    return act;
  }

  /* Rolling summary comparable to Python's World.summary() (last quarter of a finished run). */
  class Recorder {
    constructor(world) { this.w = world; this.rows = []; }
    tick() { const s = this.w.stats; this.rows.push([this.w.count(), s.gainC, s.gain1, s.gain2, s.leak, s.heat]); }
    summary(kappa) {
      const T = this.rows.length, from = Math.floor(T * 0.75);
      let gain = 0, g1 = 0, g2 = 0, leak = 0, heat = 0, pop = 0, n = 0;
      for (let i = from; i < T; i++) { const r = this.rows[i]; pop += r[0]; gain += r[1] + r[2] + r[3]; g1 += r[2]; g2 += r[3]; leak += r[4]; heat += r[5]; n++; }
      return { pop: pop / n, captureFraction: gain / Math.max(gain + leak, 1e-12), entropyRate: (leak + kappa * heat) / n, share1: g1 / Math.max(gain, 1e-12), share2: g2 / Math.max(gain, 1e-12), t2Reached: this.w.firstUnlock[2] !== null ? 1 : 0 };
    }
  }

  return { World, Recorder, oracle, DEFAULTS, NG, NCH };
});
