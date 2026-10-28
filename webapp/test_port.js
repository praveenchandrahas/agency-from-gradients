// Sanity checks for the JS port (run with: node webapp/test_port.js).
// Statistical, not bit-exact: the Python engine is the reference.
const assert = require("assert");
const { World, Recorder, oracle } = require("./sim.js");

function summarise(opts, seeds, steps, pol) {
  const out = [];
  for (let s = 0; s < seeds; s++) {
    const w = new World(opts, 1000 + s); if (pol) w.policy = pol;
    const r = new Recorder(w);
    for (let i = 0; i < steps; i++) { w.step(); r.tick(); }
    out.push(r.summary(w.cfg.kappa));
  }
  const m = (k) => out.reduce((a, o) => a + o[k], 0) / out.length;
  return { ent: m("entropyRate"), t2: m("t2Reached"), pop: m("pop") };
}
const drift = summarise({ selection: "drift" }, 3, 6000);
const orc = summarise({}, 3, 6000, oracle);
assert(orc.ent > drift.ent, "hand-coded forager should out-produce neutral drift");
assert(orc.t2 === 1, "hand-coded forager should reach tier 2");
const noMort = new World({ mortality: false }, 5);
for (let i = 0; i < 500; i++) noMort.step();
assert(noMort.cum.deaths === 0, "mortality off => no deaths");
const abundant = summarise({ scarcity: false, selection: "drift" }, 2, 3000);
assert(abundant.pop >= drift.pop, "abundance should not reduce population");
console.log("port sanity checks passed", { drift, orc });
