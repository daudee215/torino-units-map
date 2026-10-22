"""Extract a reviewed ARERA residential benchmark without mixing customer classes.
The provincial 2023 archive encountered during discovery contains BTA/ATECO
non-domestic rows and is deliberately excluded from this residential benchmark.
"""
import datetime
import io
import json
import zipfile
from pathlib import Path
import openpyxl

root = Path(__file__).resolve().parents[1]
z = zipfile.ZipFile(root / "_raw/arera/Dati_regione_2025.zip")
name = next(n for n in z.namelist() if "Dati prelievo clienti" in n)
book = openpyxl.load_workbook(io.BytesIO(z.read(name)), read_only=True, data_only=True)
rows = list(book.active.values)[1:]
filtered = [r for r in rows if r[4] == "Piemonte" and r[1] == "Tutti"
            and r[2] == "1.5<potenza_impegnata<=3" and r[3] == "Residente"]
monthly = sorted([dict(month=r[0].month, kwh=r[8], f1=r[5], f2=r[6], f3=r[7])
                  for r in filtered if isinstance(r[0], datetime.datetime)], key=lambda r: r["month"])
annual = [r[8] for r in filtered if str(r[0]) == "2025"]
assert [r["month"] for r in monthly] == list(range(1, 13))
assert len(annual) == 1
total = sum(r["kwh"] for r in monthly)
assert abs(total - annual[0]) < 1e-6
out = dict(provider="ARERA", year=2025, region="Piemonte", market="Tutti", residency="Residente",
           power_class="1.5<potenza_impegnata<=3", monthly=monthly, annual_sum_monthly_kwh=total,
           annual_source_rows=[dict(kwh=annual[0])],
           source="https://www.arera.it/dati-e-statistiche/dettaglio/analisi-dei-consumi-dei-clienti-domestici",
           data_url="https://www.arera.it/fileadmin/allegati/dati/monitoraggioretail/Dati_regione_2025.zip",
           method="Sum of 12 monthly mean withdrawals, matching the published annual row; changing customer population, not a fixed-cohort annual bill.",
           scope="Regional resident domestic customers with contracted power >1.5 and <=3 kW, all markets; not individual-apartment measurement.",
           retrieved="2026-10-22")
(root / "data/demand_benchmark.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
print(f"ARERA Piemonte resident 1.5–3 kW 2025: {total:.3f} kWh/year; monthly and annual rows reconcile.")
