"use strict";
/* Unità San Donato: Leaflet + canvas. One renderer per pane, created once. */

const $ = (id) => document.getElementById(id);
const fmt = (v, d = 0) => (v == null || Number.isNaN(+v)) ? "–" : Number(v).toLocaleString(document.documentElement.lang === "en" ? "en-GB" : "it-IT", { maximumFractionDigits: d, minimumFractionDigits: d });
const norm = (s) => (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9/ ]/g, " ").replace(/\s+/g, " ").trim();
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* ---------- colours ---------- */
const C = {};
const isDark = () => {
  const t = document.documentElement.getAttribute("data-theme");
  return t ? t === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
};
function readColors() {
  const cs = getComputedStyle(document.documentElement);
  ["--brand", "--fg1", "--text1", "--text3", "--success", "--warning-fill", "--danger", "--map-bg", "--road", "--road-line", "--lot-line", "--bld-line", "--halo"]
    .forEach((k) => { C[k] = cs.getPropertyValue(k).trim(); });
  C.nodata = isDark() ? "#3a3a3a" : "#f5f5f5";
}
readColors();

/* ArcGIS / ColorBrewer sequential ramps */
const MODES = {
  fam: {
    title: "Famiglie stimate per lotto", key: "famiglie_stimate",
    hint: "Famiglie del censimento ripartite per superficie residenziale. Stima, non unità catastali.",
    ramp: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
    cls: [[0.5, 5, "1–5"], [5.5, 15, "6–15"], [15.5, 40, "16–40"], [40.5, 100, "41–100"], [100.5, 1e9, "oltre 100"]], none: "0 o non residenziale",
  },
  piani: {
    title: "Edificio più alto (piani)", key: "livelli_max",
    hint: "Piani fuori terra dalla Carta Tecnica; «5+1» conta come 6, «5+s» come 5,5.",
    ramp: ["#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"],
    cls: [[0, 2, "1–2"], [2.1, 4, "3–4"], [4.1, 6, "5–6"], [6.1, 8, "7–8"], [8.1, 99, "9 e oltre"]], none: "nessun edificio principale",
  },
  ingr: {
    title: "Ingressi civici per lotto", key: "n_ingressi",
    hint: "Numeri civici (con lettere, scale e interni) assegnati al lotto.",
    ramp: ["#ccece6", "#99d8c9", "#66c2a4", "#2ca25f", "#006d2c"],
    cls: [[1, 1, "1"], [2, 3, "2–3"], [4, 8, "4–8"], [9, 20, "9–20"], [21, 9999, "oltre 20"]], none: "nessuno",
  },
  aff: {
    title: "Affidabilità della stima", key: "affidabilita",
    hint: "Bassa dove la sezione ha meno di 40 o più di 250 m² di superficie per famiglia.",
  },
};
let mode = "fam";
let fMin = 0, fLow = false, lotOpacity = 0.85;

function lotColor(p) {
  if (mode === "aff") return !(p.sul_res_m2 > 0) ? C.nodata : (p.affidabilita === "bassa" ? C["--warning-fill"] : C["--success"]);
  const m = MODES[mode], v = p[m.key];
  if (v == null) return C.nodata;
  for (let i = 0; i < m.cls.length; i++) if (v >= m.cls[i][0] && v <= m.cls[i][1]) return m.ramp[i];
  return C.nodata;
}
const passes = (p) => (p.famiglie_stimate || 0) >= fMin && (!fLow || (p.sul_res_m2 > 0 && p.affidabilita === "bassa"));
function lotStyle(p) {
  const on = passes(p);
  return { color: C["--lot-line"], weight: 0.6, opacity: on ? 1 : 0.35, fillColor: lotColor(p), fillOpacity: on ? lotOpacity : 0.06 };
}
const bldStyle = (p) => ({ color: C["--bld-line"], weight: 0.8, opacity: 0.8, fillColor: C["--bld-line"], fillOpacity: (p.CAT_USO || "").startsWith("residenziale") ? 0.04 : 0.14 });
const roadStyle = () => ({ color: C["--road-line"], weight: 0.5, fillColor: C["--road"], fillOpacity: 1 });
const sezStyle = () => ({ color: C["--danger"], weight: 1.3, dashArray: "5 4", fill: false });
const entStyle = () => ({ radius: 3.6, weight: 1.2, color: C["--fg1"], fillColor: C["--brand"], fillOpacity: 1 });

/* ---------- map ---------- */
const map = L.map("map", { zoomSnap: 0.5, minZoom: 13, maxZoom: 21, zoomControl: false });
L.control.zoom({ position: "topright", zoomInTitle: "Ingrandisci", zoomOutTitle: "Riduci" }).addTo(map);
L.control.scale({ imperial: false, position: "bottomright" }).addTo(map);
map.attributionControl.setPrefix(false).addAttribution("Catasto © Agenzia delle Entrate · Carta Tecnica, civici, sezioni © Città di Torino · CC BY 4.0");
const R = {};
[["base", 200], ["sez", 380], ["roads", 390], ["lots", 400], ["bld", 410], ["sel", 420], ["ent", 430], ["draw", 440]].forEach(([n, z]) => {
  map.createPane(n).style.zIndex = z;
  if (n !== "base") R[n] = L.canvas({ pane: n, padding: 0.2, tolerance: 5 });
});
map.setView([45.0778, 7.6542], 18);

