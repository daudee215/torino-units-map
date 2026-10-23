/* Public-source screening. Monthly net balance is not simultaneous self-consumption. */
(function(root){
  "use strict";
  const finite=(x,name,min=0,max=Infinity)=>{if(typeof x!=="number"||!Number.isFinite(x)||x<min||x>max)throw Error(`Invalid ${name}`);return x;};
  function calculate(input,cohort,solar){
    const households=input.households===null?null:finite(input.households,"households");
    const roof=input.roofM2===null?null:finite(input.roofM2,"roof area");
    const usable=finite(input.usableShare,"usable share",0,1);
    const density=finite(input.density,"panel density",0,0.5);
    const sensitivity=finite(input.demandSensitivity,"demand sensitivity",0,1);
    const roofSensitivity=finite(input.roofSensitivity,"roof sensitivity",0,1);
    const share=input.pvShare===null?null:finite(input.pvShare,"PV share",0,1);
    const capacity=roof===null?null:roof*usable*density;
    const assignedCapacity=capacity===null||share===null?null:capacity*share;
    if(cohort.monthly.length!==12||solar.length!==12)throw Error("Twelve monthly source rows required");
    const monthly=cohort.monthly.map((m,i)=>{
      if(m.month!==i+1||solar[i].month!==i+1)throw Error("Missing/duplicate source month");
      const kwh=finite(m.kwh,"monthly demand");
      const yieldKwh=finite(solar[i].kwh_per_kwp,"monthly solar yield");
      const demand=households===null?null:households*kwh;
      const generation=assignedCapacity===null?null:assignedCapacity*yieldKwh;
      return {month:i+1,demand_kwh:demand,demand_low_kwh:demand===null?null:demand*(1-sensitivity),demand_high_kwh:demand===null?null:demand*(1+sensitivity),
        generation_kwh:generation,
        generation_low_kwh:roof===null||share===null?null:roof*Math.max(0,usable-roofSensitivity)*density*share*yieldKwh,
        generation_high_kwh:roof===null||share===null?null:roof*Math.min(1,usable+roofSensitivity)*density*share*yieldKwh,
        net_kwh:demand===null||generation===null?null:generation-demand};
    });
    const total=k=>monthly.some(m=>m[k]===null)?null:monthly.reduce((s,m)=>s+m[k],0);
    const annual=Object.fromEntries(Object.keys(monthly[0]).filter(k=>k!=="month").map(k=>[k,total(k)]));
    annual.generation_to_demand_ratio=annual.demand_kwh>0&&annual.generation_kwh!==null?annual.generation_kwh/annual.demand_kwh:null;
    annual.ratio_low=annual.demand_high_kwh>0&&annual.generation_low_kwh!==null?annual.generation_low_kwh/annual.demand_high_kwh:null;
    annual.ratio_high=annual.demand_low_kwh>0&&annual.generation_high_kwh!==null?annual.generation_high_kwh/annual.demand_low_kwh:null;
    return {capacity_kwp:capacity,assigned_capacity_kwp:assignedCapacity,monthly,annual,kind:"public_screening_scenario",interval_kind:"user_defined_sensitivity_not_confidence_interval",self_consumption_kwh:null};
  }
  const api={calculate};if(typeof module!=="undefined"&&module.exports)module.exports=api;else root.PublicEnergyModel=api;
})(typeof window==="undefined"?globalThis:window);
