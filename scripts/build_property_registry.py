"""Build a provenance-bearing public property graph and persistent local SQLite.

Unknown subalterni remain unknown. Certificates retain their own grain and energy
totals. Geometric/address proposals require review and never become legal facts.
"""
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/registry"
DB = ROOT / "output/registry/properties.sqlite"
TODAY = date(2026, 10, 23).isoformat()
PORTAL = "https://energia-energiapt.piemontetu.it/fra-ept/ape"
CATALOG = "https://www.dati.gov.it/view-dataset/dataset_id/dettaglio-attestato-di-prestazione-energetica-ape-sezione-dati-generali"


def norm(value):
    s = str(value if value is not None else "").strip().upper()
    return str(int(s)) if s.isdigit() else s


def text(value):
    return re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFKD", str(value if value is not None else "")).upper())


def floor_key(value):
    s=str(value if value is not None else '').strip().upper()
    if re.fullmatch(r'[+-]?\d+(?:[.,]\d+)?',s):return str(Decimal(s.replace(',','.')).normalize())
    return re.sub(r'\s+','',s)


def interior(value):
    raw = str(value if value is not None else '').strip()
    value = re.sub(r'\s+', ' ', raw.upper())
    # Punctuation, zero and descriptors are retained without claiming a unit label.
    placeholder=not re.search(r'[A-Z0-9]',value) or value in {'0','N.D.','ND','N/A','NA','SNC','NON INDICATO'}
    descriptor=bool(re.search(r'\b(SCALA|CORTILE|TUTTI|ALL|SUB)\b',value)) or value in {'BIS','TER'}
    candidate=bool(re.fullmatch(r'(?:\d{1,4}[A-Z]?|[A-Z]\d{0,3}|\d{1,4}[/ -][A-Z0-9]{1,4})',value))
    kind='placeholder' if placeholder else 'descriptor' if descriptor else 'identifier_candidate' if candidate else 'needs_review'
    return dict(raw=raw or None, normalized=value if kind=='identifier_candidate' else None,
                kind=kind,source_field='interno', source=CATALOG)


def numeric(value):
    try:
        result = float(Decimal(str(value).replace(",", "."))) if value not in (None, "") else None
        return result if result is None or math.isfinite(result) else None
    except InvalidOperation:
        return None