/* ---------- basemaps ---------- */
const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/";
const BASES = {
  gray: { url: ESRI + "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", max: 16, attr: "Basemap © Esri, HERE, Garmin, © contributori OpenStreetMap" },
  dark: { url: ESRI + "Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", max: 16, attr: "Basemap © Esri, HERE, Garmin, © contributori OpenStreetMap" },
  img: { url: ESRI + "World_Imagery/MapServer/tile/{z}/{y}/{x}", max: 19, attr: "Ortofoto © Esri, Maxar, Earthstar Geographics" },
};
let base = "none", baseLayer = null;
function setBase(name) {
  if (baseLayer) { map.removeLayer(baseLayer); baseLayer = null; }
  base = name;
  if (name !== "none") {
    const b = BASES[name];
    let errors = 0, loaded = 0;
    baseLayer = L.tileLayer(b.url, { pane: "base", maxNativeZoom: b.max, maxZoom: 21, attribution: b.attr });
    baseLayer.on("tileload", () => { loaded++; });
    baseLayer.on("tileerror", () => {
      if (++errors > 6 && loaded === 0) {
        setBase("none");
        $("baseNote").hidden = false;
        $("baseNote").textContent = "La mappa di base Esri non risponde. Controlla la connessione; il catasto resta visibile.";
      }
    });
    baseLayer.addTo(map);
  }
  document.querySelectorAll("#basemaps button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.base === base)));
  if (name === "img" && lotOpacity > 0.5) setOpacity(0.45);
  else if (name !== "img" && lotOpacity === 0.45) setOpacity(0.85);
  syncLayers();
}
$("basemaps").addEventListener("click", (e) => { const b = e.target.closest("button[data-base]"); if (b && !b.disabled) setBase(b.dataset.base); });

/* ---------- data decoding (delta ints at 1e-6 deg) ---------- */
let META;
function ring(a) {
  const out = new Array(a.length / 2);
  let x = 0, y = 0;
  for (let i = 0, j = 0; i < a.length; i += 2, j++) { x += a[i]; y += a[i + 1]; out[j] = [META.lat0 + y / META.q, META.lon0 + x / META.q]; }
  return out;
}
const polyLL = (g) => g.map((p) => p.map(ring));
const pointLL = (g) => [META.lat0 + g[1] / META.q, META.lon0 + g[0] / META.q];
function rows(d) {
  const keys = Object.keys(d.p), out = new Array(d.n);
  for (let i = 0; i < d.n; i++) { const o = {}; for (const k of keys) o[k] = d.p[k][i]; out[i] = o; }
  return out;
}
const get = (f) => fetch(`data/${f}.json`).then((r) => { if (!r.ok) throw new Error(`data/${f}.json: HTTP ${r.status}`); return r.json(); });

/* ---------- state ---------- */
const G = { roads: L.layerGroup(), lots: L.layerGroup(), bld: L.layerGroup(), ent: L.layerGroup(), sez: L.layerGroup(), lbl: L.layerGroup(), sel: L.layerGroup(), area: L.layerGroup() };
G.sel.addTo(map); G.area.addTo(map);
const LOTS = [], BLD = [], ENTS = [], SEZ = [], ROADS = [];
const lotByFp = new Map(), entById = new Map(), entsByFp = new Map(), bldByFp = new Map();
let selected = null, selEnt = null, CENSUS = 0;

/* ---------- layer visibility ---------- */
const want = { lots: true, bld: true, ent: true, sez: false, lbl: true };
const Z = { bld: 15.5, ent: 16.5, lblLot: 18.5, lblEnt: 19.5 };
function syncLayers() {
  const z = map.getZoom();
  [[G.roads, base === "none"], [G.lots, want.lots], [G.bld, want.bld && z >= Z.bld], [G.sez, want.sez], [G.ent, want.ent && z >= Z.ent]].forEach(([l, on]) => {
    if (on && !map.hasLayer(l)) l.addTo(map); if (!on && map.hasLayer(l)) map.removeLayer(l);
  });
  refreshLabels();
}
[["L-lots", "lots"], ["L-bld", "bld"], ["L-ent", "ent"], ["L-sez", "sez"], ["L-lbl", "lbl"]].forEach(([id, k]) => {
  const el = $(id); el.addEventListener("change", () => { want[k] = el.checked; syncLayers(); });
});

/* labels only for what is on screen */
function refreshLabels() {
  G.lbl.clearLayers();
  const z = map.getZoom();
  if (!want.lbl || z < Z.lblLot) { if (map.hasLayer(G.lbl)) map.removeLayer(G.lbl); return; }
  const b = map.getBounds().pad(0.05);
  let n = 0;
  if (want.lots) for (const o of LOTS) {
    if (n > 500) break;
    if (!o.c || !b.contains(o.c)) continue;
    G.lbl.addLayer(L.tooltip({ permanent: true, direction: "center", className: "lbl", interactive: false }).setLatLng(o.c).setContent(o.p.particella));
    n++;
  }
  if (want.ent && z >= Z.lblEnt) for (const o of ENTS) {
    if (n > 1000) break;
    const ll = o.layer.getLatLng(); if (!b.contains(ll)) continue;
    G.lbl.addLayer(L.tooltip({ permanent: true, direction: "right", offset: [5, 0], className: "lbl civ", interactive: false }).setLatLng(ll).setContent(esc(o.p.CIVICO)));
    n++;
  }
  if (!map.hasLayer(G.lbl)) G.lbl.addTo(map);
}

/* ---------- legend ---------- */
function renderLegend() {
  const m = MODES[mode];
  let h = `<b>${m.title}</b>`;
  if (mode === "aff") {
    h += `<div><i style="background:${C["--success"]}"></i>Normale</div><div><i style="background:${C["--warning-fill"]}"></i>Bassa</div><div><i style="background:${C.nodata}"></i>Nessuna residenza</div>`;
  } else {
    h += m.cls.map(([, , lab], i) => `<div><i style="background:${m.ramp[i]}"></i>${lab}</div>`).join("");
    h += `<div><i style="background:${C.nodata}"></i>${m.none}</div>`;
  }
  if (want.ent) h += `<div><span class="pt" style="background:${C["--brand"]}"></span>Ingresso civico</div>`;
  $("legend").innerHTML = h;
  $("modeHint").textContent = m.hint;
}
function restyleLots() { for (const o of LOTS) o.layer.setStyle(lotStyle(o.p)); countFilter(); }
function countFilter() {
  const n = LOTS.reduce((s, o) => s + (passes(o.p) ? 1 : 0), 0);
  $("fCount").textContent = (fMin > 0 || fLow) ? `${fmt(n)} lotti su ${fmt(LOTS.length)} rispettano il filtro.` : "";
}
$("modes").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-mode]"); if (!b) return;
  mode = b.dataset.mode;
  document.querySelectorAll("#modes button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
  restyleLots(); renderLegend();
});
let fTimer;
$("fMin").addEventListener("input", (e) => { fMin = +e.target.value; $("fMinV").textContent = fMin; clearTimeout(fTimer); fTimer = setTimeout(restyleLots, 60); });
$("fLow").addEventListener("change", (e) => { fLow = e.target.checked; restyleLots(); });
function setOpacity(v) { lotOpacity = v; $("op").value = Math.round(v * 100); $("opV").textContent = Math.round(v * 100) + "%"; restyleLots(); }
$("op").addEventListener("input", (e) => setOpacity(+e.target.value / 100));

