/* Explicit screening assumptions; no measured consumption or production is inferred. */
(function (root) {
  "use strict";
  const defaults = { householdKwh: 2000, roofShare: 0.45, density: 0.2, yieldKwh: 1100, heatIntensity: 150, savingShare: 0.35 };
  function calculate(input, assumptions = defaults) {
    const a = { ...defaults, ...assumptions };
    for (const k of Object.keys(defaults)) if (!Number.isFinite(a[k]) || a[k] < 0) throw new Error(`Invalid assumption: ${k}`);
    if (a.roofShare > 1 || a.savingShare > 1) throw new Error("Shares must be between 0 and 1");
    const households = Math.max(0, Number(input.households) || 0);
    const roof = Math.max(0, Number(input.roof) || 0);
    const floorArea = Math.max(0, Number(input.floorArea) || 0);
    const demand = households * a.householdKwh;
    const usableRoof = roof * a.roofShare;
    const capacity = usableRoof * a.density;
    const production = capacity * a.yieldKwh;
    const heat = floorArea * a.heatIntensity;
    return { households, roof, floorArea, usableRoof, capacity, production, demand, heat,
      heatSaved: heat * a.savingShare, heatAfter: heat * (1 - a.savingShare),
      annualRatio: demand > 0 ? production / demand : null,
      annualBalance: production - demand };
  }
  const api = { defaults, calculate };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.EnergyModel = api;
})(typeof window === "undefined" ? globalThis : window);
