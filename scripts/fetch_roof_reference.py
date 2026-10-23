"""Cache small, publicly queryable height and LiDAR-index samples, not roof solids."""
import json
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'_raw/roofs'
ARPA='https://webgis.arpa.piemonte.it/ags/rest/services/topografia_dati_di_base/Edifici_3D_2017/MapServer/0/query'
MASE='https://wms.pcn.minambiente.it/ogc'


def main():
    RAW.mkdir(parents=True,exist_ok=True)
    if not (RAW/'arpa-pilot-sample.geojson').exists():
        p=dict(f='geojson',where='1=1',geometry='7.6525,45.077,7.6555,45.0795',geometryType='esriGeometryEnvelope',
               inSR=4326,outSR=4326,spatialRel='esriSpatialRelIntersects',outFields='OBJECTID,UUID,ELEV,DES,USO,USO_DESC',
               returnGeometry='true',resultRecordCount=500)
        r=requests.get(ARPA,params=p,timeout=40);r.raise_for_status();data=r.json()
        assert data.get('type')=='FeatureCollection' and not data.get('exceededTransferLimit')
        (RAW/'arpa-pilot-sample.geojson').write_text(json.dumps(data),encoding='utf-8')
    path=RAW/'mase-lidar-study-index.gml'
    if not path.exists():
        # WFS advertises only EPSG:4326: WFS 1.1 axis order is latitude, longitude.
        p=dict(map='/ms_ogc/wfs/QU_Lidar.map',service='WFS',request='GetFeature',version='1.1.0',
               typename='EL.QUADRO.UNIONE.LIDAR.0101',bbox='45.070,7.640,45.086,7.668,urn:ogc:def:crs:EPSG::4326',
               srsName='urn:ogc:def:crs:EPSG::4326',maxFeatures=100)
        r=requests.get(MASE,params=p,timeout=40);r.raise_for_status()
        if b'ExceptionReport' in r.content:raise ValueError('MASE coverage query failed')
        path.write_bytes(r.content)
        (RAW/'mase-study-query.json').write_text(json.dumps(dict(url=r.url,retrieved='2026-10-22',
            license='CC BY 4.0',license_source='https://gn.mase.gov.it/portale/distribuzione-dati-pst',
            semantics='Tile index geometry is not a guarantee of valid DSM pixels or roof-plane geometry')),encoding='utf-8')
    print('Cached ARPA height sample and MASE 1 m tile index for the pilot.')


if __name__=='__main__':main()
