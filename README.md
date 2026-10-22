# Unità San Donato

Mappa web dei lotti catastali di San Donato e Campidoglio (Torino) con edifici, numeri civici e famiglie stimate per lotto. Serve come base per collegare i subalterni delle visure catastali e i codici POD a ogni ingresso.

## Avvio in locale

Serve un server HTTP, perché la pagina carica i dati da `data/`. Aprire `index.html` come file non funziona.

```
py -m http.server 8765 --bind 127.0.0.1
```

oppure doppio clic su `serve.bat` (Windows), poi apri http://localhost:8765.

Per pubblicarla su GitHub Pages basta attivare Pages sul branch principale, cartella radice. Il file `.nojekyll` è già presente.

## Cosa c'è nella mappa

- Lotti catastali colorati per famiglie stimate, piani, ingressi o affidabilità, con filtro e trasparenza.
- Edifici principali della Carta Tecnica, ingressi civici (con lettere, scale e interni), sezioni di censimento.
- Etichette di particelle (da zoom 18,5) e civici (da 19,5).
- Ricerca per indirizzo o per foglio/particella (`1175/434`).
- Scheda del lotto con riferimento SISTER da copiare, righe del modulo POD, link diretto (`#lotto-1175-434`) e download del lotto.
- Selezione per poligono o per vista corrente, con riepilogo e download ZIP (GeoJSON e CSV).
- Elenco dei lotti nella vista ordinati per famiglie stimate, per decidere le visure.
- Mappe di base Esri (grigio chiaro, grigio scuro, ortofoto).
- Tasti: `/` per cercare, `D` per disegnare un'area, `Esc` per annullare.

## Dati

| File | Contenuto |
|---|---|
| `data/*.json` | Livelli per la mappa, coordinate in interi delta a 1e-6 gradi (circa 0,1 m) |
| `data/download/torino_sandonato_dati.zip` | GeoPackage completo (EPSG:32632) e CSV |

Fonti: cartografia catastale dell'Agenzia delle Entrate (WFS INSPIRE, CC BY 4.0); Carta Tecnica, numerazione civica e sezioni di censimento della Città di Torino (CC BY 4.0). Elaborazione del 22 ottobre 2026.

## Metodo

1. Le particelle vengono scaricate dal WFS dell'Agenzia delle Entrate a riquadri (il servizio non risponde su aree grandi) e unite per riferimento.
2. Gli edifici della Carta Tecnica (EPSG:3003) sono riproiettati in EPSG:32632 e traslati di −1,1 m est e +1,0 m nord. La traslazione è stimata cercando lo spostamento che minimizza l'area di 1.500 edifici sulle particelle stradali (dal 3,8% allo 0,95%). I civici sono già nel sistema catastale e non vengono spostati.
3. Ogni ingresso viene assegnato al lotto che lo contiene o al più vicino entro 25 m (i punti stanno sulla linea di facciata), poi all'edificio più vicino sullo stesso lotto.
4. Le famiglie di ogni sezione di censimento sono ripartite tra gli edifici residenziali in proporzione alla superficie lorda (impronta × piani). Correlazione tra superficie e famiglie per sezione: r = 0,81.
5. Le sezioni con meno di 40 o più di 250 m² per famiglia sono segnate ad affidabilità bassa.

Le famiglie stimate non sono unità catastali: mancano le abitazioni vuote e la ripartizione dipende dai piani della Carta Tecnica. I subalterni reali vengono dalle visure SISTER (Catasto Fabbricati, foglio e particella).

## Script

In `scripts/`, da eseguire in ordine:

1. `fetch_parcels.py` scarica le particelle a riquadri.
2. `analysis.py` unisce particelle, edifici, civici e sezioni e produce il GeoPackage.
3. `build_web.py` genera i file in `data/`.

Requisiti: Python 3.11 o successivo, geopandas, shapely, pyproj, lxml.
