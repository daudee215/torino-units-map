"""Bounded, resumable public cadastral checks for the municipal inventory audit."""
from pathlib import Path
from datetime import datetime,timezone
import json,time,requests
ROOT=Path(__file__).resolve().parents[1]
BASE='https://energia-energiapt.piemontetu.it/fra-ept/restfacade/be/mgr/sicee/ape'

def main():
    parcels=json.loads((ROOT/'output/qa/unmatched-inventory-parcels.json').read_text(encoding='utf-8'))
    out=ROOT/'_raw/ape/review-phase';out.mkdir(parents=True,exist_ok=True)
    last=0;failures=0;count=0
    for fp in parcels:
        name='parcel-'+fp.replace('/','-')+'.json'
        if (ROOT/'_raw/ape/inventory'/name).exists() or (out/name).exists():continue
        time.sleep(max(0,1-(time.monotonic()-last)));last=time.monotonic()
        sheet,parcel=fp.split('/')
        query=dict(sezione='',foglio=sheet,particella=parcel,subalterno='',type='catast',noteInterneCatast='')
        result=dict(parcel=fp,query=query,source=BASE,retrieved=datetime.now(timezone.utc).isoformat(),status='error',scope='municipal_inventory_audit')
        try:
            response=requests.post(BASE,json=query,timeout=(15,60));response.raise_for_status();rows=response.json()
            assert isinstance(rows,list) and all(isinstance(r,dict) and {'anno','certificatore','progressivo'}<=r.keys() for r in rows)
            result.update(records=rows,returned_records=len(rows),complete_response=len(rows)<500,status='queried' if len(rows)<500 else 'possible_truncation');failures=0
        except (requests.RequestException,ValueError,AssertionError) as error:
            result['error']=str(error)[:250];failures+=1
        (out/name).write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
        count+=1;print(fp,result['status'],result.get('returned_records'),flush=True)
        if failures>=3:raise RuntimeError('Stopped after three consecutive provider failures; snapshots retained.')
    print('Additional parcel requests:',count)

if __name__=='__main__':main()
