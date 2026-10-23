"""Resume public SIPEE street searches observed in the official citizen UI.

No login, private API, PDFs or contacts. Responses reaching the observed 500-row
limit are explicitly incomplete. Raw response snapshots stay ignored in _raw/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import re
import unicodedata
from datetime import datetime, timezone
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://energia-energiapt.piemontetu.it/fra-ept/restfacade/be/mgr/sicee/"
CACHE = ROOT / "_raw/ape/inventory"


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    temp.replace(path)


def run(limit=None, retry_unresolved=False):
    entrances = json.loads((ROOT / "data/ingressi.json").read_text(encoding="utf-8"))
    streets = sorted(set(entrances["p"]["VIA"]))
    session = requests.Session()
    last_request = 0

    def request(method, suffix, **kwargs):
        nonlocal last_request
        time.sleep(max(0, 1 - (time.monotonic() - last_request)))
        last_request = time.monotonic()
        r = session.request(method, BASE + suffix, timeout=(15, 60), **kwargs)
        r.raise_for_status()
        return r.json()

    for index, street in enumerate(streets[:limit] if limit else streets, 1):
        key = hashlib.sha256(street.encode()).hexdigest()[:16]
        target = CACHE / f"street-{key}.json"
        previous=json.loads(target.read_text(encoding='utf-8')) if target.exists() else None
        if previous and (not retry_unresolved or previous['status'] in {'queried','possible_truncation'}):continue
        stamp = datetime.now(timezone.utc).isoformat()
        result = dict(street=street, retrieved=stamp, source=BASE + "ape", status="error")
        if previous:result['previous_status']=previous['status']
        try:
            query_street=re.sub(r'\bS\.\s*','SAN ',street)
            if street=='PIAZZA DICIOTTO DICEMBRE':query_street='PIAZZA XVIII DICEMBRE'
            # Official normalizer resolves the legacy civic-layer name to DON BOSCO GIOVANNI.
            if street=='VIA S. GIOVANNI BOSCO':query_street='VIA GIOVANNI BOSCO'
            suffix='-'+hashlib.sha256(query_street.encode()).hexdigest()[:8] if query_street!=street else ''
            normalizer = CACHE / f"normalize-{key}{suffix}.json"
            if normalizer.exists():
                matches = json.loads(normalizer.read_text(encoding="utf-8"))
            else:
                matches = request("GET", "indirizzo", params={"indirizzo": "Torino " + query_street})
                save(normalizer, matches)
            choices = {x["properties"]["tipoVia"] + " " + x["properties"]["nomeVia"]: x["properties"]
                       for x in matches if x.get("type") == "STRADE"
                       and x.get("properties", {}).get("codiceIstat") == "001272"}
            fold=lambda s:re.sub('[^A-Z0-9]','',unicodedata.normalize('NFKD',s).upper())
            exact={k:v for k,v in choices.items() if fold(k)==fold(query_street)}
            if len(exact)==1:choices=exact
            if len(choices) != 1:
                result.update(status="ambiguous_street" if choices else "unresolved_street", choices=list(choices))
            else:
                canonical, props = next(iter(choices.items()))
                query = dict(istatComune="001272", indirizzo=props["nomeVia"], type="indirizzo")
                rows = request("POST", "ape", json=query)
                if not isinstance(rows, list):
                    raise ValueError("Expected a certificate array")
                result.update(status="possible_truncation" if len(rows) >= 500 else "queried",
                              canonical_street=canonical, query=query, records=rows,
                              returned_records=len(rows), complete_response=len(rows) < 500)
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            result["error"] = str(exc)[:300]
        save(target, result)
        print(f"{index}/{len(streets)} {street}: {result['status']} ({result.get('returned_records', 0)})", flush=True)


def capped_parcels(limit=30):
    """Target parcels on capped streets with the already observed citizen query.

    Cap flags remain on original searches. A parcel query without a municipality
    field is not evidence that its returned cadastral municipality is Torino.
    """
    capped={r['street'] for path in CACHE.glob('street-*.json')
            if (r:=json.loads(path.read_text(encoding='utf-8'))).get('status')=='possible_truncation'}
    entrances=json.loads((ROOT/'data/ingressi.json').read_text(encoding='utf-8'))['p']
    parcels=sorted({fp for street,fp in zip(entrances['VIA'],entrances['fp']) if street in capped and fp})
    remaining=[fp for fp in parcels if not (CACHE/f"parcel-{fp.replace('/','-')}.json").exists()]
    print(f'{len(parcels)} parcels on capped streets; {len(remaining)} not yet queried',flush=True)
    for fp in remaining[:limit]:
        sheet,parcel=fp.split('/')
        query=dict(sezione='',foglio=sheet,particella=parcel,subalterno='',type='catast',noteInterneCatast='')
        result=dict(parcel=fp,query=query,retrieved=datetime.now(timezone.utc).isoformat(),source=BASE+'ape',status='error')
        try:
            response=requests.post(BASE+'ape',json=query,timeout=(15,60));response.raise_for_status();rows=response.json()
            if not isinstance(rows,list):raise ValueError('Expected certificate array')
            result.update(records=rows,returned_records=len(rows),complete_response=len(rows)<500,
                status='possible_truncation' if len(rows)>=500 else 'queried')
        except (requests.RequestException,ValueError) as exc:result['error']=str(exc)[:300]
        save(CACHE/f"parcel-{fp.replace('/','-')}.json",result)
        print(fp,result['status'],result.get('returned_records',0),flush=True)
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--retry-unresolved", action='store_true')
    parser.add_argument("--capped-parcels",action='store_true')
    args = parser.parse_args()
    if args.capped_parcels:capped_parcels(args.limit or 30)
    else:run(args.limit,args.retry_unresolved)