/* ---------- panel / action bar ---------- */
const TITLES = { dettagli: "Dettagli lotto", simbologia: "Simbologia e filtri", livelli: "Livelli", base: "Mappa di base", area: "Selezione per area", priorita: "Priorità visure", scarica: "Scarica dati", metodo: "Area di studio e metodo" };
let panel = "dettagli";
function openPanel(name, toggle) {
  const p = $("panel");
  if (toggle && panel === name && !p.hidden) { p.hidden = true; markActions(null); setTimeout(() => map.invalidateSize(), 0); return; }
  if(panel !== name) p.querySelector(".panel-body").scrollTop = 0;
  panel = name; p.hidden = false;
  document.querySelectorAll("[data-view]").forEach((v) => { v.hidden = v.dataset.view !== name; });
  $("panelTitle").textContent = TITLES[name];
  markActions(name);
  if (name === "priorita") renderPrio();
  setTimeout(() => map.invalidateSize(), 0);
}
const markActions = (name) => document.querySelectorAll(".actionbar button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.panel === name)));
document.querySelector(".actionbar").addEventListener("click", (e) => { const b = e.target.closest("button[data-panel]"); if (b) openPanel(b.dataset.panel, true); });
$("panelClose").addEventListener("click", () => { $("panel").hidden = true; markActions(null); setTimeout(() => map.invalidateSize(), 0); });

/* ---------- toast + clipboard ---------- */
let tTimer;
function toast(msg, err) {
  const t = $("toast"); t.textContent = msg; t.classList.toggle("err", !!err); t.hidden = false;
  clearTimeout(tTimer); tTimer = setTimeout(() => { t.hidden = true; }, 2600);
}
function copy(text, okMsg) {
  const fallback = () => {
    const ta = document.createElement("textarea"); ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    let ok = false; try { ok = document.execCommand("copy"); } catch (_) { /* ignore */ }
    ta.remove(); toast(ok ? okMsg : "Copia non riuscita: seleziona il testo a mano.", !ok);
  };
  if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(() => toast(okMsg), fallback);
  else fallback();
}

/* ---------- selection + details ---------- */
let hiLot = null, hiEnt = null;
function selectLot(fp, entId, opts = {}) {
  const o = lotByFp.get(fp); if (!o) return;
  selected = fp; selEnt = entId || null;
  G.sel.clearLayers();
  const ll = o.layer.getLatLngs();
  G.sel.addLayer(L.polygon(ll, { pane: "sel", renderer: R.sel, interactive: false, color: C["--halo"], weight: 7, opacity: 0.35, fill: false }));
  G.sel.addLayer(L.polygon(ll, { pane: "sel", renderer: R.sel, interactive: false, color: C["--halo"], weight: 2.2, fill: false }));
  const e = entId && entById.get(entId);
  if (e) G.sel.addLayer(L.circleMarker(e.layer.getLatLng(), { pane: "sel", renderer: R.sel, radius: 9, weight: 2.5, color: C["--halo"], fill: false, interactive: false }));
  renderDetails(o, entId);
  document.dispatchEvent(new CustomEvent("lotselected", { detail: { fp, entId } }));
  if (opts.fit) map.fitBounds(o.layer.getBounds(), { maxZoom: 19.5, padding: [40, 40] });
  try { history.replaceState(null, "", "#lotto-" + fp.replace("/", "-")); } catch (_) { /* file:// */ }
  if (opts.open !== false) openPanel("dettagli");
}
function chip(p) {
  if (!(p.sul_res_m2 > 0)) return `<span class="chip"><i style="background:${C.nodata};outline:1px solid var(--border)"></i>Nessuna residenza</span>`;
  return p.affidabilita === "bassa"
    ? `<span class="chip"><i style="background:${C["--warning-fill"]}"></i>Affidabilità bassa</span>`
    : `<span class="chip"><i style="background:${C["--success"]}"></i>Affidabilità normale</span>`;
}
const entsOf = (fp) => (entsByFp.get(fp) || []).slice().sort((a, b) => a.p.indirizzo.localeCompare(b.p.indirizzo, "it", { numeric: true }));
const sisterQuery = (p) => `Catasto Fabbricati · Torino (L219) · foglio ${p.foglio} · particella ${p.particella}`;
function entranceEvidenceRows(list) {
  const head = ["indirizzo", "cod_civico", "foglio", "particella", "famiglie_stimate_ingresso", "fonte"];
  return [head.join("\t")].concat(list.map((o) => {
    const [fg, pt] = (o.p.fp || "/").split("/");
    return [o.p.indirizzo, o.p.COD_CIVICO, fg, pt, o.p.famiglie_per_ingresso ?? "", "GIS pubblico / public GIS"].join("\t");
  })).join("\n");
}
function renderDetails(o, entId) {
  const p = o.p, list = entsOf(p.foglio_particella);
  $("detEmpty").hidden = true;
  const d = $("det"); d.hidden = false;
  d.innerHTML = `
    <div class="block">
      <div class="lotref"><span class="fp">${esc(p.foglio_particella)}</span><small>foglio / particella</small></div>
      <div>${chip(p)}</div>
      <div class="kpis">
        <div><b>${fmt(p.famiglie_stimate)}</b><span>famiglie stimate</span></div>
        <div><b>${fmt(p.n_edifici)}</b><span>edifici</span></div>
        <div><b>${fmt(list.length)}</b><span>ingressi</span></div>
      </div>
      <dl class="kv">
        <dt>Superficie residenziale</dt><dd class="num">${fmt(p.sul_res_m2)} m²</dd>
        <dt>Edificio più alto</dt><dd>${p.livelli_max == null ? "–" : fmt(p.livelli_max, p.livelli_max % 1 ? 1 : 0) + " piani"}</dd>
        <dt>Superficie del lotto</dt><dd class="num">${fmt(p.area_m2)} m²</dd>
        <dt>Uso prevalente</dt><dd>${esc(p.uso_prevalente || "–")}</dd>
        <dt>Epoca di costruzione</dt><dd>${esc(p.epoca || "–")}</dd>
        <dt>Riferimento INSPIRE</dt><dd class="num">${esc(p.ref)}</dd>
      </dl>
    </div>
    <div class="block">
      <h3>Visura SISTER</h3>
      <div class="copyrow"><code>${esc(sisterQuery(p))}</code><button class="btn outline sm" type="button" id="cpSister">Copia</button></div>
      <div class="actions">
        <button class="btn outline sm" type="button" id="cpEvidence" ${list.length ? "" : "disabled"}>Copia evidenze ingressi</button>
        <button class="btn outline sm" type="button" id="cpLink">Copia link</button>
        <button class="btn outline sm" type="button" id="dlLot">Scarica lotto</button>
        <button class="btn ghost sm" type="button" id="zLot">Zoom al lotto</button>
      </div>
    </div>
    <div class="block" style="padding-bottom:4px"><h3>Ingressi (${list.length})</h3>
      ${list.length ? "" : `<p class="hint">Nessun numero civico su questo lotto.</p>`}
    </div>
    ${list.length ? `<ul class="list" id="entList">${list.map((e) => `<li><button type="button" data-ent="${e.id}" class="${e.id === entId ? "on" : ""}"><span>${esc(e.p.indirizzo)}</span><small>${e.p.famiglie_per_ingresso == null ? "" : "≈ " + fmt(e.p.famiglie_per_ingresso, 1) + " fam."}</small></button></li>`).join("")}</ul>` : ""}`;
  $("cpSister").onclick = () => copy(sisterQuery(p), "Riferimento SISTER copiato");
  if (list.length) $("cpEvidence").onclick = () => copy(entranceEvidenceRows(list), `${list.length} righe copiate: incollale in Excel o Fogli`);
  $("cpLink").onclick = () => copy(location.href.split("#")[0] + "#lotto-" + p.foglio_particella.replace("/", "-"), "Link al lotto copiato");
  $("dlLot").onclick = () => exportSet(`lotto_${p.foglio_particella.replace("/", "_")}`, { lots: [o], bld: bldByFp.get(p.foglio_particella) || [], ents: list });
  $("zLot").onclick = () => map.fitBounds(o.layer.getBounds(), { maxZoom: 19.5, padding: [40, 40] });
  const el = $("entList");
  if (el) el.addEventListener("click", (ev) => {
    const b = ev.target.closest("button[data-ent]"); if (!b) return;
    const e = entById.get(b.dataset.ent); if (!e) return;
    map.setView(e.layer.getLatLng(), Math.max(map.getZoom(), 19.5)); selectLot(p.foglio_particella, b.dataset.ent);
  });
}

/* ---------- search ---------- */
let IDX = [], hitList = [], hitPos = 0;
const qEl = $("q"), res = $("results");
function doSearch() {
  const raw = qEl.value.trim(), t = norm(raw);
  hitList = []; hitPos = 0;
  if (t.length < 2) { res.hidden = true; return; }
  const fpm = raw.match(/^(\d{3,4})\s*[\/\-\s]\s*(\d+)$/);
  if (fpm && lotByFp.has(`${+fpm[1]}/${fpm[2]}`)) hitList.push({ fp: `${+fpm[1]}/${fpm[2]}`, label: `Lotto ${+fpm[1]}/${fpm[2]}`, sub: "foglio/particella" });
  const words = t.split(" ");
  const found = [];
  for (let i = 0; i < IDX.length && found.length < 300; i++) if (words.every((w) => IDX[i].k.includes(w))) found.push(IDX[i]);
  found.sort((a, b) => a.k.localeCompare(b.k, "it", { numeric: true }));
  found.slice(0, 9).forEach((x) => hitList.push({ ent: x.o, label: x.o.p.indirizzo, sub: x.o.p.fp }));
  res.innerHTML = hitList.length
    ? hitList.map((h, i) => `<button type="button" data-i="${i}" class="${i === 0 ? "on" : ""}"><span>${esc(h.label)}</span><small>${esc(h.sub)}</small></button>`).join("")
    : `<p>Nessun indirizzo dell'area di studio corrisponde a «${esc(raw)}».</p>`;
  res.hidden = false;
}
function pick(i) {
  const h = hitList[i]; if (!h) return;
  res.hidden = true;
  if (h.fp) { qEl.value = h.label; selectLot(h.fp, null, { fit: true }); return; }
  qEl.value = h.ent.p.indirizzo;
  map.setView(h.ent.layer.getLatLng(), 19.5);
  if(lotByFp.has(h.ent.p.fp)) selectLot(h.ent.p.fp, h.ent.id);
  else {
    showRawFeature(h.ent.p, typeof tr === "function" ? tr("Ingresso senza lotto", "Entrance without parcel") : "Ingresso senza lotto");
    if(typeof openStreet === "function") openStreet(h.ent);
  }
}
qEl.addEventListener("input", doSearch);
qEl.addEventListener("focus", () => { if (hitList.length) res.hidden = false; });
qEl.addEventListener("keydown", (e) => {
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    if (!hitList.length) return; e.preventDefault();
    hitPos = (hitPos + (e.key === "ArrowDown" ? 1 : -1) + hitList.length) % hitList.length;
    res.querySelectorAll("button").forEach((b, i) => b.classList.toggle("on", i === hitPos));
  } else if (e.key === "Enter") { pick(hitPos); }
  else if (e.key === "Escape") { res.hidden = true; qEl.blur(); }
});
res.addEventListener("click", (e) => { const b = e.target.closest("button[data-i]"); if (b) pick(+b.dataset.i); });
document.addEventListener("click", (e) => { if (!e.target.closest(".search")) res.hidden = true; });

