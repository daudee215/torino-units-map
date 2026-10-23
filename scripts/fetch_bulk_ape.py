"""Download the official CC BY 4.0 general APE table and retain pilot rows.

The raw CSV is ignored. Public output is allowlisted, with no free-text notes,
contacts or declarations. Original certificate IDs are preserved verbatim.
"""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
CODE = "Sicee_v_dati_generali_v2_8405"
URL = f"https://api.smartdatanet.it/api/{CODE}/download/8405/all"
CATALOG = "https://www.dati.gov.it/view-dataset/dataset_id/dettaglio-attestato-di-prestazione-energetica-ape-sezione-dati-generali"
FIELDS = "id_certificato data_invio_file data_scadenza oggetto_ape nr_um coord_e coord_n desc_prov desc_comune desc_indirizzo num_civico interno piano cap rif_catasto codice_comune_catastale foglio sezione particella subalterno destinazione_uso descr_destinazione_uso flg_residenziale sup_riscaldata sup_raffrescata vol_lordo_riscaldato zona_climatica anno_costruzione flg_attivo".split()


def normalized(value):
    value = str(value if value is not None else "").strip().upper()
    return str(int(value)) if value.isdigit() else value


def run():
    folder = ROOT / "_raw/ape/bulk"
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "general.csv"
    meta_path = folder / "general-source.json"
    if not source.exists():
        temporary = source.with_suffix(".partial")
        digest = hashlib.sha256()
        total = 0
        with requests.get(URL, stream=True, timeout=(15, 90)) as response:
            response.raise_for_status()
            with temporary.open("wb") as output:
                for chunk in response.iter_content(4 * 1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
                    total += len(chunk)
                    if total > 4 * 1024**3:
                        raise ValueError("Unexpected bulk size; stopped before unbounded acquisition")
                    if total // (64 * 1024**2) != (total-len(chunk)) // (64 * 1024**2):
                        print(f"Official general APE download: {total/1024**2:.0f} MiB", flush=True)
        temporary.replace(source)
        meta_path.write_text(json.dumps(dict(url=URL, catalog=CATALOG, license="CC BY 4.0",
            provider="Regione Piemonte / CSI Piemonte", retrieved=datetime.now(timezone.utc).isoformat(),
            bytes=total, sha256=digest.hexdigest()), indent=2), encoding="utf-8")
    lots = json.loads((ROOT / "data/lotti.json").read_text(encoding="utf-8"))["p"]
    parcel_keys = {(normalized(f), normalized(p)) for f,p in zip(lots["foglio"], lots["particella"])}
    records, count, city_count, latest = [], 0, 0, None
    # The publisher's CSV uses single-byte Italian accented characters.
    with source.open(encoding="cp1252", errors="replace", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        assert set(FIELDS) <= set(reader.fieldnames or []), "Official general APE schema changed"
        for row in reader:
            count += 1
            if normalized(row["codice_comune_catastale"]) != "L219":
                continue
            city_count += 1
            date = row["data_invio_file"][:10]
            if date and (latest is None or date > latest):
                latest = date
            if (normalized(row["foglio"]),normalized(row["particella"])) in parcel_keys:
                records.append({field:row[field].strip() or None for field in FIELDS})
    source_meta = json.loads(meta_path.read_text(encoding="utf-8"))
    source_meta.update(rows_read=count,torino_rows=city_count,retained_pilot_rows=len(records),
        latest_torino_submission=latest, selection="L219 plus exact normalized pilot sheet/parcel; not coordinate geocoding",
        catalog_modified="2019-11-02", catalog_freshness_warning="Catalog date is stale; report actual row dates separately")
    target = ROOT / "data/ape_bulk_general.json"
    target.write_text(json.dumps(dict(source=source_meta,records=records),ensure_ascii=False,separators=(",", ":")),encoding="utf-8")
    print(json.dumps({k:source_meta[k] for k in ['rows_read','torino_rows','retained_pilot_rows','latest_torino_submission']}),flush=True)


if __name__ == "__main__":
    run()
