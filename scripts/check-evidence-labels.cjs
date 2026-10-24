/* Real UI modules against the curated source cases; no DOM or API state is mocked. */
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
(async()=>{
 const box={window:{},document:{documentElement:{lang:'en'}},fetch:async name=>{assert(name.startsWith('data/property-evidence/cases.json'));return new Response(await fs.readFile(path.join(root,name.split('?')[0])));},Response};vm.createContext(box);
 for(const name of ['evidence-labels.js','property-evidence-cases.js']){vm.runInContext(await fs.readFile(path.join(root,name),'utf8'),box);if(name==='evidence-labels.js')box.EvidenceLabels=box.window.EvidenceLabels;}
 const labels=box.window.EvidenceLabels,cases=box.window.PropertyEvidenceCases;
 assert(labels.method('source_id_uins').includes('Reported by source'));assert(!labels.method('source_id_uins').includes('Geometric candidate'));assert(labels.method('parcel_overlap_fraction').includes('Geometric candidate'));assert(labels.entrance({status:'unknown'}).includes('Unknown'));
 let html=await cases.detail('san-francesco-38g-2026');assert(html.includes('1306 / 93 / 45')&&html.includes('civic:98478')&&html.includes('civic:68681'));assert(!html.includes('civic:68682'));assert(html.includes('#page=3')&&html.includes('#page=4')&&html.includes('Current access'));
 const data=await cases.data(),roma=data.cases.find(c=>c.id==='roma-1282-94-40-address-control');assert(roma.property_matches.length>0);
 html=await cases.context({kind:'property',id:roma.property_matches[0].id},'1282/94');assert(html.includes(roma.id));html=await cases.context({kind:'property',id:'property:not-acquired'},'1282/94');assert(!html.includes(roma.id));
 html=await cases.context({kind:'entrance',id:'civic:68681'},null);assert(html.includes('san-francesco-38g-2026'));
 html=await cases.detail('repubblica-31-market-2023');assert(html.includes('Excluded from the described scope')&&html.includes('1217 / 163 / 4'));
 box.document.documentElement.lang='it';assert(labels.badge('document_observation').includes('Descritto nel documento'));html=await cases.detail('san-francesco-38g-2026');assert(html.includes('Percorso secondario sul cortile')&&html.includes('Accesso attuale'));
 assert((await cases.list()).includes('11')&&(await cases.list()).includes('2'));
 console.log('Evidence UI verified: bilingual types, declared site keys versus geometric candidates, scoped documentary matches, exact civic letter, two access roles, exclusion and unknowns.');
})().catch(e=>{console.error(e);process.exitCode=1;});