/* ---------- priority list ---------- */
let prioRows = [];
function renderPrio() {
  if (panel !== "priorita" || $("panel").hidden || !LOTS.length) return;
  const b = map.getBounds();
  prioRows = LOTS.filter((o) => o.p.sul_res_m2 > 0 && o.c && b.contains(o.c)).sort((a, z) => z.p.famiglie_stimate - a.p.famiglie_stimate).slice(0, 40);
  $("prio").innerHTML = prioRows.length
    ? prioRows.map((o, i) => `<li><button type="button" data-fp="${esc(o.p.foglio_particella)}"><span>${i + 1}. ${esc(o.p.foglio_particella)} · ${fmt(entsOf(o.p.foglio_particella).length)} ingressi${o.p.affidabilita === "bassa" ? " · bassa" : ""}</span><small>${fmt(o.p.famiglie_stimate)} fam.</small></button></li>`).join("")
    : `<li class="empty">Nessun lotto residenziale nella vista. Allontanati o spostati sulla mappa.</li>`;
}
$("prio").addEventListener("click", (e) => { const b = e.target.closest("button[data-fp]"); if (b) selectLot(b.dataset.fp, null, { fit: true, open: false }); });
$("prioCopy").addEventListener("click", () => {
  if (!prioRows.length) return;
  copy(["foglio\tparticella\tfamiglie_stimate\tingressi\taffidabilita"].concat(prioRows.map((o) => [o.p.foglio, o.p.particella, o.p.famiglie_stimate, entsOf(o.p.foglio_particella).length, o.p.affidabilita || ""].join("\t"))).join("\n"),
    `${prioRows.length} lotti copiati`);
});

