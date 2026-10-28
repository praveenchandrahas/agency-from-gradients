(function () {
  "use strict";
  var S = AGSim;
  function $(id) { return document.getElementById(id); }
  var css = getComputedStyle(document.documentElement);
  function tok(n) { return css.getPropertyValue(n).trim(); }
  function rgb(hex) { var h = hex.replace("#", ""); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; }
  var COL = { grass: rgb(tok("--grass")), amber: rgb(tok("--amber")), violet: rgb(tok("--violet")), hunger: rgb(tok("--hunger")), canvas: tok("--canvas"), fg: tok("--fg"), muted: tok("--muted"), line: tok("--line"), accent: tok("--accent") };
  function rgba(c, a) { return "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + a + ")"; }

  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var SPEEDS = [1, 4, 25, 150];
  var SAMPLE = 40, KEEP = 500;

  var state = { rules: { scarcity: true, heredity: true, mortality: true, succession: true }, selection: "persistence", playing: !reduced, speed: reduced ? 0 : 1, skipTarget: 0, skipStart: 0 };
  var world, hist, ema, events, flags, lastNarr = 0, lastUi = 0, narrCache = "";

  function newWorld() {
    var expert = state.selection === "expert";
    var seed = (Math.random() * 2147483647) | 0;
    world = new S.World(Object.assign({}, state.rules, { selection: expert ? "persistence" : state.selection }), seed);
    if (expert) world.policy = S.oracle;
    hist = { pop: [], used: [], dep: [] };
    ema = { c: 0, g1: 0, g2: 0, leak: 0, init: false };
    events = []; flags = { t1: false, t2: false, conv: 0, famine: false, glow: false, invest: false };
    state.skipTarget = 0; $("skipbar").hidden = true;
    renderEvents(); updateUi(true); narrate(true);
  }

  function pushEvent(text) { events.unshift({ day: world.t, text: text }); if (events.length > 6) events.pop(); renderEvents(); }
  function renderEvents() {
    var ol = $("events"); ol.textContent = "";
    events.forEach(function (e) {
      var li = document.createElement("li"), t = document.createElement("time"), s = document.createElement("span");
      t.textContent = "Day " + e.day.toLocaleString(); s.textContent = e.text; li.appendChild(t); li.appendChild(s); ol.appendChild(li);
    });
  }

  function stepOnce() {
    world.step();
    var s = world.stats, a = 1 / 300;
    if (!ema.init) { ema.c = s.gainC; ema.g1 = s.gain1; ema.g2 = s.gain2; ema.leak = s.leak; ema.init = true; }
    else { ema.c += (s.gainC - ema.c) * a; ema.g1 += (s.gain1 - ema.g1) * a; ema.g2 += (s.gain2 - ema.g2) * a; ema.leak += (s.leak - ema.leak) * a; }
    if (world.t % SAMPLE === 0) {
      var m = metrics();
      push(hist.pop, world.count()); push(hist.used, m.used * 100); push(hist.dep, m.dep * 100);
    }
    detect();
  }
  function push(arr, v) { arr.push(v); if (arr.length > KEEP) arr.shift(); }

  function metrics() {
    var gain = ema.c + ema.g1 + ema.g2, tot = gain + ema.leak;
    return { used: tot > 0 ? gain / tot : 0, dep: gain > 0 ? (ema.g1 + ema.g2) / gain : 0, g1: gain > 0 ? ema.g1 / gain : 0, g2: gain > 0 ? ema.g2 / gain : 0, gc: gain > 0 ? ema.c / gain : 1 };
  }

  function instincts() {
    var n = 0, acc = [0, 0, 0, 0, 0], g = world.genome, NG = S.NG, NCH = S.NCH;
    for (var a = 0; a < world.alive.length; a++) {
      if (!world.alive[a]) continue; n++;
      var o = a * NG;
      acc[0] += g[o + 0]; acc[1] += g[o + 5]; acc[2] += g[o + 6]; acc[3] += g[o + 2 * NCH + 1]; acc[4] += g[o + 2 * NCH + 3];
    }
    return n ? acc.map(function (v) { return v / n; }) : acc;
  }

  function detect() {
    var fu = world.firstUnlock;
    if (!flags.t1 && fu[1] !== null) { flags.t1 = true; pushEvent("A creature opened a small deposit for the first time."); }
    if (!flags.t2 && fu[2] !== null) { flags.t2 = true; pushEvent("A big deposit opened fully. Several creatures were investing in it at once."); }
    if (world.converted > flags.conv) { flags.conv = world.converted; if (flags.conv <= 4) pushEvent("A small deposit ran dry and a big one formed in its place."); }
    var pop = world.count();
    if (!flags.famine && world.t > 100 && pop < world.cfg.initPop * 0.55) { flags.famine = true; pushEvent("Famine. The population fell to " + pop + "."); }
    if (flags.famine && pop > world.cfg.initPop * 0.85) flags.famine = false;
    if (pop === 0 && !flags.dead) { flags.dead = true; pushEvent("Everyone died. This world could not support life under these rules."); state.playing = false; syncPlay(); }
  }

  function narrate(force) {
    var now = performance.now();
    if (!force && now - lastNarr < 600) return;
    lastNarr = now;
    var m = metrics(), pop = world.count(), pct = function (x) { return Math.round(x * 100) + "%"; };
    var head, body = "";
    var sel = state.selection;
    if (pop === 0) { head = "Everyone died."; body = "With these rules the creatures could not find enough energy. Press New world to try again."; }
    else if (sel === "expert") {
      head = "These creatures follow rules we wrote by hand.";
      body = "They walk toward food and glow and spend energy to open deposits. " + pct(m.dep) + " of their energy now comes from deposits. Nothing here evolves; this is what success could look like.";
    } else if (world.t < 200) {
      head = "The creatures wander at random.";
      body = "Each one burns energy just to exist and eats whatever grass it bumps into. None of them knows about deposits.";
    } else if (world.t > 8000 && m.dep < 0.02 && (sel === "persistence" || sel === "entropy")) {
      head = "Still ignoring the deposits after " + world.t.toLocaleString() + " days.";
      body = "Survival alone has not led these creatures to open deposits in this world. In some worlds they find them and in others they do not. Check the instinct bars, then press New world to roll another.";
    } else if (m.g2 > 0.12) {
      head = "Big deposits now supply " + pct(m.g2) + " of all energy.";
      body = "Creatures are working together to keep them open. Only about " + pct(m.used) + " of the available sunshine is used, so most of it is still leftover.";
    } else if (m.g1 + m.g2 > 0.06) {
      head = "Some creatures have learned to open deposits.";
      body = pct(m.dep) + " of the energy now comes from deposits instead of grass. Watch the instinct bars: the habit is spreading through inheritance.";
    } else if (flags.famine) {
      head = "Hard times: the population has shrunk a lot.";
      body = "Grass alone cannot feed everyone. Whoever finds extra energy gets to have children.";
    } else if (sel === "drift") {
      head = "Random parents. Having more energy gives no advantage.";
      body = "Children are born at random among the creatures still alive. Starving still weeds out poor foragers, so some instincts improve, but nobody gets extra children for doing well. This is the baseline the other worlds are compared with.";
    } else if (sel === "entropy") {
      head = "Creatures that burn the most energy have children.";
      body = "Using energy is rewarded directly. Check whether that produces better foraging, or only restless creatures.";
    } else {
      head = "The creatures are using " + pct(m.used) + " of the sunshine.";
      body = "They eat grass and have children when they have spare energy. Instincts change slowly, so try Very fast and wait a few thousand days.";
    }
    var key = head + body;
    if (key !== narrCache) { narrCache = key; $("headline").textContent = head; $("body").textContent = body; }
  }

  // ---- drawing -------------------------------------------------------------
  var cv = $("world"), ctx = cv.getContext("2d");
  function fitCanvas() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2), w = Math.round(cv.clientWidth * dpr);
    if (w > 0 && cv.width !== w) { cv.width = w; cv.height = w; }
  }
  function draw() {
    fitCanvas();
    var W = cv.width, L = world.L, cell = W / L, cfg = world.cfg, i, j, k;
    ctx.fillStyle = COL.canvas; ctx.fillRect(0, 0, W, W);
    for (i = 0; i < L; i++) for (j = 0; j < L; j++) {
      var v = world.commons[i * L + j];
      if (v > 0.02) { ctx.fillStyle = rgba(COL.grass, (0.08 + 0.72 * v).toFixed(3)); ctx.fillRect(j * cell, i * cell, cell + 0.6, cell + 0.6); }
    }
    var sites = [];
    for (k = 0; k < L * L; k++) if (world.ttype[k]) sites.push(k);
    sites.forEach(function (c) {
      if (world.stock[c] <= cfg.depletedAt) return;
      var tt = world.ttype[c], col = tt === 1 ? COL.amber : COL.violet, cx = ((c % L) + 0.5) * cell, cy = (Math.floor(c / L) + 0.5) * cell, r = cell * 5.2;
      var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      g.addColorStop(0, rgba(col, 0.22)); g.addColorStop(1, rgba(col, 0));
      ctx.fillStyle = g; ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
    });
    sites.forEach(function (c) {
      var tt = world.ttype[c], col = tt === 1 ? COL.amber : COL.violet, x = c % L, y = Math.floor(c / L), cx = (x + 0.5) * cell, cy = (y + 0.5) * cell;
      var open = world.openness(c), full = Math.min(world.stock[c] / (tt === 1 ? cfg.stock1 : cfg.stock2), 1), dry = world.stock[c] <= cfg.depletedAt;
      ctx.lineWidth = Math.max(1.5, cell * 0.09);
      if (tt === 1) {
        var s = cell * 0.84, x0 = cx - s / 2, y0 = cy - s / 2;
        if (dry) { ctx.setLineDash([3, 3]); ctx.strokeStyle = rgba(COL.amber, 0.35); ctx.strokeRect(x0, y0, s, s); ctx.setLineDash([]); return; }
        ctx.fillStyle = rgba(COL.amber, 0.12 + 0.7 * open * Math.max(full, 0.3)); ctx.fillRect(x0, y0 + s * (1 - open), s, s * open);
        ctx.strokeStyle = rgba(COL.amber, 0.45 + 0.55 * full); ctx.strokeRect(x0, y0, s, s);
      } else {
        var d = cell * 1.5;
        ctx.beginPath(); ctx.moveTo(cx, cy - d); ctx.lineTo(cx + d, cy); ctx.lineTo(cx, cy + d); ctx.lineTo(cx - d, cy); ctx.closePath();
        ctx.fillStyle = rgba(COL.violet, 0.10 + 0.6 * open * Math.max(full, 0.3)); ctx.fill();
        if (open > 0.02) {
          ctx.save(); ctx.clip(); ctx.fillStyle = rgba(COL.violet, 0.35 + 0.4 * open); ctx.fillRect(cx - d, cy + d - 2 * d * open, 2 * d, 2 * d * open); ctx.restore();
        }
        ctx.strokeStyle = rgba(COL.violet, dry ? 0.3 : 0.5 + 0.5 * full); ctx.stroke();
      }
    });
    var E = cfg.reproThresh, hc = COL.hunger, fc = [244, 246, 255];
    for (var a = 0; a < world.alive.length; a++) {
      if (!world.alive[a]) continue;
      var px = (world.y[a] + 0.5) * cell, py = (world.x[a] + 0.5) * cell, t = Math.max(0, Math.min(world.energy[a] / E, 1));
      ctx.fillStyle = "rgb(" + Math.round(hc[0] + (fc[0] - hc[0]) * t) + "," + Math.round(hc[1] + (fc[1] - hc[1]) * t) + "," + Math.round(hc[2] + (fc[2] - hc[2]) * t) + ")";
      ctx.beginPath(); ctx.arc(px, py, cell * 0.27, 0, 6.2832); ctx.fill();
      ctx.lineWidth = 1; ctx.strokeStyle = "rgba(5,8,18,.7)"; ctx.stroke();
      if (world.lastAct[a] === 5) {
        var ct = world.ttype[world.x[a] * L + world.y[a]];
        ctx.beginPath(); ctx.arc(px, py, cell * 0.5, 0, 6.2832);
        ctx.strokeStyle = ct === 2 ? rgba(COL.violet, 0.95) : ct === 1 ? rgba(COL.amber, 0.95) : "rgba(233,237,248,.5)";
        ctx.lineWidth = Math.max(1.5, cell * 0.08); ctx.stroke();
      }
    }
  }

  function chart(id, data, max, unit) {
    var c = $(id), dpr = Math.min(window.devicePixelRatio || 1, 2), w = Math.round(c.clientWidth * dpr), h = Math.round(c.clientHeight * dpr);
    if (!w || !h) return;
    if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
    var g = c.getContext("2d"); g.clearRect(0, 0, w, h);
    var padL = 4 * dpr, padR = 30 * dpr, padT = 6 * dpr, padB = 6 * dpr, pw = w - padL - padR, ph = h - padT - padB;
    g.font = (10 * dpr) + "px " + tok("--mono"); g.textBaseline = "middle"; g.fillStyle = COL.muted; g.strokeStyle = COL.line; g.lineWidth = 1;
    [0, 0.5, 1].forEach(function (f) {
      var y = padT + ph * (1 - f); g.beginPath(); g.moveTo(padL, y); g.lineTo(padL + pw, y); g.stroke();
      g.fillText(String(Math.round(max * f)), padL + pw + 4 * dpr, y);
    });
    if (data.length < 2) return;
    var n = data.length, pts = data.map(function (v, i) { return [padL + pw * (i / (KEEP - 1 > n - 1 ? Math.max(n - 1, 1) : KEEP - 1)), padT + ph * (1 - Math.min(v / max, 1))]; });
    g.beginPath(); pts.forEach(function (p, i) { i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1]); });
    g.strokeStyle = COL.accent; g.lineWidth = 1.8 * dpr; g.stroke();
    g.lineTo(pts[n - 1][0], padT + ph); g.lineTo(pts[0][0], padT + ph); g.closePath(); g.fillStyle = rgba(rgb(tok("--accent")), 0.14); g.fill();
    g.beginPath(); g.arc(pts[n - 1][0], pts[n - 1][1], 3 * dpr, 0, 6.2832); g.fillStyle = COL.accent; g.fill();
  }

  var INST = [["Seeks grass", COL.grass], ["Follows the amber glow", COL.amber], ["Follows the violet glow", COL.violet], ["Opens small deposits", COL.amber], ["Opens big deposits", COL.violet]];
  (function buildInst() {
    var box = $("inst");
    INST.forEach(function (it, i) {
      var l = document.createElement("div"); l.textContent = it[0];
      var tr = document.createElement("div"); tr.className = "track";
      var f = document.createElement("div"); f.className = "fill"; f.id = "inst" + i; f.style.background = rgba(it[1], 0.9); tr.appendChild(f);
      box.appendChild(l); box.appendChild(tr);
    });
  })();

  function updateUi(force) {
    var now = performance.now();
    if (!force && now - lastUi < 150) return;
    lastUi = now;
    var m = metrics(), pop = world.count();
    $("day").textContent = "Day " + world.t.toLocaleString() + "  ·  " + pop + " creatures";
    var usedP = Math.round(m.used * 100);
    $("bUsed").style.width = usedP + "%"; $("bWaste").style.width = (100 - usedP) + "%";
    $("usedTxt").textContent = usedP + "% used, " + (100 - usedP) + "% wasted";
    $("sGrass").style.width = Math.round(m.gc * 100) + "%"; $("sAmber").style.width = Math.round(m.g1 * 100) + "%"; $("sViolet").style.width = Math.round(m.g2 * 100) + "%";
    $("srcTxt").textContent = "grass " + Math.round(m.gc * 100) + "% · small " + Math.round(m.g1 * 100) + "% · big " + Math.round(m.g2 * 100) + "%";
    chart("chPop", hist.pop, world.cfg.maxPop); chart("chUsed", hist.used, 100); chart("chDep", hist.dep, 100);
    var ex = state.selection === "expert", ins = instincts();
    INST.forEach(function (it, i) {
      var f = $("inst" + i), v = ex ? 0 : Math.max(-1.5, Math.min(1.5, ins[i])) / 1.5;
      f.style.left = v >= 0 ? "50%" : (50 + v * 50) + "%"; f.style.width = Math.abs(v) * 50 + "%";
    });
    $("instNote").textContent = ex ? "The hand-coded forager has fixed rules, so there are no instincts to evolve." : "At the start these hover around zero because every creature is random. A bar to the right means creatures are drawn toward it, to the left means they avoid it.";
    var sk = $("skipfill"); if (state.skipTarget) sk.style.width = Math.min(100, 100 * (world.t - state.skipStart) / (state.skipTarget - state.skipStart)) + "%";
    narrate(false);
  }

  // ---- loop ----------------------------------------------------------------
  function frame() {
    if (state.playing) {
      var skipping = state.skipTarget > 0, budget = skipping ? 28 : 11, want = skipping ? 1e9 : SPEEDS[state.speed], t0 = performance.now(), n = 0;
      while (n < want) {
        stepOnce(); n++;
        if (skipping && world.t >= state.skipTarget) { state.skipTarget = 0; $("skipbar").hidden = true; break; }
        if ((n & 7) === 0 && performance.now() - t0 > budget) break;
        if (!state.playing) break;
      }
    }
    draw(); updateUi(false);
    requestAnimationFrame(frame);
  }

  // ---- controls ------------------------------------------------------------
  function syncPlay() { var b = $("play"); b.textContent = state.playing ? "Pause" : "Play"; b.setAttribute("aria-pressed", String(state.playing)); }
  $("play").addEventListener("click", function () { state.playing = !state.playing; syncPlay(); });
  document.querySelectorAll('input[name="speed"]').forEach(function (r) { r.addEventListener("change", function () { state.speed = +r.value; }); });
  $("skip").addEventListener("click", function () { state.skipStart = world.t; state.skipTarget = world.t + 5000; $("skipbar").hidden = false; $("skipfill").style.width = "0"; state.playing = true; syncPlay(); });
  $("restart").addEventListener("click", function () { newWorld(); });
  document.addEventListener("keydown", function (e) { if (e.code === "Space" && !/BUTTON|INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) { e.preventDefault(); $("play").click(); } });
  function readRules() {
    ["scarcity", "heredity", "mortality", "succession"].forEach(function (k) { state.rules[k] = $("r-" + k).checked; });
    var r = document.querySelector('input[name="sel"]:checked'); state.selection = r ? r.value : "persistence";
  }
  function writeRules() {
    ["scarcity", "heredity", "mortality", "succession"].forEach(function (k) { $("r-" + k).checked = state.rules[k]; });
    $("s-" + state.selection).checked = true;
  }
  document.querySelectorAll('.rule input').forEach(function (el) { el.addEventListener("change", function () { readRules(); newWorld(); state.playing = true; syncPlay(); }); });
  var PRESETS = {
    natural: { rules: {}, sel: "persistence" }, drift: { rules: {}, sel: "drift" }, entropy: { rules: {}, sel: "entropy" }, expert: { rules: {}, sel: "expert" },
    noheredity: { rules: { heredity: false }, sel: "persistence" }, plenty: { rules: { scarcity: false }, sel: "persistence" }
  };
  document.querySelectorAll(".preset").forEach(function (b) {
    b.addEventListener("click", function () {
      var p = PRESETS[b.dataset.preset];
      state.rules = Object.assign({ scarcity: true, heredity: true, mortality: true, succession: true }, p.rules); state.selection = p.sel;
      writeRules(); newWorld(); state.playing = true; state.speed = 2; syncPlay();
      document.getElementById("sp2").checked = true;
      cv.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "nearest" });
    });
  });
  cv.addEventListener("pointermove", function (e) {
    var r = cv.getBoundingClientRect(), L = world.L, y = Math.floor((e.clientX - r.left) / r.width * L), x = Math.floor((e.clientY - r.top) / r.height * L);
    if (x < 0 || y < 0 || x >= L || y >= L) return;
    var c = x * L + y, parts = ["Grass " + Math.round(world.commons[c] * 100) + "%"], tt = world.ttype[c], n = 0, es = 0;
    if (tt) parts.push((tt === 1 ? "Small" : "Big") + " deposit: " + (world.stock[c] <= world.cfg.depletedAt ? "used up" : Math.round(world.openness(c) * 100) + "% open, " + Math.round(world.stock[c]) + " energy left"));
    for (var a = 0; a < world.alive.length; a++) if (world.alive[a] && world.x[a] === x && world.y[a] === y) { n++; es += world.energy[a]; }
    if (n) parts.push(n + " creature" + (n > 1 ? "s" : "") + ", average energy " + (es / n).toFixed(1));
    $("inspect").textContent = parts.join("  ·  ");
  });
  cv.addEventListener("pointerleave", function () { $("inspect").textContent = "Hover over the world to inspect a square."; });

  // Open directly on a preset via #natural, #drift, ...  (plain hash names only)
  syncPlay(); writeRules(); newWorld();
  var h = (location.hash || "").slice(1);
  if (PRESETS[h]) { var b = document.querySelector('.preset[data-preset="' + h + '"]'); if (b) b.click(); }
  // Warm start: skip ahead a little so the first screen already shows structure.
  window.__ag = { world: function () { return world; }, state: state };
  requestAnimationFrame(frame);
})();
