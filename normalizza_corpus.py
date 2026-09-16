# -*- coding: utf-8 -*-
"""
normalizza_corpus.py — normalizzazione additiva dei campi a testo libero del corpus.

COSA FA: legge corpus_working_407rec_2026-09-16.csv e vi AGGIUNGE 9 colonne derivate,
senza modificare nessuna colonna originale (nessuna perdita di informazione):

  Stato_categoria                      (decisione D2, fase 0) 6 valori standard ricavati da Stato_implementazione
  Anno_implementazione_effettiva       (D3) anno in cui l'implementazione e' realmente operativa
  Anno_annuncio_o_selezione            (D3) anno dell'annuncio o della selezione a un bando
  Anno_fondazione_organizzazione       (D3) anno di fondazione, quando il campo Anno lo conteneva
  Anno_da_verificare                   (D3) marcato quando il testo non permette di isolare l'anno con sicurezza
  Livello_confidenza_normalizzato      (D4) scala fissa a 5 valori
  Grado_verificabilita_normalizzato    (D4) scala fissa a 5 valori
  Grado_verificabilita_nota            (D4) chiarimento, dove serve
  KPI_tipo                             (D5) marcato dove il KPI e' un obiettivo dichiarato, non un risultato misurato

QUANDO ESEGUIRLO: dopo aver accodato nuovi casi al corpus e prima di build_knowledge_layer.py,
in modo che i casi nuovi nascano con le stesse colonne derivate dei casi esistenti.

COME: da terminale, dalla cartella del progetto:   python3 normalizza_corpus.py
Riscrive il corpus in place: fare una copia di sicurezza prima di eseguirlo su dati non salvati.

NOTA: i 3 casi elencati in AMBIGUOUS_IDS sono classificati a mano come "Ambiguo/da rivedere"
perche' il testo non permetteva una classificazione sicura: non sono stati forzati in una categoria.

Prima stesura: 2026-09-16 (fase 0 di pulizia dati). Vedi decisioni_fase0.md e diagnosi_fase0.md.
"""
import csv, re, collections

IN_FILE = "corpus_working_407rec_2026-09-16.csv"