/* ---------- drawing an area ---------- */
let drawing = false, pts = [], drawLine = null, drawGhost = null, areaPoly = null, areaSel = null;
function startDraw() {
  if (drawing) return;
  openPanel("area");
  drawing = true; pts = [];
  map.doubleClickZoom.disable();
  map.getContainer().classList.add("drawing");
  $("drawbar").hidden = false; updateDrawbar();
}
function stopDraw() {
  drawing = false; pts = [];
  map.doubleClickZoom.enable();
  map.getContainer().classList.remove("drawing");
  $("drawbar").hidden = true;
  if (drawLine) { map.removeLayer(drawLine); drawLine = null; }
  if (drawGhost) { map.removeLayer(drawGhost); drawGhost = null; }
}
function updateDrawbar() {
  $("drawMsg").textContent = pts.length < 3 ? `Clic per aggiungere vertici (${pts.length}/3 minimo)` : `${pts.length} vertici · doppio clic o «Completa»`;
  $("drawDone").disabled = pts.length < 3; $("drawUndo").disabled = !pts.length;
  if (drawLine) map.removeLayer(drawLine);
  drawLine = pts.length ? L.polygon(pts, { pane: "draw", renderer: R.draw, interactive: false, color: C["--brand"], weight: 2, dashArray: "6 4", fillColor: C["--brand"], fillOpacity: 0.08 }).addTo(map) : null;
}
map.on("click", (e) => { if (drawing) { pts.push(e.latlng); updateDrawbar(); } });
map.on("dblclick", (e) => { if (drawing && pts.length >= 3) { L.DomEvent.stop(e); finishDraw(); } });
map.on("mousemove", (e) => {
  $("coords").textContent = `${e.latlng.lat.toFixed(5)}° N  ${e.latlng.lng.toFixed(5)}° E  ·  z ${map.getZoom()}`;
  if (!drawing || !pts.length) return;
  if (drawGhost) drawGhost.setLatLngs([pts[pts.length - 1], e.latlng, pts[0]]);
  else drawGhost = L.polyline([pts[pts.length - 1], e.latlng, pts[0]], { pane: "draw", renderer: R.draw, interactive: false, color: C["--brand"], weight: 1.5, dashArray: "3 4" }).addTo(map);
});
$("drawDone").onclick = () => finishDraw();
$("drawUndo").onclick = () => { pts.pop(); updateDrawbar(); };
$("drawCancel").onclick = () => stopDraw();
$("drawBtn").onclick = startDraw;
$("drawTop").onclick = startDraw;
$("viewBtn").onclick = () => {
  const b = map.getBounds();
  applyArea([b.getSouthWest(), b.getNorthWest(), b.getNorthEast(), b.getSouthEast()]);
};
$("clearSel").onclick = clearArea;
function finishDraw() {
  // a double click also fires two clicks: drop near-duplicate trailing vertices
  const clean = pts.filter((p, i) => i === 0 || map.latLngToContainerPoint(p).distanceTo(map.latLngToContainerPoint(pts[i - 1])) > 4);
  stopDraw();
  if (clean.length >= 3) applyArea(clean);
}
function clearArea() {
  G.area.clearLayers(); areaPoly = null; areaSel = null;
  $("selOut").innerHTML = ""; $("clearSel").disabled = true;
}
function applyArea(latlngs) {
  G.area.clearLayers();
  const coords = latlngs.map((p) => [p.lng, p.lat]); coords.push(coords[0]);
  let poly = turf.polygon([coords]);
  if (turf.kinks(poly).features.length) { poly = turf.convex(turf.featureCollection(coords.map((c) => turf.point(c)))) || poly; toast("Il poligono si incrociava: uso il suo contorno esterno."); }
  areaPoly = poly;
  const bb = L.latLngBounds(latlngs);
  const lots = LOTS.filter((o) => o.layer.getBounds().intersects(bb) && turf.booleanIntersects(poly, o.layer.toGeoJSON(7)));
  const fpSet = new Set(lots.map((o) => o.p.foglio_particella));
  const bld = BLD.filter((o) => o.layer.getBounds().intersects(bb) && turf.booleanIntersects(poly, o.layer.toGeoJSON(7)));
  const ents = ENTS.filter((o) => { const ll = o.layer.getLatLng(); return bb.contains(ll) && turf.booleanPointInPolygon([ll.lng, ll.lat], poly); });
  areaSel = { lots, bld, ents };
  L.geoJSON(poly, { pane: "draw", renderer: R.draw, interactive: false, style: { color: C["--brand"], weight: 2, dashArray: "6 4", fillColor: C["--brand"], fillOpacity: 0.06 } }).addTo(G.area);
  lots.forEach((o) => G.area.addLayer(L.polygon(o.layer.getLatLngs(), { pane: "sel", renderer: R.sel, interactive: false, color: C["--halo"], weight: 1.4, fill: false })));
  const P = lots.map((o) => o.p);
  const hh = P.reduce((s, p) => s + (p.famiglie_stimate || 0), 0), sul = P.reduce((s, p) => s + (p.sul_res_m2 || 0), 0);
  const low = P.filter((p) => p.sul_res_m2 > 0 && p.affidabilita === "bassa").length;
  const areaM2 = turf.area(poly);
  $("selOut").innerHTML = `
    <div class="block">
      <h3>Contenuto dell'area</h3>
      <div class="kpis">
        <div><b>${fmt(lots.length)}</b><span>lotti</span></div>
        <div><b>${fmt(ents.length)}</b><span>ingressi</span></div>
        <div><b>${fmt(hh)}</b><span>famiglie stimate</span></div>
      </div>
      <dl class="kv">
        <dt>Edifici</dt><dd class="num">${fmt(bld.length)}</dd>
        <dt>Lotti con residenza</dt><dd class="num">${fmt(P.filter((p) => p.sul_res_m2 > 0).length)}</dd>
        <dt>Di cui affidabilità bassa</dt><dd class="num">${fmt(low)}</dd>
        <dt>Superficie residenziale</dt><dd class="num">${fmt(sul)} m²</dd>
        <dt>Superficie dell'area</dt><dd class="num">${fmt(areaM2 / 10000, 2)} ha</dd>
      </dl>
    </div>
    <div class="block">
      <h3>Scarica la selezione</h3>
      <button class="btn wide" type="button" id="dlSel" ${lots.length ? "" : "disabled"}>Scarica ZIP (GeoJSON + CSV)</button>
      <p class="hint">Lotti, edifici e ingressi in GeoJSON EPSG:4326, CSV degli stessi, evidenze degli ingressi e il poligono di selezione.</p>
      <button class="btn outline wide" type="button" id="cpSelEvidence" ${ents.length ? "" : "disabled"}>Copia evidenze ingressi (${fmt(ents.length)})</button>
    </div>`;
  $("dlSel").onclick = () => exportSet(`selezione_${new Date().toISOString().slice(0, 10)}`, areaSel, poly);
  $("cpSelEvidence").onclick = () => copy(entranceEvidenceRows(ents.slice().sort((a, b) => a.p.indirizzo.localeCompare(b.p.indirizzo, "it", { numeric: true }))), `${ents.length} righe copiate`);
  $("clearSel").disabled = false;
  openPanel("area");
}

