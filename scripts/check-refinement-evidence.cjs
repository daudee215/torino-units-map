/* Exercise actual context shards through the real UI module. */
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),path=require('node:path'),vm=require('node:vm'),{webcrypto}=require('node:crypto');
(async()=>{
 const root=path.resolve(__dirname,'..');let reads=0;
 const box={window:{},document:{documentElement:{lang:'en'}},URL,TextEncoder,Response,DecompressionStream,crypto:webcrypto,EvidenceLabels:{badge:()=>'<span>Document observation</span>'}};
 box.fetch=async relative=>{assert(relative.startsWith('data/refinement/'));assert(!relative.includes('..'));reads++;return new Response(await fs.readFile(path.join(root,relative.split('?')[0])));};
 vm.createContext(box);vm.runInContext(await fs.readFile(path.join(root,'refinement-evidence.js'),'utf8'),box);const ui=box.window.RefinementEvidence;
 const parcel={id:'cadastre:L219_128200.94',kind:'parcel'},d={selected_parcel:parcel.id,fp:'1282/94'};
 const html=await ui.context(parcel,d);assert(html.includes('236.7'));assert(html.includes('not assigned to this parcel'));assert(html.includes('2,602'));assert(html.includes('flat plane'));
 const civic=await ui.context({id:'civic:116066',kind:'entrance'},d);assert(civic.includes('30083353')&&civic.includes('VIA ROMA 366'));assert(civic.includes('not legal access'));
 const plava=await ui.context({id:'cadastre:L219_146400.262',kind:'parcel'},{selected_parcel:'cadastre:L219_146400.262',fp:'1464/262'});assert(plava.includes('unknown, not zero'));assert(plava.includes('<dd>0</dd>'));assert(plava.includes('4 sections'));
 const docs=await ui.documents(parcel,{fp:'1289/135'});assert(docs.includes('courtyard portions')&&docs.includes('subalterno 18'));assert(docs.includes('#page=2'));assert(!docs.includes('four apartments verified'));
 const cigna=await ui.documents(parcel,{fp:'1150/64'});assert(cigna.includes('171')&&cigna.includes('common non-assessable asset'));assert(cigna.includes('does not assign a document'));
 const bologna=await ui.documents(parcel,{fp:'1145/98'});assert(bologna.includes('1145/97')&&bologna.includes('subalterno not reported'));assert(!bologna.includes('#page=null'));
 const east=await ui.documents(parcel,{fp:'1204/98'});assert(east.includes('not two apartments')&&east.includes('54'));
 const catalogue=await ui.catalogue();assert(catalogue.includes('9 selected documentary sources')&&catalogue.includes('east'));
 box.document.documentElement.lang='it';const it=await ui.context(parcel,d);assert(it.includes('non assegnati')&&it.includes('Terreno'));assert(reads<12);
 console.log('Refinement: exact civic IDs, section-only housing, zero/unknown separation, terrain limits, scoped documents, bilingual labels and bounded reads verified.');
})().catch(e=>{console.error(e);process.exitCode=1;});
