"""Inspect a real height-service tile. This does not reconstruct roof planes."""
from collections import Counter
import json
from pathlib import Path
import geopandas as gpd
from lxml import etree
from enrich_public_data import decode

ROOT=Path(__file__).resolve().parents[1]


def main():
    sample=gpd.read_file(ROOT / "_raw/roofs/arpa-pilot-sample.geojson").to_crs(32632)
    data=json.loads((ROOT / "data/edifici.json").read_text(encoding="utf-8"))
    meta=json.loads((ROOT / "data/meta.json").read_text(encoding="utf-8"))
    rows=[{k:v[i] for k,v in data['p'].items()} for i in range(data['n'])]
    buildings=gpd.GeoDataFrame(rows,geometry=[decode(g,meta) for g in data['g']],crs=4326).to_crs(32632)
    results=[]
    for _,feature in sample.iterrows():
        candidates=buildings.iloc[buildings.sindex.query(feature.geometry,predicate="intersects")]
        scored=[]
        for _,b in candidates.iterrows():
            if not feature.geometry.is_valid or not b.geometry.is_valid:
                continue
            union=feature.geometry.union(b.geometry).area
            iou=feature.geometry.intersection(b.geometry).area / union if union else 0
            scored.append((iou,b))
        scored.sort(key=lambda x:x[0],reverse=True)
        if not scored or scored[0][0]<0.8:
            continue
        iou,b=scored[0]
        results.append(dict(arpa_id=int(feature.OBJECTID),building_id=str(b.bld_id),iou=round(iou,5),
                            arpa_height_m=int(feature.ELEV),quality_code=feature.DES,
                            existing_height_m=b.ALT_EDIFIC))
    target=ROOT / "data/roof_reference_sample.geojson"
    # The sample remains LOCAL, outside the v1 publication allowlist.
    original=json.loads((ROOT / "_raw/roofs/arpa-pilot-sample.geojson").read_text(encoding="utf-8"))
    original["source_note"]="ARPA Piemonte Edifici 3D 2017; Torino eaves heights from DB topografico 2015. Height attributes only, not roof planes. Map-service reuse license URL was unavailable; local inspection only."
    target.write_text(json.dumps(original,separators=(",", ":")),encoding="utf-8")
    audit=dict(sample_features=len(sample),height_quality_codes=dict(Counter(sample.DES)),
               matched_existing_footprints_iou_08=len(results),matches=results,
               original_coordinates_have_z=any(len(ring[0])>2 for f in original['features'] for ring in (f['geometry']['coordinates'] if f['geometry']['type']=='Polygon' else [r for p in f['geometry']['coordinates'] for r in p])),
               has_roof_planes=False,datum="Horizontal EPSG:32632 at source, GeoJSON converted to EPSG:4326; absolute vertical datum not verified",
               bounds=[7.6525,45.077,7.6555,45.0795],retrieved="2026-10-22")
    tiles=[]
    index=etree.parse(str(ROOT/'_raw/roofs/mase-lidar-study-index.gml'))
    for feature in index.xpath('//*[local-name()="featureMember"]/*'):
        props={etree.QName(x).localname:x.text for x in feature if etree.QName(x).localname in ['tavola','contratto','directory','data','risoluzion','rilievo']}
        coords=[float(v) for v in feature.xpath('.//*[local-name()="posList"]/text()')[0].split()]
        ring=[[coords[i+1],coords[i]] for i in range(0,len(coords),2)]
        tiles.append(dict(type='Feature',properties=props,geometry=dict(type='Polygon',coordinates=[ring])))
    assert len(tiles)<100, 'Coverage-index request may be truncated'
    (ROOT/'data/lidar_coverage_sample.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=tiles,
        source='MASE Geoportale Nazionale / PST-A, CC BY 4.0; tile index only, not a DSM or roof model'),separators=(',',':')),encoding='utf-8')
    audit['mase_advertised_1m_index_tiles']=len(tiles)
    audit['mase_dsm_pixels_acquired']=False
    (ROOT / "output/qa").mkdir(parents=True,exist_ok=True)
    (ROOT / "output/qa/roof-height-audit.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
    evidence=dict(as_of="2026-10-22",audit={k:v for k,v in audit.items() if k!='matches'},
      summary_it="Nessuna copertura LoD2/2.5 verificata nel pilota. Un campione ARPA di 152 geometrie contiene quote in gronda, non falde di tetto. Non si ricavano appartamenti da queste altezze.",
      summary_en=f"No verified LoD2/2.5 coverage in the pilot. An ARPA sample of {len(sample)} footprints contains eaves heights, not roof planes. These heights do not identify apartments.",
      sources=[
        dict(title="MASE / PST-A · LiDAR 1 m",url="https://gn.mase.gov.it/portale/distribuzione-dati-pst",
          status_it="8 tavole indicizzate · raster non acquisito",status_en="8 indexed tiles · raster not acquired",
          finding_it="Il WFS nazionale restituisce 8 tavole da 1 m nel riquadro pilota (Contratto 140; data originale 080623, formato non confermato). Licenza CC BY 4.0. Il servizio download configurato dal viewer restituisce HTTP 404. Copertura dei pixel, datum verticale e falde non verificati.",
          finding_en="The national WFS returns 8 advertised 1 m tiles in the pilot rectangle (Contract 140; raw date 080623, format unconfirmed). CC BY 4.0. The viewer-configured download service returns HTTP 404. Valid-pixel coverage, vertical datum and roof planes remain unverified."),
        dict(title="ARPA · Edifici 3D 2017",url="https://www.geoportale.piemonte.it/geonetwork/srv/api/records/arlpa_to:EDIF_2017-12-21-11:00",
          status_it="Campione reale acquisito · solo altezze",status_en="Real sample acquired · heights only",
          finding_it=f"{len(sample)} geometrie interrogate; {len(results)} corrispondenze con impronte esistenti a IoU ≥ 0,8. Codice DES To; fonte Torino 2015. Licenza del map-service non recuperabile: campione solo locale.",
          finding_en=f"{len(sample)} queried footprints; {len(results)} existing-footprint matches at IoU ≥ 0.8. DES code To; Torino 2015 source. Map-service license unavailable: sample remains local."),
        dict(title="LINKS · Turin3D (2022 survey)",url="https://huggingface.co/datasets/links-ads/Turin3D",
          status_it="Fuori dal pilota · San Salvario",status_en="Outside pilot · San Salvario",
          finding_it="Il lavoro originale (arXiv:2504.05882, §3.3) localizza i 57 blocchi a San Salvario, non a San Donato. LiDAR aereo reale, ma nessun LoD2 pronto per questo pilota.",
          finding_en="The original paper (arXiv:2504.05882, §3.3) locates its 57 blocks in San Salvario, not San Donato. Real aerial LiDAR, but no ready LoD2 for this pilot."),
        dict(title="Piemonte · DSM ICE 2009–2011",url="https://www.geoportale.piemonte.it/geonetwork/srv/api/records/r_piemon:12a0bdd2-166a-4825-8645-1a4605b70f48",
          status_it="Metadati verificati · griglia 5 m",status_en="Metadata verified · 5 m grid",
          finding_it="Licenza CC BY 4.0 nei metadati. Nessun raster scaricabile recuperato da questa scheda. Risoluzione insufficiente per piccoli ostacoli e abbaini; non importato come tetto dettagliato.",
          finding_en="Metadata specifies CC BY 4.0. No downloadable raster was recovered from this record. Too coarse for small obstructions and dormers; not imported as detailed roofs."),
        dict(title="Torino · nuovo DB Geotopografico",url="http://geoportale.comune.torino.it/web/node/3280",
          status_it="Portale non raggiungibile",status_en="Portal unreachable",
          finding_it="La pagina indicizzata annuncia dati aperti. Il portale municipale non è raggiungibile durante la verifica; geometrie, copertura e datum dei prodotti non sono stati verificati.",
          finding_en="The indexed page announces open data. The municipal portal was unreachable during verification; product geometry, coverage and datum remain unverified.")])
    (ROOT / "data/roof_evidence.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in audit.items() if k!='matches'},ensure_ascii=False))


if __name__=="__main__":main()