with open(IN_FILE, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    rows = list(reader)

print(f"Righe lette: {len(rows)}, colonne originali: {len(fieldnames)}")

# ============ 2a. Stato_categoria ============
AMBIGUOUS_IDS = {"TS-AI-00008", "TS-AI-00066", "TS-AI-00176"}

def classify_stato(v):
    vl = v.lower()
    if vl.startswith('abbandonato') or vl.startswith('interrotto/disattivato'):
        return 'Abbandonato'
    if vl.startswith('completato') or vl.startswith('concluso') or vl.startswith('risposta operativa completata') or vl.startswith('progetto pilota completato'):
        return 'Concluso'
    if vl.startswith('operativo') or vl.startswith('dispiegamento production-ready') or vl.startswith('piattaforma earthranger operativa'):
        return 'Operativo'
    grant_kw = re.search(r'grant|premio|accelerator|acceleratore|fellowship|coorte|challenge|selezion|vincitri|vincitore|finanziament[oi] patrick|mcgovern|salesforce|aws imagine|google\.org|ibm sustainability|ibm impact|data\.org', vl)
    dev_kw = bool(re.match(r'^(in fase|in sviluppo|in corso|proof of concept|pilota|prototipo|fase |beta\b)', vl))
    if dev_kw and grant_kw:
        return 'Annunciato/selezionato in programma (non ancora operativo)'
    if dev_kw:
        return 'In sviluppo/pilota (generico)'
    return 'Ambiguo/da rivedere'

for r in rows:
    if r['ID_caso'] in AMBIGUOUS_IDS:
        r['Stato_categoria'] = 'Ambiguo/da rivedere'
    else:
        r['Stato_categoria'] = classify_stato(r['Stato_implementazione'])

c = collections.Counter(r['Stato_categoria'] for r in rows)
print("\n--- Stato_categoria ---")
for k, v in c.most_common():
    print(f"{v:4d}  {k}")

# ============ 3a. Separazione Anno ============
YEAR_RE = re.compile(r'(1[89]\d{2}|20[0-2]\d)')
FOUND_RE = re.compile(r'fondazion|fondat[ao]|nasc[ei]ta dell.organizzazione')
GRANT_RE = re.compile(r'grant|premio|selezion|vincitr|vincitor|coorte|accelerat|fellowship|challenge|finanziament|annunci|open call')

def split_anno(anno_raw):
    """Ritorna (effettiva, annuncio, fondazione, da_verificare)"""
    v = anno_raw.strip()
    # caso pulito: solo un anno o un intervallo di due anni, senza altro testo
    if re.fullmatch(r'(19|20)\d{2}(\s*[-–]\s*(19|20)\d{2})?', v):
        return v, '', '', ''

    # spezza in segmenti separati da parentesi/trattini/punti e virgola
    segments = re.split(r';|(?<=\))\s*-\s*|(?<=\))\s*,\s*', v)
    eff_candidates = []
    grant_candidates = []
    found_candidates = []
    for seg in segments:
        years = YEAR_RE.findall(seg)
        if not years:
            continue
        seg_l = seg.lower()
        if FOUND_RE.search(seg_l):
            found_candidates.extend(years)
        elif GRANT_RE.search(seg_l):
            grant_candidates.extend(years)
        else:
            eff_candidates.extend(years)

    # fallback: se la segmentazione non ha isolato nulla (es. tutto su un unico segmento con piu' anni e piu' keyword miste), riprova sull'intero testo con una scansione a finestra
    if not eff_candidates and not grant_candidates and not found_candidates:
        years = YEAR_RE.findall(v)
        vl = v.lower()
        if FOUND_RE.search(vl) and len(years) >= 2:
            found_candidates = [years[0]]
            eff_candidates = years[1:]
        elif GRANT_RE.search(vl) and len(years) >= 1:
            grant_candidates = years
        else:
            eff_candidates = years

    eff = eff_candidates[-1] if eff_candidates else ''
    annuncio = grant_candidates[0] if grant_candidates else ''
    fondazione = found_candidates[0] if found_candidates else ''

    da_verificare = ''
    if not eff:
        # nessun anno "di implementazione" isolato con sicurezza
        da_verificare = 'SI'
        if not eff and grant_candidates and not found_candidates:
            # se c'e' solo un anno di grant/selezione, usalo anche come effettiva approssimativa ma segnala comunque
            eff = grant_candidates[-1]
    return eff, annuncio, fondazione, da_verificare

n_split = 0
n_flag = 0
flagged = []
for r in rows:
    eff, annuncio, fondazione, flag = split_anno(r['Anno_implementazione'])
    r['Anno_implementazione_effettiva'] = eff
    r['Anno_annuncio_o_selezione'] = annuncio
    r['Anno_fondazione_organizzazione'] = fondazione
    r['Anno_da_verificare'] = flag
    if r['Anno_implementazione'].strip() != eff or annuncio or fondazione:
        n_split += 1
    if flag:
        n_flag += 1
        flagged.append((r['ID_caso'], r['Anno_implementazione']))

print(f"\n--- Anno ---")
print(f"Righe con testo originale complesso (annuncio/fondazione separati o riformulate): {n_split}")
print(f"Righe segnalate 'da verificare manualmente' (nessun anno di implementazione isolato con sicurezza): {n_flag}")
for id_, txt in flagged:
    print(f"  {id_} | {txt}")

# ============ 4a. Normalizzazione Livello_confidenza / Grado_verificabilita ============
CONF_MAP = {
    'basso': 'Basso', 'basso-medio': 'Basso-Medio', 'medio-basso': 'Basso-Medio', 'basso-medio ': 'Basso-Medio',
    'medio': 'Medio',
    'medio-alto': 'Medio-Alto',
    'alto': 'Alto', 'molto alto': 'Alto',
}
def norm_conf(v):
    key = v.strip().lower().replace('à','a')
    return CONF_MAP.get(key, v.strip())

for r in rows:
    r['Livello_confidenza_normalizzato'] = norm_conf(r['Livello_confidenza'])

c2 = collections.Counter(r['Livello_confidenza_normalizzato'] for r in rows)
print("\n--- Livello_confidenza_normalizzato ---")
for k, v in c2.most_common():
    print(f"{v:4d}  {k}")

VERIF_MAP = {
    'alta': 'Alta', 'molto alta': 'Alta',
    'media-alta': 'Media-Alta',
    'media': 'Media',
    'medio-bassa': 'Bassa-Media', 'bassa-media': 'Bassa-Media',
    'bassa': 'Bassa',
}
def split_verif(v):
    v = v.strip()
    m = re.match(r'^([^(]+?)\s*(\((.*)\))?$', v)
    base = m.group(1).strip() if m else v
    nota = m.group(3).strip() if m and m.group(3) else ''
    key = base.lower().replace('à','a')
    canon = VERIF_MAP.get(key, base)
    return canon, nota

for r in rows:
    canon, nota = split_verif(r['Grado_verificabilita'])
    r['Grado_verificabilita_normalizzato'] = canon
    r['Grado_verificabilita_nota'] = nota

c3 = collections.Counter(r['Grado_verificabilita_normalizzato'] for r in rows)
print("\n--- Grado_verificabilita_normalizzato ---")
for k, v in c3.most_common():
    print(f"{v:4d}  {k}")

# ============ 5a. KPI_tipo ============
KPI_KWS = ['selezion','vincitric','vincitore','finalist','obiettivo dichiarat','previst','atteso','attesi','target di','punta a','pianificat']
def kpi_flag(v):
    if not v.strip():
        return ''
    low = v.lower()
    if any(k in low for k in KPI_KWS):
        return 'Obiettivo dichiarato/selezione (non ancora misurato)'
    return ''

n_kpi = 0
for r in rows:
    r['KPI_tipo'] = kpi_flag(r['KPI'])
    if r['KPI_tipo']:
        n_kpi += 1
print(f"\n--- KPI_tipo ---\nRighe flaggate: {n_kpi}/{len(rows)}")

# ============ scrittura ============
new_cols = ['Stato_categoria', 'Anno_implementazione_effettiva', 'Anno_annuncio_o_selezione',
            'Anno_fondazione_organizzazione', 'Anno_da_verificare',
            'Livello_confidenza_normalizzato', 'Grado_verificabilita_normalizzato',
            'Grado_verificabilita_nota', 'KPI_tipo']
# Idempotenza: se una colonna derivata esiste gia' (script rieseguito su un corpus
# gia' normalizzato) il suo valore viene aggiornato, non duplicato in una seconda colonna.
out_fieldnames = fieldnames + [c for c in new_cols if c not in fieldnames]

with open(IN_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=out_fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nFile riscritto: {IN_FILE}")
print(f"Colonne totali ora: {len(out_fieldnames)} (erano {len(fieldnames)}, nuove {len([c for c in new_cols if c not in fieldnames])}, aggiornate {len([c for c in new_cols if c in fieldnames])})")