/* ---------- exports ---------- */
function csvCell(v) {
  if (v == null) return "";
  const s = String(v).replace(/^[=+@\t\r]/, "'$&");
  return /[",\n;]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}
function toCSV(objs, cols) { return "﻿" + [cols.join(",")].concat(objs.map((o) => cols.map((c) => csvCell(o[c])).join(","))).join("\r\n"); }
function fc(list, extra) {
  return JSON.stringify({ type: "FeatureCollection", crs: { type: "name", properties: { name: "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    features: list.map((o) => { const g = o.layer.toGeoJSON(7); g.properties = Object.assign({}, o.p, extra ? extra(o) : {}); return g; }) });
}
const LOT_COLS = ["ref", "foglio", "particella", "foglio_particella", "area_m2", "n_edifici", "n_ingressi", "livelli_max", "sul_res_m2", "famiglie_stimate", "uso_prevalente", "epoca", "affidabilita", "dwellings_2023", "households_2023", "census_status", "civici", "lon", "lat"];
const BLD_COLS = ["bld_id", "CAT_USO", "NUM_PIANI", "livelli", "ALT_EDIFIC", "EPOCA_COST", "VAL_STORIC", "impronta_m2", "sul_res_m2", "famiglie_stimate", "n_ingressi", "foglio", "particella", "SEZCENS", "affidabilita", "dwellings_2023", "households_2023", "census_status", "census_section_2021", "lon", "lat"];
const ENT_COLS = ["COD_CIVICO", "VIA", "CIVICO", "indirizzo", "CAP", "CIRCOSCRIZIONE", "fp", "match_lotto", "bld_id", "famiglie_per_ingresso", "grid_areas_2025", "lon", "lat"];
const ll6 = (ll) => ({ lon: +ll.lng.toFixed(7), lat: +ll.lat.toFixed(7) });
const README = (n) => `Unità San Donato · esportazione ${new Date().toLocaleString("it-IT")}

File
- lotti.geojson / lotti.csv: lotti catastali (Agenzia delle Entrate, WFS INSPIRE) con sintesi di edifici, ingressi e famiglie stimate
- edifici.geojson / edifici.csv: edifici principali della Carta Tecnica di Torino (traslati -1,1 m E, +1,0 m N per allinearli al catasto)
- ingressi.geojson / ingressi.csv: numeri civici della Città di Torino con lotto ed edificio assegnati
${n ? "- area_selezione.geojson: il poligono usato per la selezione\n" : ""}
Sistema di riferimento: GeoJSON in WGS84 (EPSG:4326, ordine lon/lat). Nei CSV lon/lat sono il centroide (poligoni) o il punto.
Precisione delle coordinate: 1e-6 gradi (circa 0,1 m).

Famiglie stimate: famiglie della sezione di censimento ripartite tra gli edifici residenziali in proporzione alla superficie lorda. Non sono unità catastali.
Affidabilità bassa: sezione con meno di 40 o più di 250 m² di superficie per famiglia.

Licenze: Agenzia delle Entrate CC BY 4.0; Città di Torino CC BY 4.0. Citare le fonti.
`;
async function exportSet(name, set, areaPoly) {
  try {
    toast("Preparo il file…");
    const zip = new JSZip();
    const lotsX = set.lots.map((o) => Object.assign({}, o.p, { civici: entsOf(o.p.foglio_particella).map((e) => e.p.indirizzo).join("; ") }, ll6(o.c || o.layer.getBounds().getCenter())));
    zip.file("lotti.geojson", fc(set.lots, (o) => ({ civici: entsOf(o.p.foglio_particella).map((e) => e.p.indirizzo).join("; ") })));
    zip.file("lotti.csv", toCSV(lotsX, LOT_COLS));
    zip.file("edifici.geojson", fc(set.bld));
    zip.file("edifici.csv", toCSV(set.bld.map((o) => Object.assign({}, o.p, ll6(o.layer.getBounds().getCenter()))), BLD_COLS));
    zip.file("ingressi.geojson", fc(set.ents));
    zip.file("ingressi.csv", toCSV(set.ents.map((o) => Object.assign({}, o.p, ll6(o.layer.getLatLng()))), ENT_COLS));
    if (areaPoly) zip.file("area_selezione.geojson", JSON.stringify(areaPoly));
    zip.file("LEGGIMI.txt", README(!!areaPoly));
    if(typeof W !== "undefined" && W.ready) {
      const selectedParcels = new Set(set.lots.map(o => o.p.foglio_particella));
      const selectedBuildings = new Set(set.bld.map(o => String(o.p.bld_id)));
      zip.file("census2023_source.json", JSON.stringify({reference_year:2023, geometry_year:2021, source:W.census.source, buildings:Object.fromEntries(Object.entries(W.census.buildings).filter(([id])=>selectedBuildings.has(id))),limitations:W.census.limitations},null,2));
      zip.file("inspected_ape_records.json", JSON.stringify({...W.apes,certificates:W.apes.certificates.filter(c=>selectedParcels.has(c.parcel))},null,2));
      zip.file("energy_source_benchmarks.json", JSON.stringify({arera:W.benchmark,pvgis:W.solar,kind:"public_benchmarks_not_measured_apartment_energy"},null,2));
      zip.file("ENERGY_NOTES.txt", "Census dwelling counts are allocated estimates, not identified apartments. APE coverage is partial and APE values describe standardized use, not billed consumption. No interior apartment geometry or PODs are available. Multi-subalterno certificate totals must not be duplicated.\n");
    }
    const blob = await zip.generateAsync({ type: "blob", compression: "DEFLATE", compressionOptions: { level: 6 } });
    saveBlob(blob, name + ".zip");
    toast(`Scaricato ${name}.zip (${fmt(blob.size / 1e6, 1)} MB)`);
  } catch (err) {
    toast("Esportazione non riuscita: " + err.message, true);
  }
}
function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}
$("dlFull").onclick = () => {
  const a = document.createElement("a"); a.href = "data/download/torino_sandonato_energy.zip"; a.download = "torino_sandonato_energy.zip";
  document.body.appendChild(a); a.click(); a.remove();
};
$("dlAllGeo").onclick = () => exportSet("torino_sandonato_tutti_i_livelli", { lots: LOTS, bld: BLD, ents: ENTS });

/* ---------- theme ---------- */
function restyle() {
  readColors();
  ROADS.forEach((l) => l.setStyle(roadStyle()));
  LOTS.forEach((o) => o.layer.setStyle(lotStyle(o.p)));
  BLD.forEach((o) => o.layer.setStyle(bldStyle(o.p)));
  SEZ.forEach((l) => l.setStyle(sezStyle()));
  ENTS.forEach((o) => o.layer.setStyle(entStyle()));
  if (selected) selectLot(selected, selEnt, { open: false });
  renderLegend();
}
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", restyle);
new MutationObserver(restyle).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

/* ---------- keyboard ---------- */
document.addEventListener("keydown", (e) => {
  const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || "");
  if (e.key === "Escape" && drawing) { stopDraw(); return; }
  if (typing) return;
  if (e.key === "/") { e.preventDefault(); qEl.focus(); }
  else if (e.key === "d" || e.key === "D") startDraw();
});

map.on("moveend", () => { refreshLabels(); renderPrio(); });
map.on("zoomend", syncLayers);

/* ---------- load ---------- */
renderLegend();
(async function load() {
  try {
    META = await get("meta");
    const [lotti, strade] = await Promise.all([get("lotti"), get("strade")]);
    strade.g.forEach((g) => ROADS.push(L.polygon(polyLL(g), { pane: "roads", renderer: R.roads, interactive: false, ...roadStyle() }).addTo(G.roads)));
    rows(lotti).forEach((p, i) => {
      const layer = L.polygon(polyLL(lotti.g[i]), { pane: "lots", renderer: R.lots, ...lotStyle(p) });
      const o = { p, layer, c: null };
      layer.bindTooltip(() => `<b>${esc(p.foglio_particella)}</b> · ${fmt(p.famiglie_stimate)} fam. stimate · ${fmt(p.n_ingressi)} ingressi`, { sticky: true, direction: "top", offset: [0, -8] });
      layer.on("click", () => { if (!drawing) selectLot(p.foglio_particella); });
      layer.on("mouseover", () => { if (!drawing) layer.setStyle({ weight: 2, color: C["--brand"] }); });
      layer.on("mouseout", () => layer.setStyle(lotStyle(p)));
      LOTS.push(o); lotByFp.set(p.foglio_particella, o); G.lots.addLayer(layer);
    });
    syncLayers();
    $("loading").textContent = "Caricamento edifici e ingressi…";
    // label anchors after first paint
    setTimeout(() => { for (const o of LOTS) { try { o.c = o.layer.getCenter(); } catch (_) { o.c = o.layer.getBounds().getCenter(); } } refreshLabels(); renderPrio(); }, 0);

    const [edifici, ingressi, sezioni] = await Promise.all([get("edifici"), get("ingressi"), get("sezioni")]);
    rows(edifici).forEach((p, i) => {
      const layer = L.polygon(polyLL(edifici.g[i]), { pane: "bld", renderer: R.bld, interactive: false, ...bldStyle(p) });
      const o = { p, layer }; BLD.push(o); G.bld.addLayer(layer);
      if (p.foglio != null) { const fp = `${p.foglio}/${p.particella}`; if (!bldByFp.has(fp)) bldByFp.set(fp, []); bldByFp.get(fp).push(o); }
    });
    rows(sezioni).forEach((p, i) => {
      const layer = L.polygon(polyLL(sezioni.g[i]), { pane: "sez", renderer: R.sez, ...sezStyle() });
      layer.bindTooltip(`Sezione ${p.SEZCENS} · ${fmt(p.NFAMIGL)} famiglie · ${fmt(p.NRESID)} residenti`, { sticky: true });
      SEZ.push(layer); G.sez.addLayer(layer); CENSUS += p.NFAMIGL || 0;
    });
    rows(ingressi).forEach((p, i) => {
      const id = String(p.COD_CIVICO);
      const layer = L.circleMarker(pointLL(ingressi.g[i]), { pane: "ent", renderer: R.ent, ...entStyle() });
      layer.bindTooltip(esc(p.indirizzo), { direction: "top", offset: [0, -6] });
      const ok = p.fp && lotByFp.has(p.fp);
      layer.on("click", (e) => {
        if (drawing) return; L.DomEvent.stopPropagation(e);
        if (ok) selectLot(p.fp, id);
        else if(typeof showRawFeature === "function") { showRawFeature(p, tr("Ingresso senza lotto", "Entrance without parcel")); openStreet(entById.get(id)); }
      });
      const o = { id, p, layer }; ENTS.push(o); entById.set(id, o); G.ent.addLayer(layer);
      IDX.push({ o, k: norm(p.indirizzo) });
      if (ok) { if (!entsByFp.has(p.fp)) entsByFp.set(p.fp, []); entsByFp.get(p.fp).push(o); }
    });
    syncLayers();
    fillStats();
    $("loading").hidden = true;
    document.dispatchEvent(new Event("projectready"));

    const h = location.hash.match(/^#lotto-(\d+)-(\w+)$/);
    const start = h ? null : IDX.find((x) => x.k === norm("Via Felice Cordero Di Pamparato 17"));
    if (h && lotByFp.has(`${h[1]}/${h[2]}`)) selectLot(`${h[1]}/${h[2]}`, null, { fit: true });
    else if (start) { map.setView(start.o.layer.getLatLng(), 18.5); selectLot(start.o.p.fp, start.o.id); }
  } catch (err) {
    $("loading").hidden = false;
    $("loading").innerHTML = `<div class="card" style="padding:14px 16px;max-width:420px"><b>I dati non si sono caricati.</b><br>${esc(err.message)}.<br>Apri la pagina dal server locale (serve.bat, http://localhost:8765) e non come file.</div>`;
  }
})();

function fillStats() {
  const P = LOTS.map((o) => o.p);
  const r = [
    ["Lotti catastali", fmt(P.length)], ["Lotti con residenza", fmt(P.filter((p) => p.sul_res_m2 > 0).length)],
    ["Edifici principali", fmt(BLD.length)], ["Ingressi civici", fmt(ENTS.length)],
    ["Famiglie (censimento)", fmt(CENSUS)], ["Famiglie ripartite sui lotti", fmt(P.reduce((s, p) => s + (p.famiglie_stimate || 0), 0))],
    ["Lotti ad affidabilità bassa", fmt(P.filter((p) => p.sul_res_m2 > 0 && p.affidabilita === "bassa").length)],
    ["Superficie mediana per famiglia", fmt(META.sul_per_famiglia_mediana, 1) + " m²"],
  ];
  $("stats").innerHTML = r.map(([a, b]) => `<span>${a}</span><span>${b}</span>`).join("");
}
