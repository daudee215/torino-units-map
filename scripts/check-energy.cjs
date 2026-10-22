const assert = require('node:assert/strict');
const { calculate, defaults } = require('../energy-model.js');
const c = calculate({ households: 10, roof: 100, floorArea: 500 }, { ...defaults, householdKwh: 1600, roofShare: .5, density: .2, yieldKwh: 1300 });
assert.equal(c.demand, 16000);
assert.equal(c.capacity, 10);
assert.equal(c.production, 13000);
assert.equal(c.annualRatio, .8125);
assert.equal(c.heatAfter + c.heatSaved, c.heat);
assert.equal(calculate({ households: 0, roof: 100 }).annualRatio, null);
assert.equal(calculate({ households: 1, roof: 0 }).production, 0);
assert.throws(() => calculate({}, { roofShare: 1.1 }));
assert.throws(() => calculate({}, { householdKwh: NaN }));
const census = require('../data/census2023.json');
assert.equal(Object.keys(census.buildings).length, 5080);
assert.equal(Object.values(census.audit.allocation_status).reduce((a,b)=>a+b,0), 5080);
for (const r of Object.values(census.buildings)) {
  if (r.status !== 'allocated_2023') assert.equal(r.dwellings, null);
  else { assert.ok(r.dwellings >= 0); assert.ok(r.households >= 0); }
}
const demand = require('../data/demand_benchmark.json');
assert.equal(demand.monthly.length, 12);
assert.ok(Math.abs(demand.monthly.reduce((s,r)=>s+r.kwh,0)-demand.annual_sum_monthly_kwh)<1e-8);
const ape = require('../data/ape_units.json');
assert.equal(ape.certificates[0].standard_electricity_kwh_year, null);
assert.equal(ape.certificates[1].scope, 'unit_multi_subalterno');
assert.equal(ape.certificates[1].attestation_object, 'unit');
assert.deepEqual(ape.certificates[1].subalterni, ['8','9']);
console.log('Energy units, source totals, null handling and group-record checks passed.');
