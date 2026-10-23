"""Additional page-inspected, non-personal observations. No legal changes inferred."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]

def main():
    sources=json.loads((ROOT/'output/qa/review-document-downloads.json').read_text(encoding='utf-8'))
    specs=[
        (4,4,'2021','1175/643','114','VIA DIGIONE 3','documented_address_only',False,
         'Il piano 2021–2023 riporta il subalterno 114 come ex portineria. Non dimostra una trasformazione del subalterno 113.',
         'The 2021–2023 plan reports subalterno 114 as former porter premises. It does not establish a change from subalterno 113.'),
        (3,2,'2022','1175/643','114','VIA DIGIONE 3','documented_historical_access',False,
         'Il documento del 2022 riporta accesso diretto dall’androne carraio e un servizio comune nel cortile per il subalterno 114.',
         'The 2022 document reports direct access from the vehicle entrance hall and a shared courtyard facility for subalterno 114.'),
        (0,11,None,'1221/149','2','VIA BEAUMONT 22','documented_address_only',True,
         'Il piano 2025–2027, nella sezione programmata ANNO 2027, elenca il subalterno 2 al piano terra, con 53 m² catastali e aggiornamento da effettuare. Non attesta una variazione eseguita nel 2025 o nel 2027.',
         'The 2025–2027 plan, in its planned YEAR 2027 section, lists ground-floor subalterno 2, 53 cadastral m², with updating pending. It does not attest a completed change in 2025 or 2027.'),
        (2,9,None,'1221/149','2','VIA BEAUMONT 22','documented_address_only',True,
         'Il piano 2026–2028, nella sezione programmata ANNO 2028, riporta ancora il subalterno 2 da aggiornare. Il 2028 è un anno di programma, non la data di una variazione eseguita.',
         'The 2026–2028 plan, in its planned YEAR 2028 section, still lists subalterno 2 for updating. 2028 is a programme year, not the date of a completed change.')]
    out=[]
    for i,page,year,fp,sub,address,status,pending,it,en in specs:
        source=sources[i];assert hashlib.sha256((ROOT/source['file']).read_bytes()).hexdigest()==source['sha256']
        sheet,parcel=fp.split('/')
        out.append(dict(id=f'review-doc-{i}-{page}',source=source['url'],page=page,sha256=source['sha256'],
            observed_source_year=year,source_label=year or ('2025–2027 plan / planned 2027' if i==0 else '2026–2028 plan / planned 2028'),planned_year=2028 if i==2 else 2027 if i==0 else None,
            members=[['L219','',sheet,parcel,sub]],parcel=fp,address=address,status=status,
            cadastral_update_pending=pending,claims_it=it,claims_en=en,manually_page_inspected=True,
            current_access_confirmed=False,completed_cadastral_change=False,source_lineage='municipal_property_documents'))
    target=ROOT/'output/property-review';target.mkdir(exist_ok=True)
    (target/'document-observations.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('Prepared four additional inspected observations; no renumbering, sale or future change inferred.')

if __name__=='__main__':main()
