"""Curated, page-checked municipal observations; no owners or tenants extracted."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import fitz

ROOT=Path(__file__).resolve().parents[1]


def main():
    specs=[
        dict(id='torino-concessions-2022-digione-113',file='deliberazione_gc_2022_741_all_2_elenco_beni_destinati.pdf',
             source='https://risorse.comune.torino.it/comuneaffitta/bm~doc/deliberazione_gc_2022_741_all_2_elenco_beni_destinati.pdf',
             page=2,document_year=2022,parcels=['1175/643'],members=[['L219','','1175','643','113']],
             address='VIA DIGIONE 3',floor_reported='T',area_reported_m2=None,
             claims_it='Il documento riporta il subalterno 113 a via Digione 3: un locale al piano terra, già portineria, con cantina pertinenziale.',
             claims_en='The document reports subalterno 113 at Via Digione 3: ground-floor former porter premises with an associated cellar.',
             access_support='address_only',courtyard_support=False),
        dict(id='torino-disposals-2023-digione-114',file='DEL-685-2023-All_6-29545_2023_06.pdf',
             source='https://risorse.comune.torino.it/bilancio/pdf/2023/DEL-685-2023-All_6-29545_2023_06.pdf',
             page=13,document_year=2023,parcels=['1175/643'],members=[['L219','','1175','643','114']],
             address='VIA DIGIONE 3',floor_reported='T',area_reported_m2=20,area_kind='approximate_premises_area',
             claims_it='Il documento riporta il subalterno 114 a via Digione 3: circa 20 m² al piano terra, accesso diretto dall’androne carraio e un servizio comune nel cortile.',
             claims_en='The document reports subalterno 114 at Via Digione 3: approximately 20 m² on the ground floor, access from the vehicle entrance hall and a shared courtyard facility.',
             access_support='historical_access_description',courtyard_support=True),
        dict(id='torino-2019-buon-pastore-complex',file='16_2019_all_25_lotto21_schedatecnicopatrimoniale_principeeugenio.pdf',
             source='https://risorse.comune.torino.it/comunevende/bm~doc/16_2019_all_25_lotto21_schedatecnicopatrimoniale_principeeugenio.pdf',
             page=1,cadastral_page=7,document_year=2019,parcels=['1180/229','1180/232','1180/235','1180/255','1180/259','1180/448'],
             members=[],address='CORSO PRINCIPE EUGENIO 18 / VIA MORIS 9',floor_reported=None,area_reported_m2=None,
             claims_it='Il complesso del Buon Pastore è descritto con una corte centrale e accessi da strade diverse. I riferimenti catastali interessano porzioni graffate e aggiornamenti in corso nel 2019.',
             claims_en='The Buon Pastore complex is described with a central courtyard and access from different streets. Its cadastral references concern linked portions and changes pending in 2019.',
             access_support='historical_complex_description',courtyard_support=True,outside_loaded_parcels=True)]
    concession='https://risorse.comune.torino.it/comuneaffitta/bm~doc/deliberazione_gc_2022_741_all_2_elenco_beni_destinati.pdf'
    disposal='https://risorse.comune.torino.it/bilancio/pdf/2023/DEL-685-2023-All_6-29545_2023_06.pdf'
    specs.extend([
        dict(id='torino-2022-francia-73',source=concession,page=1,document_year=2022,parcels=['1223/9'],
            members=[['L219','','1223','9','2']],address='CORSO FRANCIA 73',floor_reported=None,area_reported_m2=1670,
            area_kind='approximate_whole_premises_area',object_scope='former_school',
            claims_it='Ex scuola identificata come subalterno 2, descritta con quattro piani fuori terra e circa 1.670 m² complessivi. Non è una superficie di appartamento.',
            claims_en='Former school identified as subalterno 2, described with four above-ground floors and about 1,670 m² overall. This is not an apartment area.',access_support='address_only',courtyard_support=False),
        dict(id='torino-2022-fabrizi-55',source=concession,page=3,document_year=2022,parcels=['1173/331'],
            members=[['L219','','1173','331','2']],address='VIA NICOLA FABRIZI 55',floor_reported='T',area_reported_m2=None,
            claims_it='Il subalterno 2 è descritto come locali al piano terra, con due vani e servizi esterni, in un edificio abitativo.',
            claims_en='Subalterno 2 is described as ground-floor premises with two rooms and external facilities in a residential building.',access_support='address_only',courtyard_support=False),
        dict(id='torino-2023-regina-220-land',source=disposal,page=8,document_year=2023,parcels=['1179/415'],
            members=[['L219','','1179','415','']],cadastre='CT',object_scope='land_parcel',address='CORSO REGINA MARGHERITA 220',floor_reported=None,area_reported_m2=347,area_kind='cadastral_land_area',
            claims_it='Terreno identificato al Catasto Terreni, superficie catastale 347 m². Non identifica un appartamento né un subalterno urbano.',
            claims_en='Land recorded in the land cadastre, with cadastral area 347 m². It does not identify an apartment or an urban subalterno.',access_support='address_only',courtyard_support=False),
        dict(id='torino-2023-beaumont-22',source=disposal,page=12,document_year=2023,parcels=['1221/149'],
            members=[['L219','','1221','149','2']],address='VIA BEAUMONT 22',floor_reported='T',area_reported_m2=53,area_kind='cadastral_premises_area',cadastral_update_pending=True,
            claims_it='Locale ex portineria al piano terra, subalterno 2, superficie catastale 53 m². Il documento segnala un aggiornamento catastale da effettuare.',
            claims_en='Ground-floor former porter premises, subalterno 2, cadastral area 53 m². The document explicitly reports a cadastral update still to be made.',access_support='address_only',courtyard_support=False),
        dict(id='torino-2023-borsellino-right-of-way',source=disposal,page=24,document_year=2023,parcels=['1222/476'],
            members=[['L219','','1222','476','']],cadastre='CT',object_scope='servitude_on_part_of_parcel',address='VIA BORSELLINO 16',floor_reported=None,area_reported_m2=260,area_kind='approximate_servitude_portion_area',
            claims_it='Il documento descrive una servitù di passaggio pedonale e carraio su parte del terreno: circa 260 m². Non è un’unità immobiliare o un percorso rilevato.',
            claims_en='The document describes a pedestrian and vehicle right of way over part of the land: about 260 m². This is neither a property unit nor a surveyed route.',access_support='historical_right_of_way_description',courtyard_support=False),
        dict(id='torino-2023-racconigi-market',source=disposal,page=25,document_year=2023,parcels=['1224/562','1224/546'],
            members=[['L219','','1224','562',str(sub)] for sub in [1,2,3,8,9,10,11,12,17,18,21,28,29,32,33,34,35,36,37,38,39,40,41,44,45,46,47,48,49,50,51]]+[['L219','','1224','546','42']],
            address='CORSO RACCONIGI',floor_reported=None,area_reported_m2=None,object_scope='multi_property_market_concession',
            claims_it='Una concessione del mercato coperto elenca 31 subalterni sulla particella 562 e il subalterno 42 sulla particella 546 per il parcheggio. Non sono appartamenti.',
            claims_en='One covered-market concession lists 31 subalterni on parcel 562 and subalterno 42 on parcel 546 for parking. These are not apartments.',access_support='no_numbered_entrance_reported',courtyard_support=False)
    ])
    output=[]
    for spec in specs:
        spec.setdefault('file',spec['source'].split('/')[-1])
        path=ROOT/'_raw/documents'/spec['file'];document=fitz.open(path)
        text=document[spec['page']-1].get_text()
        if spec['members']:
            assert all(m[2] in text and m[3] in text and (not m[4] or m[4] in text) for m in spec['members'])
        output.append(dict(spec,provider='Città di Torino',source_lineage='municipal_property_documents',
            inspected=datetime.now(timezone.utc).isoformat(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            status='historical_source_report',current_validity='unknown',date_precision='year',
            raw_document_published=False,legal_confirmation=False))
    path=ROOT/'output/investigation/document-observations.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'Prepared {len(output)} page-checked municipal observations. No identities merged; land, servitudes and grouped market references retain their scope.')


if __name__=='__main__':main()
