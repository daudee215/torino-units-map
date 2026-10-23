"""Extract the April 2023 municipal asset inventory with positional schema checks.

Asset primary addresses are group attributes, not confirmed unit entrances.
The PDF and all extracted observations remain local and outside publication.
"""
from collections import Counter,defaultdict
from pathlib import Path
import hashlib
import json
import math
import re
import fitz

ROOT=Path(__file__).resolve().parents[1]
SOURCE='https://risorse.comune.torino.it/amministrazionetrasparente/bm~doc//fabbricati_di_propr_della_citt_e_loro_destinazione_d_uso_aprile_2023.pdf'
EDGES=[55.38,150.66,224.70,319.98,479.34,509.34,539.34,569.34,599.34,634.86,664.86,694.86]
FIELDS=['asset_group_code','municipality','asset_primary_address','asset_description','municipal_cadastral_row_code','sheet','parcel','subalterno','consistency_m2','consistency_rooms','consistency_m3']


def measure(raw):
    if not raw:return None
    if not re.fullmatch(r'\d+(?:[.,]\d+)?',raw):return None
    value=float(raw.replace(',','.'))
    return value if math.isfinite(value) else None


def main():
    path=ROOT/'_raw/documents/municipal-properties-april-2023.pdf'
    document=fitz.open(path);raw=[];groups=defaultdict(lambda:defaultdict(set));skipped=0
    assert len(document)==466 and 'Consistenza MQ' in document[0].get_text()
    excluded_pages=[];parsed_pages=[]
    for page_index,page in enumerate(document):
        if abs(page.rect.width-612)<1 and abs(page.rect.height-792)<1:
            excluded_pages.append(page_index+1);continue
        assert abs(page.rect.width-792)<1 and abs(page.rect.height-612)<1
        parsed_pages.append(page_index+1)
        lines=defaultdict(list)
        for word in page.get_text('words'):lines[round(word[1],1)].append(word)
        for y,words in sorted(lines.items()):
            cells=[[] for _ in FIELDS]
            for x0,_,x1,_,text,*_ in sorted(words,key=lambda w:w[0]):
                x=(x0+x1)/2
                for i in range(len(FIELDS)):
                    if EDGES[i]<=x<EDGES[i+1]:cells[i].append(text);break
            values=[' '.join(c) for c in cells]
            if not values[0].isdigit() or not values[4].isdigit():
                skipped+=1;continue
            row=dict(zip(FIELDS,values));row.update(page=page_index+1,row_y=y)
            for field in ['municipality','asset_primary_address','asset_description']:
                if row[field]:groups[row['asset_group_code']][field].add(row[field])
            raw.append(row)
    pilot={p.relative_to(ROOT/'data/registry/parcels').with_suffix('').as_posix() for p in (ROOT/'data/registry/parcels').glob('*/*.json')}
    records=[];uncertain=0
    for row in raw:
        inherited=[];conflicts=[]
        for field in ['municipality','asset_primary_address','asset_description']:
            values=groups[row['asset_group_code']][field]
            if len(values)>1:conflicts.append(field)
            if not row[field] and len(values)==1:row[field]=next(iter(values));inherited.append(field)
        if not row['municipality'].upper().startswith('TORINO'):continue
        fp=row['sheet']+'/'+row['parcel']
        numeric=all(row[k].isdigit() and row[k] not in {'0','999','9999'} for k in ['sheet','parcel','subalterno'])
        observation=dict(row,id=f"municipal-2023:{row['municipal_cadastral_row_code']}:{row['page']}:{row['row_y']}",
            member=['L219','',row['sheet'],row['parcel'],row['subalterno']],
            inherited_group_fields=inherited,group_field_conflicts=conflicts,
            scope='municipal_asset_cadastral_reference',address_scope='asset_group_primary_address',
            identity_status='reported_key' if numeric else 'incomplete_or_placeholder_key',
            current_validity='unknown',legal_confirmation=False,
            field_units=dict(consistency_m2='m²',consistency_rooms='rooms',consistency_m3='m³'),
            numeric_consistency={k:measure(row[k]) for k in ['consistency_m2','consistency_rooms','consistency_m3']},
            in_pilot=fp in pilot,source=SOURCE,edition='April 2023')
        records.append(observation);uncertain+=not numeric
    by_parcel=defaultdict(list)
    for record in records:
        if record['in_pilot']:by_parcel[record['sheet']+'/'+record['parcel']].append(record)
    result=dict(local_only=True,source=SOURCE,edition='April 2023',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        counts=dict(pdf_pages=len(document),parsed_complete_table_pages=len(parsed_pages),excluded_partial_layout_pages=len(excluded_pages),extracted_source_rows=len(raw),torino_rows=len(records),
            pilot_rows=sum(map(len,by_parcel.values())),pilot_parcels=len(by_parcel),
            incomplete_or_placeholder_torino_rows=uncertain,skipped_non_data_lines=skipped,
            duplicated_source_row_codes=sum(n>1 for n in Counter(r['municipal_cadastral_row_code'] for r in records).values())),
        excluded_pages=excluded_pages,exclusion_reason='Portrait print layouts repeat only partial columns; excluded rather than reconstructed or double-counted.',
        limitations=['Municipal assets only; not an apartment census.',
            'Primary address and description belong to the asset group, not each cadastral unit.',
            'Areas, room counts and cubic metres are distinct; blanks stay unknown.',
            'Automated PDF extraction is not individually page-verified for every row.',
            'Legacy sheets, placeholders and source conflicts are retained without alias inference.'],
        torino_records=records,pilot_records=dict(by_parcel))
    out=ROOT/'output/investigation/municipal-inventory.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
