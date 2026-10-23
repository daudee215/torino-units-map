"""Export public source facts/proposals; never review notes or future meters."""
import csv
import io
import json
from pathlib import Path
import sqlite3
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def csv_bytes(rows,fields):
    out=io.StringIO(newline='')
    writer=csv.DictWriter(out,fieldnames=fields)
    writer.writeheader()
    for row in rows:
        values={}
        for key in fields:
            value=row.get(key)
            if isinstance(value,(list,dict)):value=json.dumps(value,ensure_ascii=False,separators=(',',':'))
            if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@','\t','\r')):value="'"+value
            values[key]='' if value is None else value
        writer.writerow(values)
    return out.getvalue().encode('utf-8-sig')


def main():
    with sqlite3.connect(ROOT/'output/registry/properties.sqlite') as db:
        properties=[json.loads(r[0]) for r in db.execute("SELECT attributes FROM entities WHERE kind='property' ORDER BY id")]
        certificates=[json.loads(r[0]) for r in db.execute("SELECT attributes FROM entities WHERE kind='certificate' ORDER BY id")]
        links=[dict(zip(['id','source','target','kind','status','evidence','valid_from','valid_to'],r)) for r in db.execute('SELECT id,source,target,kind,status,evidence,valid_from,valid_to FROM relationships ORDER BY id')]
    target=ROOT/'data/download/torino_property_registry_v2.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('properties.csv',csv_bytes(properties,['id','scope','identity_complete','members','address','civic','floor','reported_interiors','interior_observations','heated_area_m2','residential','certificates','latest_certificate','flags']))
        archive.writestr('certificates.csv',csv_bytes(certificates,['id','public_code','source_record_id','property_id','members','object_scope','submitted','expires','status','eligible_on_date','address','civic','floor','interior_observations','heated_area_m2','source','source_kind','source_aliases','flags','standard_electricity_kwh_year']))
        archive.writestr('relationship_proposals.csv',csv_bytes(links,['id','source','target','kind','status','evidence','valid_from','valid_to']))
        archive.write(ROOT/'data/registry/summary.json','source-audit.json')
        archive.write(ROOT/'data/roof_evidence.json','roof-evidence.json')
        archive.writestr('README.txt','Local v2 public-source register. Properties/groups and certificates are different grains, not a complete apartment census.\n'
            'No apartment interior geometry, PODs or measured consumption. Multi-subalterno certificate totals are not duplicated.\n'
            'Relationship proposals are unreviewed source-derived candidates. The local review ledger and all review notes are excluded.\n'
            'Blank fields mean unknown/not reported, never zero. Roof evidence is not a surveyed LoD2/2.5 dataset.\n'
            'Original-provider attribution and source dates are retained in source-audit.json and certificate source URLs.\n')
    print(f'Source register ZIP: {target.stat().st_size:,} bytes; {len(properties):,} identities, {len(certificates):,} certificates; reviews excluded.')


if __name__=='__main__':main()
