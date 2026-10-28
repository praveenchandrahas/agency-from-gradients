(function () {
  "use strict";
  var S = AGSim;
  function $(id) { return document.getElementById(id); }
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var DPR = Math.min(window.devicePixelRatio || 1, 2);

  /* ------------------------------------------------------------------ waterfall (illustration) */
  (function () {
    var cv = $("fall"), ctx = cv.getContext("2d"), W = cv.width, H = cv.height;
    var slider = $("catch"), big = $("usedbig");
    var drops = [], used = 0, wasted = 0, last = 0, acc = 0;
    var pools = [{ x: 150, y: 150, w: 170, label: "Grass: everyday energy" }, { x: 430, y: 255, w: 170, label: "Small wells" }, { x: 710, y: 340, w: 170, label: "Big wells" }];
    function p() { return slider.value / 100; }
    function spawn() { drops.push({ x: pools[0].x + (Math.random() - .5) * 120, y: -10, vy: 1.2 + Math.random() * .6, stage: 0, state: "fall", life: 1, tx: 0 }); }
    function frame(t) {
      var dt = Math.min((t - last) / 16.7, 3); last = t;
      acc += dt * (reduced ? 0 : 0.28); while (acc >= 1) { spawn(); acc -= 1; }
      ctx.clearRect(0, 0, W, H);
      var g = ctx.createRadialGradient(150, -40, 10, 150, -40, 360); g.addColorStop(0, "rgba(255,217,168,.55)"); g.addColorStop(1, "rgba(255,217,168,0)");
      ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#ffd9a8"; ctx.beginPath(); ctx.arc(150, -4, 26, 0, 7); ctx.fill();
      ctx.font = "600 15px ui-sans-serif,system-ui,sans-serif"; ctx.textAlign = "center";
      pools.forEach(function (pl, i) {
        ctx.fillStyle = "#12384a"; ctx.strokeStyle = "#2c6479"; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.roundRect(pl.x - pl.w / 2, pl.y, pl.w, 46, 10); ctx.fill(); ctx.stroke();
        ctx.fillStyle = "#a9c3c4"; ctx.fillText(pl.label, pl.x, pl.y + 72);
        var mills = Math.round(p() * 4); // little mills along the rim
        for (var m = 0; m < mills; m++) {
          var mx = pl.x - pl.w / 2 + 22 + m * ((pl.w - 44) / 3);
          ctx.strokeStyle = "#7bd88f"; ctx.lineWidth = 2.5; var a = t / 400 + m;
          ctx.beginPath(); ctx.arc(mx, pl.y + 8, 11, 0, 7); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(mx - 11 * Math.cos(a), pl.y + 8 - 11 * Math.sin(a)); ctx.lineTo(mx + 11 * Math.cos(a), pl.y + 8 + 11 * Math.sin(a)); ctx.stroke();
        }
      });
      ctx.fillStyle = "#04101a"; ctx.fillRect(0, H - 34, W, 34); ctx.fillStyle = "#6f8d93"; ctx.fillText("Lost into empty space", W / 2, H - 12);
      for (var i = drops.length - 1; i >= 0; i--) {
        var d = drops[i];
        if (d.state === "fall") {
          d.y += d.vy * dt * 2.4;
          var pl = pools[d.stage];
          if (d.y >= pl.y && d.stage < 3) {
            if (Math.random() < p()) { d.state = "used"; d.life = 1; used++; }
            else if (d.stage === 2) { d.state = "gone"; wasted++; }
            else { d.stage++; d.x = pools[d.stage].x + (Math.random() - .5) * 120; d.y = pools[d.stage].y - 90; d.vy = 1.4; }
          }
          ctx.fillStyle = "rgba(255,217,168,.95)"; ctx.beginPath(); ctx.arc(d.x, d.y, 3.2, 0, 7); ctx.fill();
        } else if (d.state === "used") {
          d.life -= 0.02 * dt; var pl2 = pools[d.stage];
          ctx.fillStyle = "rgba(123,216,143," + Math.max(d.life, 0) + ")"; ctx.beginPath(); ctx.arc(d.x, pl2.y + 4 - (1 - d.life) * 26, 3.6, 0, 7); ctx.fill();
          if (d.life <= 0) drops.splice(i, 1);
        } else {
          d.y += 3 * dt; d.x += 1.2 * dt;
          ctx.fillStyle = "rgba(255,138,92,.8)"; ctx.beginPath(); ctx.arc(d.x, d.y, 2.6, 0, 7); ctx.fill();
          if (d.y > H) drops.splice(i, 1);
        }
      }
      var tot = used + wasted; big.textContent = tot > 20 ? Math.round(100 * used / tot) + "% used" : "…";
      if (tot > 400) { used *= 0.5; wasted *= 0.5; }
      requestAnimationFrame(frame);
    }
    slider.addEventListener("input", function () { used = wasted = 0; });
    if (reduced) { for (var k = 0; k < 40; k++) spawn(); }
    requestAnimationFrame(frame);
  })();

  /* ------------------------------------------------------------------ the pond */
  var cv = $("pond"), ctx = cv.getContext("2d");
  var L = 32, state = { playing: !reduced, speed: 1, preset: "natural" };
  var SPEEDS = [3, 9, 40, 220];
  var world, prev, cur, born, ghosts, embers, rings, acc = 0, stepAge = 0, animT = 0;
  var ema, hist, flags;

  function px(cells) { return cells * (cv.width / L); }

  function newPond() {
    var seed = (Math.random() * 2147483647) | 0, ps = state.preset;
    world = new S.World({ selection: ps === "drift" ? "drift" : "persistence" }, seed);
    if (ps === "expert") world.policy = S.oracle;
    var M = world.alive.length;
    prev = { x: new Float32Array(M), y: new Float32Array(M) };
    cur = { x: new Float32Array(M), y: new Float32Array(M) };
    born = new Float32Array(M); ghosts = []; embers = []; rings = [];
    for (var a = 0; a < M; a++) { cur.x[a] = prev.x[a] = world.x[a]; cur.y[a] = prev.y[a] = world.y[a]; }
    ema = { c: 0, g1: 0, g2: 0, leak: 0, init: false }; flags = { t1: false, t2: false };
    acc = 0; stepAge = 0;
    render(0); ui(true);
  }

  function snapshot(aliveBefore) {
    var M = world.alive.length;
    for (var a = 0; a < M; a++) {
      var was = aliveBefore[a], is = world.alive[a];
      if (is && !was) { prev.x[a] = cur.x[a] = world.x[a]; prev.y[a] = cur.y[a] = world.y[a]; born[a] = 1; rings.push({ x: world.x[a], y: world.y[a], t: 0 }); }
      else if (!is && was) ghosts.push({ x: cur.x[a], y: cur.y[a], h: hue(a), t: 0 });
      else if (is) { prev.x[a] = cur.x[a]; prev.y[a] = cur.y[a]; cur.x[a] = world.x[a]; cur.y[a] = world.y[a]; }
    }
  }
  var HUES = [8, 330, 200, 28, 285, 350, 215, 48];
  function hue(a) { return HUES[world.lineage[a] % HUES.length]; }

  function stepOnce(tween) {
    var before = tween ? world.alive.slice() : null;
    world.step();
    var s = world.stats, al = 1 / 300;
    if (!ema.init) { ema.c = s.gainC; ema.g1 = s.gain1; ema.g2 = s.gain2; ema.leak = s.leak; ema.init = true; }
    else { ema.c += (s.gainC - ema.c) * al; ema.g1 += (s.gain1 - ema.g1) * al; ema.g2 += (s.gain2 - ema.g2) * al; ema.leak += (s.leak - ema.leak) * al; }
    if (tween) {
      snapshot(before);
      var n = Math.min(6, Math.round(s.leak * 0.35));
      for (var k = 0; k < n && embers.length < 260; k++) embers.push({ x: Math.random() * L, y: Math.random() * L, t: 0, v: .4 + Math.random() * .8 });
    } else {
      var M = world.alive.length;
      for (var a = 0; a < M; a++) { cur.x[a] = prev.x[a] = world.x[a]; cur.y[a] = prev.y[a] = world.y[a]; }
    }
  }

  function hash(i, k) { var h = Math.imul(i * 7919 + k * 104729 + 13, 2654435761); h ^= h >>> 15; return ((h >>> 0) % 10000) / 10000; }

  function render(dt) {
    var W = cv.width, cs = W / L; animT += dt;
    ctx.clearRect(0, 0, W, W);
    // soft water
    var g = ctx.createRadialGradient(W * .5, W * .1, W * .05, W * .5, W * .5, W * .85);
    g.addColorStop(0, "#10394a"); g.addColorStop(.6, "#08202c"); g.addColorStop(1, "#04111a");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, W);
    // grass motes
    var com = world.commons, tt = animT;
    for (var i = 0; i < L * L; i++) {
      var c = com[i]; if (c < 0.05) continue;
      var n = Math.min(5, Math.ceil(c * 5)), cx = Math.floor(i / L), cy = i % L;
      for (var k = 0; k < n; k++) {
        var ox = hash(i, k * 2), oy = hash(i, k * 2 + 1), ph = hash(i, k + 99) * 6.28;
        var x = (cy + ox + Math.sin(tt * .7 + ph) * .12) * cs, y = (cx + oy + Math.cos(tt * .6 + ph) * .12) * cs;
        var tw = .55 + .45 * Math.sin(tt * 1.6 + ph);
        ctx.fillStyle = "rgba(155,229,138," + (0.28 + 0.5 * c * tw) + ")";
        ctx.beginPath(); ctx.arc(x, y, cs * (.045 + .03 * c), 0, 6.3); ctx.fill();
      }
    }
    // wells
    for (var j = 0; j < L * L; j++) {
      var ty = world.ttype[j]; if (!ty) continue;
      var live = world.stock[j] > world.cfg.depletedAt; if (!live) continue;
      var op = world.openness(j), wx = (j % L + .5) * cs, wy = (Math.floor(j / L) + .5) * cs;
      var col = ty === 1 ? [242, 180, 90] : [169, 139, 255], r = cs * (ty === 1 ? .62 : 1.05);
      var glow = ctx.createRadialGradient(wx, wy, r * .2, wx, wy, r * (1.9 + op));
      glow.addColorStop(0, "rgba(" + col + "," + (.12 + .45 * op) + ")"); glow.addColorStop(1, "rgba(" + col + ",0)");
      ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(wx, wy, r * (1.9 + op), 0, 6.3); ctx.fill();
      ctx.strokeStyle = "rgba(" + col + "," + (.6 + .4 * op) + ")"; ctx.lineWidth = Math.max(1.5, cs * .08);
      ctx.setLineDash(op < .98 ? [cs * .22, cs * .18] : []); ctx.lineDashOffset = -tt * 6;
      ctx.beginPath(); ctx.arc(wx, wy, r, 0, 6.3); ctx.stroke(); ctx.setLineDash([]);
      if (op > .3) { // rising bubbles when open
        for (var b = 0; b < 3; b++) { var bp = (tt * .5 + b / 3 + hash(j, b)) % 1; ctx.fillStyle = "rgba(" + col + "," + (1 - bp) * .7 + ")"; ctx.beginPath(); ctx.arc(wx + (hash(j, b + 5) - .5) * r, wy - bp * r * 1.4, cs * .05, 0, 6.3); ctx.fill(); }
      }
    }
    // embers (wasted energy)
    for (var e = embers.length - 1; e >= 0; e--) {
      var em = embers[e]; em.t += dt * .5; if (em.t > 1) { embers.splice(e, 1); continue; }
      ctx.fillStyle = "rgba(255,138,92," + (.6 * (1 - em.t)) + ")";
      ctx.beginPath(); ctx.arc(em.x * cs + Math.sin(em.t * 5 + em.v) * cs * .2, (em.y - em.t * em.v * 5) * cs, cs * .05, 0, 6.3); ctx.fill();
    }
    // creatures
    var M = world.alive.length, f = state.speed >= 2 ? 1 : Math.min(stepAge, 1);
    for (var a = 0; a < M; a++) {
      if (!world.alive[a]) continue;
      var dx = cur.x[a] - prev.x[a], dy = cur.y[a] - prev.y[a];
      if (dx > L / 2) dx -= L; else if (dx < -L / 2) dx += L; if (dy > L / 2) dy -= L; else if (dy < -L / 2) dy += L;
      var X = ((prev.y[a] + dy * f) % L + L) % L, Y = ((prev.x[a] + dx * f) % L + L) % L;
      var en = Math.max(0, Math.min(world.energy[a] / world.cfg.reproThresh, 1.3)), rad = cs * (.2 + .2 * en);
      var h = hue(a), sx = (X + .5) * cs, sy = (Y + .5) * cs;
      var gl = ctx.createRadialGradient(sx, sy, 0, sx, sy, rad * 3);
      gl.addColorStop(0, "hsla(" + h + ",85%,68%," + (.25 + .35 * Math.min(en, 1)) + ")"); gl.addColorStop(1, "hsla(" + h + ",85%,68%,0)");
      ctx.fillStyle = gl; ctx.beginPath(); ctx.arc(sx, sy, rad * 3, 0, 6.3); ctx.fill();
      ctx.fillStyle = "hsl(" + h + ",80%," + (45 + 25 * Math.min(en, 1)) + "%)"; ctx.beginPath(); ctx.arc(sx, sy, rad, 0, 6.3); ctx.fill();
      if (world.lastAct && world.lastAct[a] === 5) { ctx.strokeStyle = "rgba(255,255,255,.8)"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(sx, sy, rad * 1.7, 0, 6.3); ctx.stroke(); }
    }
    // births and deaths
    for (var r2 = rings.length - 1; r2 >= 0; r2--) { var rg = rings[r2]; rg.t += dt * 1.6; if (rg.t > 1) { rings.splice(r2, 1); continue; } ctx.strokeStyle = "rgba(255,255,255," + (.7 * (1 - rg.t)) + ")"; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc((rg.y + .5) * cs, (rg.x + .5) * cs, cs * (.3 + rg.t * .8), 0, 6.3); ctx.stroke(); }
    for (var q = ghosts.length - 1; q >= 0; q--) { var gh = ghosts[q]; gh.t += dt * 1.2; if (gh.t > 1) { ghosts.splice(q, 1); continue; } ctx.fillStyle = "hsla(" + gh.h + ",20%,60%," + (.4 * (1 - gh.t)) + ")"; ctx.beginPath(); ctx.arc((gh.y + .5) * cs, (gh.x + .5) * cs, cs * .2 * (1 + gh.t), 0, 6.3); ctx.fill(); }
  }

  /* panel */
  function metrics() {
    var gain = ema.c + ema.g1 + ema.g2, tot = gain + ema.leak;
    return { used: tot > 0 ? gain / tot : 0, g1: gain > 0 ? ema.g1 / gain : 0, g2: gain > 0 ? ema.g2 / gain : 0 };
  }
  var lastUi = 0, headCache = "";
  function ui(force) {
    var now = performance.now(); if (!force && now - lastUi < 250) return; lastUi = now;
    var m = metrics(), pop = world.count(), fams = {};
    for (var a = 0; a < world.alive.length; a++) if (world.alive[a]) fams[world.lineage[a]] = 1;
    var nf = Object.keys(fams).length, t = world.t, dep = m.g1 + m.g2;
    $("day").textContent = "Day " + t.toLocaleString();
    $("usedtxt").textContent = Math.round(m.used * 100) + "% used · " + Math.round((1 - m.used) * 100) + "% wasted";
    $("b-used").style.width = (m.used * 100) + "%";
    $("srctxt").textContent = "grass " + Math.round((1 - dep) * 100) + "% · small " + Math.round(m.g1 * 100) + "% · big " + Math.round(m.g2 * 100) + "%";
    $("b-grass").style.width = ((1 - dep) * 100) + "%"; $("b-small").style.width = (m.g1 * 100) + "%"; $("b-big").style.width = (m.g2 * 100) + "%";
    $("poptxt").textContent = pop + " of 200"; $("b-pop").style.width = (pop / 2) + "%";
    $("fam").textContent = state.preset === "expert" ? "Everyone follows the same hand-written rules." : (nf + (nf === 1 ? " family" : " families") + " still alive. Colours are founding families.");
    var h, s;
    if (pop === 0) { h = "Everyone died."; s = "This pond could not support life."; }
    else if (state.preset === "expert") { h = "These creatures follow rules we wrote by hand."; s = "They head for food and wells and pay energy to open them. Nothing here evolves: it shows what success could look like. " + Math.round(dep * 100) + "% of their energy comes from wells."; }
    else if (state.preset === "drift") { h = "Parents are chosen at random."; s = "Having more energy gives no advantage in having children, so this is the comparison pond. Starvation still removes some creatures."; }
    else if (t < 200) { h = "Creatures wander at random."; s = "Each burns energy just to exist and eats grass it bumps into. Press Very fast and give them time."; }
    else if (dep < 0.02 && t > 4000) { h = "They graze, but ignore the wells."; s = "Families with better grazing instincts won out. After " + t.toLocaleString() + " days, almost none of their energy comes from the wells."; }
    else if (dep >= 0.08) { h = "Some families learned to open wells."; s = Math.round(dep * 100) + "% of the energy now comes from wells instead of grass. The habit spreads through inheritance."; }
    else { h = "Slowly, they are getting better at finding food."; s = "Parents with spare energy have children, who inherit their instincts with small random changes."; }
    if (h !== headCache) { $("head").textContent = h; headCache = h; } $("sub").textContent = s;
  }

  /* loop */
  var lastT = 0;
  function loop(t) {
    var dt = Math.min((t - lastT) / 1000, .1); lastT = t;
    if (state.playing && world) {
      var sps = SPEEDS[state.speed]; acc += dt * sps; var n = 0;
      while (acc >= 1 && n < 260) { stepOnce(state.speed < 2); acc -= 1; n++; stepAge = 0; }
      if (n >= 260) acc = 0; stepAge = acc;
      if (state.speed >= 2) { stepAge = 1; }
      render(dt); ui(false);
    } else if (world) { render(0); }
    requestAnimationFrame(loop);
  }

  function size() { var w = cv.clientWidth || 600; cv.width = Math.round(w * DPR); cv.height = Math.round(w * DPR); if (world) render(0); }
  window.addEventListener("resize", size);
  $("play").addEventListener("click", function () { state.playing = !state.playing; this.textContent = state.playing ? "Pause" : "Play"; this.classList.toggle("on", state.playing); });
  document.querySelectorAll(".seg button").forEach(function (b) { b.addEventListener("click", function () { state.speed = +b.dataset.sp; document.querySelectorAll(".seg button").forEach(function (x) { x.classList.toggle("on", x === b); }); }); });
  $("preset").addEventListener("change", function () { state.preset = this.value; newPond(); });
  $("again").addEventListener("click", newPond);
  if (reduced) { $("play").textContent = "Play"; $("play").classList.remove("on"); }
  size(); newPond(); requestAnimationFrame(loop);
  window.__pond = { world: function () { return world; }, state: state, newPond: newPond, step: function (n) { for (var i = 0; i < n; i++) stepOnce(false); render(0); ui(true); } };

  /* ------------------------------------------------------------------ what-if explorer (real S2 results) */
  // t2_reached out of 30 seeds, keyed scarcity,heredity,mortality,succession (1 = condition ON). docs/results/s2_report.md
  var T2 = { "0000": .933, "0001": .900, "0010": .900, "0011": .867, "0100": .867, "0101": .867, "0110": .433, "0111": .533,
             "1000": .733, "1001": .867, "1010": 1.0, "1011": 1.0, "1100": .633, "1101": .800, "1110": .367, "1111": .267 };
  var dots = $("dots"); for (var d = 0; d < 30; d++) dots.appendChild(document.createElement("i"));
  function explorer() {
    var key = ["t-scar", "t-her", "t-mor", "t-suc"].map(function (id) { return $(id).checked ? "1" : "0"; }).join("");
    var k = Math.round(T2[key] * 30);
    Array.prototype.forEach.call(dots.children, function (el, i) { el.classList.toggle("hit", i < k); });
    $("dotsbig").textContent = k + " of 30 ponds";
    var all = key === "1111";
    $("dotsnote").textContent = all ? "With everything switched on, as in the original thesis: the lowest score on the board." : (k > 8 ? "Switching things off made the big wells easier to find, not harder." : "");
  }
  ["t-scar", "t-her", "t-mor", "t-suc"].forEach(function (id) { $(id).addEventListener("change", explorer); });
  explorer();
})();
