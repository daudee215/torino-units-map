"""Check all source shards, evidence grain and public file hashes before Pages."""
from pathlib import Path
import json
from build_public_site import inputs
from check_city_publication import check as check_city,clean
from check_municipal_publication import check as check_municipal
ROOT=Path(__file__).resolve().parents[1]

def check():
 (ROOT/'output/qa').mkdir(parents=True,exist_ok=True)
 m=inputs();check_city(ROOT);check_municipal(ROOT/'data/municipal')
 cases=json.loads((ROOT/'data/property-evidence/cases.json').read_text(encoding='utf8'));clean(cases)
 assert cases['case_count']==len(cases['cases'])==13 and cases['verified_current_access']==0
 assert all(not c['current_access_confirmed'] and not c['source_identities_changed'] for c in cases['cases'])
 tiles=json.loads((ROOT/'data/parcel-overview/manifest.json').read_text())
 assert tiles['source_parcels']==82434 and set(tiles['coverage_by_zoom'].values())=={82434}
 assert len(tiles['files'])==142
 print(f"Release {m['version']} source/file boundary verified; 13 evidence cases; current access unverified.",flush=True)

if __name__=='__main__':check()