def packed(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def ident(prefix, obj):
    return prefix + hashlib.sha256(packed(obj).encode()).hexdigest()[:24]


def layer(name):
    d = json.loads((ROOT / f"data/{name}.json").read_text(encoding="utf-8"))
    return [{key:values[i] for key,values in d["p"].items()} for i in range(d["n"])]


def member(municipality, section, sheet, parcel, sub):
    return [norm(x) for x in [municipality, section, sheet, parcel, sub]]


def base_certificate(cid, members, **values):
    return dict(id=cid, members=sorted({tuple(m) for m in members}), **values)


def build():
    lots, buildings, entrances = layer("lotti"), layer("edifici"), layer("ingressi")
    valid_parcels = {r["foglio_particella"] for r in lots}
    by_parcel_b, by_parcel_e = defaultdict(list), defaultdict(list)
    for b in buildings:
        if b["foglio"] is not None:
            by_parcel_b[f"{norm(b['foglio'])}/{norm(b['particella'])}"].append(b)
    for e in entrances:
        if e["fp"]:
            by_parcel_e[e["fp"]].append(e)
    certificates, aliases, audit = {}, {}, Counter()
    source_runs, street_aliases, unmatched = [], {}, {}
    acquisition_paths=sorted((ROOT / "_raw/ape/inventory").glob("street-*.json"))
    acquisition_paths+=sorted((ROOT / "_raw/ape/inventory").glob("parcel-*.json"))
    seed=ROOT / "_raw/ape/parcel-1175-434.json"
    if seed.exists():acquisition_paths.append(seed)
    for path in acquisition_paths:
        run = json.loads(path.read_text(encoding="utf-8"))
        source_runs.append(dict(kind="street" if run.get("street") else "parcel",**{k:run.get(k) for k in ["street","parcel","status","retrieved","returned_records","complete_response","canonical_street"]}))
        if run.get("canonical_street"):
            street_aliases[text(run["street"])] = text(run["canonical_street"])
        for row in run.get("records", []):
            members = [member(c.get("codiceComuneCatastale"),c.get("sezione"),c.get("foglio"),c.get("particella"),c.get("subalterno")) for c in row.get("catasto", [])]
            if not any(m[0] == "L219" and f"{m[2]}/{m[3]}" in valid_parcels for m in members):
                if not members or any(not m[0] for m in members):
                    code="-".join(str(row[k]) for k in ['anno','certificatore','progressivo'])
                    unmatched[code]=dict(public_code=code,members=members,address=row.get('indirizzo'),civic=row.get('civico'),
                                         source=PORTAL,reason='missing_municipality_or_cadastral_identity',retrieved=run['retrieved'])
                else:audit["live_records_outside_pilot"] += 1
                continue
            code = "-".join(str(row[k]) for k in ["anno","certificatore","progressivo"])
            cid = "sipee:" + code
            record = base_certificate(cid, members, public_code=code, source_kind="live_portal", source=PORTAL,
                source_record_id=row.get("uid"), retrieved=run["retrieved"], object_scope="not_reported_in_live_metadata",
                internal_certifier_id=row.get("idCertificatore"),
                submitted=(row.get("dataInizio") or "")[:10], expires=(row.get("dataScadenza") or "")[:10],
                status=row.get("stato"), active=row.get("stato") == "Inviato",
                address=row.get("indirizzo"), civic=row.get("civico"), floor=row.get("piano"),
                heated_area_m2=numeric(row.get("supRiscaldata")), use=row.get("destUsoSigla"),
                residential=(row.get("destUsoSigla") or "").startswith("E1"), construction_year=row.get("annoCostruz"),
                source_class_field=row.get("zonClima"), energy_class=None)
            if cid in certificates:
                audit["repeated_live_search_hits"] += 1
                old = certificates[cid]
                if any(old.get(k) != record.get(k) for k in ["members","status","heated_area_m2","submitted"]):
                    old.setdefault("flags", []).append("conflicting_live_snapshots")
                    audit["conflicting_live_snapshots"] += 1
            else:
                certificates[cid] = record
    # Always retain the two manually checked PDFs; this is not an inventory denominator.
    checked = json.loads((ROOT / "data/ape_units.json").read_text(encoding="utf-8"))["certificates"]
    for row in checked:
        cid = "sipee:" + row["id"]
        if cid not in certificates:
            sheet, parcel = row["parcel"].split("/")
            certificates[cid] = base_certificate(cid,[member("L219","",sheet,parcel,s) for s in row["subalterni"]],
                source_kind="inspected_pdf", source=PORTAL, submitted=row["submitted"], expires=row["valid_until"],
                status=row["status"], active=True, address=row["address"], civic="17", floor=row["floor"],
                heated_area_m2=row["heated_area_m2"], residential=row["use"] == "residential", public_code=row["id"])
        certificates[cid].update(object_scope="unit", energy_class=row["energy_class"], inspected_pdf=True,
                                 standard_electricity_kwh_year=row["standard_electricity_kwh_year"])
    bulk_path = ROOT / "data/ape_bulk_general.json"
    bulk_source = None
    if bulk_path.exists():
        bulk = json.loads(bulk_path.read_text(encoding="utf-8"))
        bulk_source = bulk["source"]
        grouped = defaultdict(list)
        for r in bulk["records"]:
            grouped[r["id_certificato"]].append(r)
        # Cross-source matching is deliberately strict, with ambiguous candidates kept separate.
        def signature(c):
            return packed([c["members"],c.get("submitted"),c.get("heated_area_m2"),floor_key(c.get("floor"))])
        live_index = defaultdict(list)
        encoded_key_index = defaultdict(list)
        for cid,c in certificates.items():
            live_index[signature(c)].append(cid)
            if c.get('public_code') and c.get('internal_certifier_id'):
                year,_,progress=c['public_code'].split('-')
                encoded_key_index[year+progress+str(c['internal_certifier_id'])].append(cid)
        key_lengths={len(key) for key in encoded_key_index}
        for external, rows in grouped.items():
            r = rows[0]
            members = [member(x["codice_comune_catastale"],x["sezione"],x["foglio"],x["particella"],x["subalterno"]) for x in rows]
            cid = "bulk:" + external
            obj = r.get("oggetto_ape") or ""
            scope = "whole_building" if "Intero" in obj else "group" if "Gruppo" in obj else "unit" if "immobiliare" in obj else "unknown"
            record = base_certificate(cid,members, source_kind="regional_bulk", source=CATALOG,
                source_record_id=external, object_scope=scope, submitted=(r.get("data_invio_file") or "")[:10],
                expires=(r.get("data_scadenza") or "")[:10], status="active_source_flag" if r.get("flg_attivo") == "1" else "inactive_source_flag",
                active=r.get("flg_attivo") == "1", address=r.get("desc_indirizzo"), civic=r.get("num_civico"),
                floor=r.get("piano"), heated_area_m2=numeric(r.get("sup_riscaldata")),
                residential=r.get("flg_residenziale") == "S", use=r.get("destinazione_uso"),
                construction_year=r.get("anno_costruzione"), declared_building_units=r.get("nr_um"), energy_class=None)
            record['interior_observations'] = [dict(interior(x.get('interno')), source_record_id=external,
                submitted=record['submitted']) for x in rows]
            record['interior_observations'] = list({packed(x):x for x in record['interior_observations']}.values())
            # Equal dates, floors and areas can belong to DIFFERENT certificates.
            # Corroborate the publisher's encoded certificate key as well as date and
            # at least one exact cadastral member. This also preserves additional
            # subalterni reported only by the live portal.
            try:decoded=bytes.fromhex(external).decode('ascii')
            except (ValueError,UnicodeDecodeError):decoded=''
            possible={cid for length in key_lengths for cid in encoded_key_index.get(decoded[-length:],[])}
            candidates=[cid for cid in possible if certificates[cid].get('submitted')==record.get('submitted')
                        and set(map(tuple,certificates[cid]['members'])) & set(map(tuple,record['members']))]
            if len(candidates) == 1:
                main = certificates[candidates[0]]
                main.setdefault('interior_observations', []).extend(record['interior_observations'])
                main.setdefault("source_aliases", []).append({"id":cid,"source":CATALOG,"method":"observed_encoded_certificate_key_plus_date_and_cadastral_member", "members":record['members'],"submitted":record['submitted'],"heated_area_m2":record['heated_area_m2'],"floor":record['floor'],"object_scope":scope,"declared_building_units":record.get('declared_building_units'),"active":record['active'],"expires":record['expires']})
                if not main.get('inspected_pdf'):main["object_scope"] = scope
                aliases[cid] = main["id"]
                audit["unique_cross_source_matches"] += 1
                if main['members'] != record['members']:
                    main.setdefault('flags',[]).append('source_cadastral_members_differ')
                    audit['source_cadastral_members_differ']+=1
                for key in ['heated_area_m2','floor']:
                    if (floor_key(main.get(key)) != floor_key(record.get(key))) if key=='floor' else main.get(key)!=record.get(key):
                        main.setdefault('flags',[]).append('source_'+key+'_disagreement')
                if main["active"] != record["active"]:
                    main.setdefault("flags", []).append("source_status_disagreement")
            else:
                if live_index.get(signature(record)):
                    record.setdefault('flags',[]).append('same_attributes_different_certificate_key')
                    audit['attribute_match_rejected_by_certificate_key']+=1
                if len(candidates) > 1:
                    record["flags"] = ["ambiguous_certificate_alias"]
                certificates[cid] = record
            audit["duplicate_bulk_rows"] += len(rows) - len({packed(x) for x in rows})
    properties, membership_index, section_index = {}, defaultdict(set), defaultdict(set)
    for cid,c in certificates.items():
        c["members"] = [list(m) for m in c["members"]]
        c["eligible_on_date"] = bool(c.get("active") and c.get("expires") and c["expires"] >= TODAY and c.get("submitted", "") <= TODAY)
        known = bool(c["members"] and all(m[0] and m[2] and m[3] and m[4].isdigit() for m in c["members"]))
        # Whole-building and grouped attestations never silently merge with a unit.
        scope = c.get("object_scope", "unknown")
        family = scope if scope in ("whole_building","group") else "cadastral_property"
        pid = ident("property:",[family,c["members"] if known else cid])
        prop = properties.setdefault(pid,dict(id=pid,members=c["members"],identity_complete=known,scope=family,
                                             certificates=[],flags=[]))
        prop["certificates"].append(cid)
        c["property_id"] = pid
        if not known:
            prop["flags"].append("missing_subalterno_or_identity")
        for m in c["members"]:
            membership_index[packed(m)].add(pid)
            section_index[packed([m[0],*m[2:]])].add(m[1])
    for p in properties.values():
        eligible = [certificates[k] for k in p["certificates"] if certificates[k]["eligible_on_date"]]
        preferred = sorted(eligible or [certificates[k] for k in p["certificates"]],key=lambda c:(c.get("submitted") or "",c["id"]),reverse=True)[0]
        p.update(latest_certificate=preferred["id"],eligible_certificates=len(eligible),residential=preferred.get("residential"),
                 address=preferred.get("address"),civic=preferred.get("civic"),floor=preferred.get("floor"),heated_area_m2=preferred.get("heated_area_m2"))
        observations=[dict(o,certificate_id=cid) for cid in p['certificates'] for o in certificates[cid].get('interior_observations',[])]
        p['interior_observations']=observations
        p['reported_interiors']=sorted({o['normalized'] for o in observations if o['normalized']})
        if len(p['reported_interiors'])>1:
            p['flags'].append('conflicting_reported_interiors')
        if len(eligible)>1:
            p["flags"].append("multiple_eligible_certificates_review_renewals")
        if any(len(membership_index[packed(m)])>1 for m in p["members"]):
            p["flags"].append("overlapping_cadastral_memberships")
        if any(len(section_index[packed([m[0],*m[2:]])])>1 for m in p["members"]):
            p["flags"].append("cadastral_section_alias_requires_review")
        p["flags"] = sorted(set(p["flags"]))
    graph = {}
    for fp in valid_parcels:
            graph[fp] = dict(parcel=fp,properties=[],certificates=[],buildings=by_parcel_b[fp],entrances=by_parcel_e[fp],links=[],unresolved_certificates=[])
    for u in unmatched.values():
        for fp in {f'{m[2]}/{m[3]}' for m in u['members'] if not m[0] and f'{m[2]}/{m[3]}' in graph}:
            graph[fp]['unresolved_certificates'].append(u)
    def link(g, source, target, kind, evidence, status="candidate"):
        value=dict(id=ident("link:",[source,target,kind]),source=source,target=target,kind=kind,status=status,evidence=evidence,
                   valid_from=None,valid_to=None)
        if not any(x["id"] == value["id"] for x in g["links"]):
            g["links"].append(value)
    for p in properties.values():
        fps = sorted({f"{m[2]}/{m[3]}" for m in p["members"] if m[0] == "L219" and f"{m[2]}/{m[3]}" in valid_parcels})
        for fp in fps:
            g = graph[fp]
            g["properties"].append(p)
            g["certificates"].extend(certificates[c] for c in p["certificates"])
            link(g,p["id"],"parcel:L219/"+fp,"declared_parcel",["source cadastral identifiers"],"source_declared")
            address = text(p.get("address"))
            civic = text(p.get("civic"))
            exact = []
            for e in g["entrances"]:
                street = street_aliases.get(text(e["VIA"]),text(e["VIA"]))
                # Bulk addresses sometimes already include civic numbers; no fuzzy matches are accepted.
                if (address == street or address == street+civic) and civic and text(e["CIVICO"]) == civic:
                    exact.append(e)
            for e in exact:
                link(g,p["id"],"entrance:"+str(e["COD_CIVICO"]),"property_entrance",["source property parcel matches inherited entrance parcel assignment","exact normalized street and civic including suffix","entrance GIS match: "+str(e['match_lotto'])])
            candidates = {str(e["bld_id"]) for e in exact if e["bld_id"] is not None}
            for b in g["buildings"]:
                via = str(b["bld_id"]) in candidates
                link(g,p["id"],"building:"+str(b["bld_id"]),"property_building",
                     ["same parcel", "inherited GIS entrance-to-building proposal" if via else "parcel-only proposal; interior unit position unknown"])
            if not exact:
                p["flags"] = sorted(set(p["flags"] + ["entrance_match_unresolved"]))
    alias_groups=defaultdict(list)
    for p in properties.values():
        if p['identity_complete']:
            alias_groups[packed([p['scope'],sorted([[m[0],*m[2:]] for m in p['members']])])].append(p)
    for candidates in alias_groups.values():
        for i,left in enumerate(candidates):
            for right in candidates[i+1:]:
                common={f'{m[2]}/{m[3]}' for m in left['members']} & {f'{m[2]}/{m[3]}' for m in right['members']} & valid_parcels
                for fp in common:
                    link(graph[fp],min(left['id'],right['id']),max(left['id'],right['id']),'property_alias',
                         ['same cadastral identifiers except section; confirm whether blank and stated sections identify the same property'])
    OUT.mkdir(parents=True,exist_ok=True)
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB)
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
      CREATE TABLE IF NOT EXISTS entities(id TEXT PRIMARY KEY, kind TEXT NOT NULL, attributes TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS properties(id TEXT PRIMARY KEY REFERENCES entities(id), identity_complete INTEGER NOT NULL, scope TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS certificates(id TEXT PRIMARY KEY REFERENCES entities(id), property_id TEXT NOT NULL REFERENCES properties(id), submitted TEXT, expires TEXT, active INTEGER NOT NULL, eligible INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS cadastral_members(property_id TEXT REFERENCES properties(id), municipality TEXT, section TEXT, sheet TEXT, parcel TEXT, subalterno TEXT, PRIMARY KEY(property_id,municipality,section,sheet,parcel,subalterno));
      CREATE TABLE IF NOT EXISTS relationships(id TEXT PRIMARY KEY, source TEXT NOT NULL REFERENCES entities(id), target TEXT NOT NULL REFERENCES entities(id), kind TEXT NOT NULL, status TEXT NOT NULL, evidence TEXT NOT NULL, valid_from TEXT, valid_to TEXT);
      CREATE INDEX IF NOT EXISTS relationships_source ON relationships(source);
      CREATE TABLE IF NOT EXISTS source_runs(id TEXT PRIMARY KEY, metadata TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS review_events(id INTEGER PRIMARY KEY AUTOINCREMENT, relationship_id TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('accepted','rejected','unreviewed')), note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
      CREATE INDEX IF NOT EXISTS review_target ON review_events(relationship_id,id);
    """)
    review_columns={r[1] for r in db.execute('PRAGMA table_info(review_events)')}
    for column in ['valid_from','valid_to']:
        if column not in review_columns:db.execute('ALTER TABLE review_events ADD COLUMN '+column+' TEXT')
    with db:
        for table in ["relationships","cadastral_members","certificates","properties","entities","source_runs"]:
            db.execute("DELETE FROM "+table)
        def entity(eid,kind,attrs):
            db.execute("INSERT OR IGNORE INTO entities VALUES(?,?,?)",(eid,kind,packed(attrs)))
        for fp,g in graph.items():
            entity("parcel:L219/"+fp,"parcel",{"parcel":fp})
            for b in g["buildings"]:entity("building:"+str(b["bld_id"]),"building",b)
            for e in g["entrances"]:entity("entrance:"+str(e["COD_CIVICO"]),"entrance",e)
        for pid,p in properties.items():
            entity(pid,"property",p)
            db.execute("INSERT INTO properties VALUES(?,?,?)",(pid,int(p["identity_complete"]),p["scope"]))
            db.executemany("INSERT INTO cadastral_members VALUES(?,?,?,?,?,?)",[(pid,*m) for m in p["members"]])
        for cid,c in certificates.items():
            entity(cid,"certificate",c)
            db.execute("INSERT INTO certificates VALUES(?,?,?,?,?,?)",(cid,c["property_id"],c.get("submitted"),c.get("expires"),int(c["active"]),int(c["eligible_on_date"])))
        for fp,g in graph.items():
            for l in g["links"]:
                db.execute("INSERT OR IGNORE INTO relationships VALUES(?,?,?,?,?,?,?,?)",(l["id"],l["source"],l["target"],l["kind"],l["status"],packed(l["evidence"]),None,None))
            folder=OUT / "parcels" / fp.split("/")[0]
            folder.mkdir(parents=True,exist_ok=True)
            (folder / (fp.split("/")[1]+".json")).write_text(packed(g),encoding="utf-8")
        for i,run in enumerate(source_runs):db.execute("INSERT INTO source_runs VALUES(?,?)",("street:"+str(i),packed(run)))
        if bulk_source:db.execute("INSERT INTO source_runs VALUES(?,?)",("regional_bulk",packed(bulk_source)))
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert not db.execute("PRAGMA foreign_key_check").fetchall()
    db.close()
    capped_streets={r['street'] for r in source_runs if r['kind']=='street' and r['status']=='possible_truncation'}
    targeted_parcels={e['fp'] for e in entrances if e.get('fp') and e['VIA'] in capped_streets}
    targeted_runs=[r for r in source_runs if r['kind']=='parcel' and r.get('parcel') is not None]
    summary=dict(version="2.2.0-dev.1",as_of=TODAY,built=datetime.now(timezone.utc).isoformat(),
        counts=dict(parcels=len(graph),parcels_with_evidence=sum(bool(g["properties"]) for g in graph.values()),
            properties=len(properties),identity_complete_properties=sum(p["identity_complete"] for p in properties.values()),
            certificates=len(certificates),eligible_certificates=sum(c["eligible_on_date"] for c in certificates.values()),
            properties_with_flags=sum(bool(p["flags"]) for p in properties.values()),
            street_queries=sum(r['kind']=="street" for r in source_runs),street_queries_capped=sum(r['kind']=='street' and r["status"] == "possible_truncation" for r in source_runs),
            targeted_parcel_queries=sum(r['kind']=='parcel' and r.get('parcel') is not None for r in source_runs),
            targeted_parcel_search_total=len(targeted_parcels),
            targeted_parcel_queries_error=sum(r['status']=='error' for r in targeted_runs),
            targeted_parcel_queries_capped=sum(r['status']=='possible_truncation' for r in targeted_runs),
            targeted_parcel_queries_empty=sum(r.get('returned_records')==0 and r['status']=='queried' for r in targeted_runs),
            properties_with_reported_interior=sum(bool(p['reported_interiors']) for p in properties.values()),
            properties_with_interior_conflict=sum('conflicting_reported_interiors' in p['flags'] for p in properties.values())),
        bulk_source=bulk_source,source_runs=source_runs,audit=dict(audit),
        limitations=["Source coverage is not a complete apartment census.","Blank cadastral sections are preserved, not guessed.",
            "Candidate entrance/building relationships require review.","Certificates and overlapping cadastral sets are not apartment counts.",
            "No apartment polygons, PODs or measured energy were created."],
        parcels=[dict(parcel=fp,properties=len(g["properties"]),certificates=len(g["certificates"]),
                      addresses=sorted({e['indirizzo'] for e in g['entrances']})) for fp,g in sorted(graph.items())])
    summary['counts']['unmatched_records_missing_identity']=len(unmatched)
    (OUT / 'unmatched.json').write_text(packed(list(unmatched.values())),encoding='utf-8')
    (OUT / "summary.json").write_text(packed(summary),encoding="utf-8")
    print(packed(summary["counts"]))


if __name__ == "__main__":
    build()
