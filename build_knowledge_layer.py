# -*- coding: utf-8 -*-
"""
Costruisce knowledge_layer/nodes/*.csv + knowledge_layer/relationships/relationships.csv
a partire da corpus_working_*.xlsx (foglio CORPUS).

Rigenera SEMPRE l'intero knowledge_layer da zero a partire dal corpus_working
corrente (non incrementale) - dato il volume ridotto (poche centinaia/migliaia
di record), è più semplice e sicuro ricostruire tutto ogni volta piuttosto che
gestire un merge incrementale nodi/relazioni. Il grafo Neo4j va poi ricaricato
con import.cypher (MERGE, quindi idempotente: rieseguirlo dopo un rebuild non
crea duplicati).

Modello concordato con l'utente (2026-08-20, vedi knowledge_layer/graph_schema.md):
- Implementation come nodo centrale, ID_caso originale mai modificato.
- Process/Subprocess/Benefit/Criticity NON derivati dal testo grezzo (90-100%
  frammentati, verificato) ma dai campi tag già costruiti (pbc_tagger.py).
- Program e Source aggiunti rispetto al protocollo base, con evidenza reale di
  ricorrenza nel corpus.
- Nessun nodo/edge per valori NON_CLASSIFICATO o per il sentinel geografico
  GLOBAL_MULTI_COUNTRY_UNSPECIFIED.

AGGIORNAMENTO 2026-08-24 (v2, approvato dall'utente):
- Aggiunta dimensione TipoBeneficiario (chi riceve il beneficio: diretto/utente
  finale, organizzazione/staff interno, causa ambientale/non umana) via
  beneficiary_tagger.py - stesso pattern multi-tag di Beneficio_Tags/Criticita_Tags.
- TRADUZIONE ITALIANA di tutta la struttura del grafo (node label, relationship
  type, property key) mantenuta finora in inglese, su richiesta esplicita
  dell'utente ("vorrei che tutto il contenuto fosse leggibile in italiano").
  I VALORI (canonical_name, testo dei campi) erano già in italiano da sempre;
  solo l'impalcatura (nomi di label/relazioni/proprietà visibili in Neo4j
  Browser/Bloom) era rimasta in inglese per convenzione tecnica.
  ATTENZIONE: questo è un cambio di schema, non additivo per il grafo Neo4j
  già caricato - richiede di svuotare e ricaricare il database (vedi
  graph_schema.md, sezione "Istruzioni di import").

AGGIORNAMENTO 2026-08-24 (v4, gap-analysis in vista dell'osservatorio pubblico):
L'utente ha chiesto quali dimensioni di analisi restassero scoperte rispetto
alle interrogazioni che un osservatorio pubblico dovrebbe supportare. Aggiunte:
- Organizzazione: Dimensione (normalizzata in 7 categorie da free text via
  normalize_dimensione()), Dimensione_dettaglio (testo originale), N_dipendenti,
  Fatturato (questi ultimi due con fill rate basso, 5%/1%, ma preservati perché
  già puliti nel corpus e mai portati sul grafo per puro difetto di omissione).
- Implementazione: Fonte_qualificata (seconda fonte/citazione, non un flag di
  qualità come inizialmente ipotizzato), Fallimenti (testo grezzo, NON taggato -
  59% dei valori sono varianti di "nessuno documentato", non giustifica una
  tassonomia dedicata, ma escluderlo anche come proprietà era un'omissione).
- Nodo Collaboratore + relazione REALIZZATO_CON: organizzazioni/enti terzi
  esplicitamente co-menzionati nel campo Organizzazione ("tramite X", "in
  collaborazione con Y", "in partnership con Z", "in co-sviluppo con W"),
  estratti via collaborator_extractor.py. Copre sia partner tecnologici sia
  enti pubblici/accademici/finanziatori one-off non già catturati da Programma.
  NOTA METODOLOGICA: dedup solo su stringa pulita (no fuzzy Entity Resolution
  come per Organization/Model/Software) - dimensione di arricchimento, non
  primaria; alcuni nomi potrebbero non essere in forma pienamente canonica.
  Un tentativo di dimensione "Funder/Donatore" generica via ricerca testuale
  libera in Osservazioni e' stato scartato dopo verifica: quasi tutte le
  menzioni di fondazioni/finanziatori o duplicavano i 6 Programmi già
  modellati, o si riferivano a chi finanziava la RICERCA/case study (non
  l'implementazione IA), o erano il destinatario dei fondi raccolti (non la
  fonte) - solo 1 caso su ~15 candidati verificati manualmente si è rivelato
  un finanziamento reale non già coperto (SkillUp Coalition, consorzio di 5
  fondazioni, TS-AI-00139), troppo poco per giustificare una dimensione
  dedicata: lasciato come nota nel registro, non modellato come nodo.
- Nodo TipoSupervisioneUmana + relazione COINVOLGE_UMANO: dimensione
  "supervisione umana" (validazione pre-uso, decisione finale, escalation,
  interpretazione, esecuzione/relazione diretta) estratta da
  Ruolo_operatore_umano via human_oversight_tagger.py - stesso pattern
  multi-tag delle altre dimensioni interpretative. Tema di forte interesse per
  la narrativa dell'osservatorio (governance IA / human-in-the-loop).

Uso: eseguire dopo aver rigenerato corpus_working_*.csv con tutte le colonne
additive (geografia, tipologia, tecnologia, Organization/Model/Software_ID,
tag Processo/Settore/Beneficio/Criticita/Tipo_beneficiario/Supervisione_umana).
Percorso del CSV sorgente e cartella di output sono parametrizzati sotto.
"""
import csv
import re
import os
import collections

CORPUS_CSV = "corpus_working_407rec_2026-09-16.csv"  # aggiornare al file corrente
OUT_DIR = "knowledge_layer/"
NODES_DIR = OUT_DIR + "nodes/"
RELS_DIR = OUT_DIR + "relationships/"

GLOBAL_SENTINEL = "GLOBAL_MULTI_COUNTRY_UNSPECIFIED"

PROGRAM_PATTERNS = [
    ("AWS Imagine Grant / AWS Nonprofit Imagine Grant", r"AWS (Nonprofit )?Imagine Grant"),
    ("Patrick J. McGovern Foundation - grant", r"Patrick J\. McGovern Foundation"),
    ("Google.org", r"Google\.org"),
    ("Salesforce Agentforce - Agents for Impact", r"Salesforce Agentforce.*Agents for Impact|Agents for Impact"),
    ("IBM Sustainability Accelerator", r"IBM Sustainability Accelerator"),
    ("data.org Activate AI Challenge", r"data\.org Activate AI"),
    # Aggiungere qui nuovi programmi ricorrenti individuati in cicli futuri,
    # solo se compaiono in almeno ~3 record (soglia usata per i 6 originali).
]

DIM_MAP = {
    'molto piccola': 'Molto Piccola', 'piccola': 'Piccola', 'piccola-emergente': 'Piccola',
    'piccola organizzazione locale': 'Piccola', 'piccola-media': 'Piccola-Media', 'media': 'Media',
    'media-grande': 'Media-Grande', 'grande': 'Grande', 'grande rete di volontari': 'Grande',
    'molto grande': 'Molto Grande', 'non disponibile': 'Non disponibile',
}


def normalize_dimensione(v):
    """Estrae la categoria dimensionale (Piccola/Media/Grande/...) dal testo
    libero di Dimensione, che spesso include dettagli tra parentesi mai
    normalizzati finora (es. 'Grande (13.000 volontari...)' -> 'Grande')."""
    v = (v or '').strip()
    lead = re.split(r'\s*[\(\[]', v, 1)[0].strip().replace('/', '-')
    return DIM_MAP.get(lead.lower(), lead if lead else 'Non disponibile')


COLLAB_TRIGGER = re.compile(
    r"(?:tramite|in collaborazione con|in partnership con|in co-sviluppo con|con il fornitore tecnologico|"
    r"con la (?:tecnologia|piattaforma)(?:\s+di)?)\s+(.+)$"
)
COLLAB_STRIP_PREFIX = re.compile(
    r"^(?:il |l'|la |le )?(?:laboratorio di innovazione|organizzazioni tecniche|fornitore tecnologico|"
    r"azienda di biotecnologia|azienda di |societ[aà] di consulenza )\s*", re.IGNORECASE
)
COLLAB_EXCLUDE = re.compile(
    r"AWS (Nonprofit )?Imagine Grant|Patrick J\. McGovern Foundation|Google\.org|"
    r"Salesforce Agentforce|Agents for Impact|IBM Sustainability Accelerator|IBM Impact Accelerator|"
    r"data\.org Activate AI|Go Further,? Faster( award)?|Faster award|Momentum to Modernize|"
    r"^coorte\b|^Data Cloud$|^Agentforce$", re.IGNORECASE
)


def _clean_collab_entity(e):
    e = e.strip(' .()-')
    e = re.sub(r"^in collaborazione con\s+", "", e, flags=re.IGNORECASE)
    e = COLLAB_STRIP_PREFIX.sub('', e)
    e = re.sub(r"^(il|lo|la|i|gli|le|l')\s+", "", e, flags=re.IGNORECASE)
    e = re.sub(r"\s+-\s+.+$", "", e)
    e = re.sub(r"\s+Open Call.*$", "", e, flags=re.IGNORECASE)
    if e.count('(') > e.count(')'):
        e = e.split('(')[0].strip()
    return e.strip(' .')


def extract_collaborators(org_field):
    """Estrae organizzazioni/enti terzi esplicitamente co-menzionati nel campo
    Organizzazione (non i 6 Programmi già modellati separatamente). Dedup solo
    su stringa pulita - non è Entity Resolution completa (vedi nota nel
    docstring del modulo)."""
    m = COLLAB_TRIGGER.search(org_field)
    if not m:
        return []
    tail = m.group(1).strip(') ').lstrip('(')
    parts = re.split(r"\s*(?:,\s*(?:e\s+|ed\s+)?|\s+ed?\s+|;\s*)", tail)
    out = []
    for p in parts:
        c = _clean_collab_entity(p)
        if c and not COLLAB_EXCLUDE.search(c) and len(c) > 2:
            out.append(c)
    return list(dict.fromkeys(out))


def main():
    os.makedirs(NODES_DIR, exist_ok=True)
    os.makedirs(RELS_DIR, exist_ok=True)

    with open(CORPUS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print("Record caricati:", len(rows))

    relationships = []
    rel_counter = 0

    def add_rel(src_id, src_type, rtype, tgt_id, tgt_type, impl_id, confidence, evidence_field, evidence_value):
        nonlocal rel_counter
        rel_counter += 1
        relationships.append({
            "Relationship_ID": f"REL-{rel_counter:06d}",
            "Source_Node_ID": src_id, "Source_Node_Type": src_type,
            "Relationship_Type": rtype,
            "Target_Node_ID": tgt_id, "Target_Node_Type": tgt_type,
            "Implementation_ID": impl_id, "Confidence": confidence,
            "Evidence_Field": evidence_field, "Evidence_Value": (evidence_value or "")[:200],
        })

    # ---------- Program (estrazione da testo, non ancora un campo risolto) ----------
    prog_id_map, next_prog = {}, 1
    prog_of_record = {}
    for r in rows:
        text = r['Organizzazione'] + ' ' + r['Tecnologia_utilizzata']
        for canon, pat in PROGRAM_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                if canon not in prog_id_map:
                    prog_id_map[canon] = f"PROG-{next_prog:02d}"
                    next_prog += 1
                prog_of_record[r['ID_caso']] = (prog_id_map[canon], canon)
                break

    # ---------- 1) Implementazione ----------
    impl_fields = ["id", "label", "nome", "Anno", "Stato", "Stato_categoria", "Problema", "Obiettivo", "Sottoprocesso",
                   "Workflow_dettagliato", "Input", "Output", "Ruolo_umano", "Livello_integrazione", "KPI", "KPI_tipo",
                   "Tempo_risparmiato", "ROI", "Livello_prova", "Grado_completezza", "Grado_verificabilita",
                   "Grado_verificabilita_normalizzato", "Grado_verificabilita_nota",
                   "Livello_confidenza", "Livello_confidenza_normalizzato", "Osservazioni", "Fonte_qualificata", "Fallimenti",
                   "Anno_implementazione_effettiva", "Anno_annuncio_o_selezione", "Anno_fondazione_organizzazione"]
    impl_rows = [{
        "id": r['ID_caso'], "label": "Implementazione", "nome": r['ID_caso'],
        "Anno": r['Anno_implementazione'], "Stato": r['Stato_implementazione'],
        "Stato_categoria": r.get('Stato_categoria', ''),
        "Problema": r['Problema_affrontato'], "Obiettivo": r['Obiettivo_implementazione'],
        "Sottoprocesso": r['Sotto_processo'], "Workflow_dettagliato": r['Workflow_dettagliato'],
        "Input": r['Input'], "Output": r['Output'], "Ruolo_umano": r['Ruolo_operatore_umano'],
        "Livello_integrazione": r['Livello_integrazione'], "KPI": r['KPI'], "KPI_tipo": r.get('KPI_tipo', ''),
        "Tempo_risparmiato": r['Tempo_risparmiato'], "ROI": r['ROI'], "Livello_prova": r['Livello_prova'],
        "Grado_completezza": r['Grado_completezza'], "Grado_verificabilita": r['Grado_verificabilita'],
        "Grado_verificabilita_normalizzato": r.get('Grado_verificabilita_normalizzato', ''),
        "Grado_verificabilita_nota": r.get('Grado_verificabilita_nota', ''),
        "Livello_confidenza": r['Livello_confidenza'],
        "Livello_confidenza_normalizzato": r.get('Livello_confidenza_normalizzato', ''),
        "Osservazioni": r['Osservazioni'],
        "Fonte_qualificata": r.get('Fonte_qualificata', ''), "Fallimenti": r.get('Fallimenti', ''),
        "Anno_implementazione_effettiva": r.get('Anno_implementazione_effettiva', ''),
        "Anno_annuncio_o_selezione": r.get('Anno_annuncio_o_selezione', ''),
        "Anno_fondazione_organizzazione": r.get('Anno_fondazione_organizzazione', ''),
    } for r in rows]
    _write(NODES_DIR + 'implementazioni.csv', impl_fields, impl_rows)

    # ---------- 2) Organizzazione ----------
    org_seen = {}
    for r in rows:
        oid = r['Organization_ID']
        if oid not in org_seen:
            org_seen[oid] = {"id": oid, "label": "Organizzazione", "nome": r['Organization_Canonical'],
                              "Tipo_organizzazione": r['Categoria_organizzativa'], "Status_legale": r['Status_legale_specifico'],
                              "Dimensione": normalize_dimensione(r.get('Dimensione', '')),
                              "Dimensione_dettaglio": r.get('Dimensione', ''),
                              "N_dipendenti": r.get('N_dipendenti', ''), "Fatturato": r.get('Fatturato', '')}
        add_rel(oid, "Organizzazione", "HA_IMPLEMENTAZIONE", r['ID_caso'], "Implementazione", r['ID_caso'], "ALTA", "Organizzazione", r['Organizzazione'])
    _write(NODES_DIR + 'organizzazioni.csv',
           ["id", "label", "nome", "Tipo_organizzazione", "Status_legale", "Dimensione", "Dimensione_dettaglio", "N_dipendenti", "Fatturato"],
           list(org_seen.values()))

    # ---------- 3) Paese ----------
    country_names = set()
    for r in rows:
        for c in r['Organization_Country'].split(';'):
            c = c.strip()
            if c and c != GLOBAL_SENTINEL: country_names.add(c)
        for c in r['Implementation_Country'].split(';'):
            c = c.strip()
            if c and c != GLOBAL_SENTINEL: country_names.add(c)
    country_id_map = {name: f"COU-{i+1:03d}" for i, name in enumerate(sorted(country_names))}
    _write(NODES_DIR + 'paesi.csv', ["id", "label", "nome"],
           [{"id": cid, "label": "Paese", "nome": name} for name, cid in country_id_map.items()])
    # Correzione 2026-09-16 (fase 0c): HA_SEDE_IN veniva emessa una volta per ogni implementazione
    # dell'organizzazione, generando relazioni duplicate (15 duplicati su 6.500) e gonfiando ogni
    # conteggio basato sulla sede. La sede e' una proprieta' dell'organizzazione, non della singola
    # implementazione: si emette una sola relazione per coppia organizzazione-paese.
    sedi_gia_emesse = set()
    for r in rows:
        for c in r['Organization_Country'].split(';'):
            c = c.strip()
            if c and c != GLOBAL_SENTINEL and (r['Organization_ID'], c) not in sedi_gia_emesse:
                sedi_gia_emesse.add((r['Organization_ID'], c))
                add_rel(r['Organization_ID'], "Organizzazione", "HA_SEDE_IN", country_id_map[c], "Paese", r['ID_caso'], "ALTA", "Organization_Country", c)
        for c in r['Implementation_Country'].split(';'):
            c = c.strip()
            if c and c != GLOBAL_SENTINEL:
                add_rel(r['ID_caso'], "Implementazione", "IMPLEMENTATO_IN", country_id_map[c], "Paese", r['ID_caso'], r['Geographic_Confidence'], "Implementation_Country", c)

    # ---------- 4) ModelloIA / 5) Software (solo entità già risolte con ID) ----------
    model_seen, soft_seen = {}, {}
    for r in rows:
        if r['Model_ID']:
            model_seen[r['Model_ID']] = {"id": r['Model_ID'], "label": "ModelloIA", "nome": r['Model_Canonical']}
            add_rel(r['ID_caso'], "Implementazione", "USA_MODELLO", r['Model_ID'], "ModelloIA", r['ID_caso'], "ALTA", "Modello_AI", r['Modello_AI'])
        if r['Software_ID']:
            soft_seen[r['Software_ID']] = {"id": r['Software_ID'], "label": "Software", "nome": r['Software_Canonical']}
            add_rel(r['ID_caso'], "Implementazione", "USA_SOFTWARE", r['Software_ID'], "Software", r['ID_caso'], "ALTA", "Software_utilizzato", r['Software_utilizzato'])
    _write(NODES_DIR + 'modelli_ia.csv', ["id", "label", "nome"], list(model_seen.values()))
    _write(NODES_DIR + 'software.csv', ["id", "label", "nome"], list(soft_seen.values()))

    # ---------- 6-12) Nodi da campi tag multi-valore ----------
    _build_tag_nodes(rows, 'Categoria_organizzativa', 'CAT', 'CategoriaOrganizzativa', add_rel,
                      rel_type='HA_TIPO', per_organization=True, node_path=NODES_DIR + 'categorie_organizzative.csv')
    _build_tag_nodes(rows, 'Tecnica_IA_Tags', 'TEC', 'TecnicaIA', add_rel, rel_type='USA_TECNICA',
                      node_path=NODES_DIR + 'tecniche_ia.csv')
    _build_tag_nodes(rows, 'Fornitore_Piattaforma_Tags', 'VEN', 'Fornitore', add_rel, rel_type='USA_FORNITORE',
                      node_path=NODES_DIR + 'fornitori.csv')
    _build_tag_nodes(rows, 'Funzione_organizzativa_Tags', 'FUNC', 'FunzioneOrganizzativa', add_rel, rel_type='HA_FUNZIONE',
                      node_path=NODES_DIR + 'funzioni_organizzative.csv')
    _build_tag_nodes(rows, 'Settore_missione_Tags', 'SET', 'SettoreMissione', add_rel, rel_type='INDIRIZZA_SETTORE',
                      node_path=NODES_DIR + 'settori_missione.csv')
    _build_tag_nodes(rows, 'Beneficio_Tags', 'BEN', 'Beneficio', add_rel, rel_type='RIPORTA_BENEFICIO',
                      node_path=NODES_DIR + 'benefici.csv')
    _build_tag_nodes(rows, 'Criticita_Tags', 'CRI', 'Criticita', add_rel, rel_type='RIPORTA_CRITICITA',
                      node_path=NODES_DIR + 'criticita.csv')
    # NUOVO 2026-08-24: chi riceve il beneficio (diretto/utente finale, organizzazione/staff, causa ambientale)
    _build_tag_nodes(rows, 'Tipo_beneficiario_Tags', 'TBEN', 'TipoBeneficiario', add_rel, rel_type='HA_BENEFICIARIO',
                      node_path=NODES_DIR + 'tipi_beneficiario.csv')
    # NUOVO 2026-08-24 (v4): tipo di supervisione/coinvolgimento umano nel workflow
    _build_tag_nodes(rows, 'Supervisione_umana_Tags', 'SUP', 'TipoSupervisioneUmana', add_rel, rel_type='COINVOLGE_UMANO',
                      node_path=NODES_DIR + 'tipi_supervisione_umana.csv')

    # ---------- 13bis) Collaboratore (NUOVO 2026-08-24, v4) ----------
    collab_id_map, next_collab = {}, 1
    for r in rows:
        for name in extract_collaborators(r['Organizzazione']):
            if name not in collab_id_map:
                collab_id_map[name] = f"COLLAB-{next_collab:03d}"
                next_collab += 1
            add_rel(r['ID_caso'], "Implementazione", "REALIZZATO_CON", collab_id_map[name], "Collaboratore",
                     r['ID_caso'], "MEDIA", "Organizzazione", r['Organizzazione'])
    _write(NODES_DIR + 'collaboratori.csv', ["id", "label", "nome"],
           [{"id": cid, "label": "Collaboratore", "nome": name} for name, cid in collab_id_map.items()])
    print(f"collaboratori.csv: {len(collab_id_map)} nodi")

    # ---------- 13) Programma ----------
    _write(NODES_DIR + 'programmi.csv', ["id", "label", "nome"],
           [{"id": pid, "label": "Programma", "nome": name} for name, pid in prog_id_map.items()])
    for impl_id, (pid, pname) in prog_of_record.items():
        add_rel(impl_id, "Implementazione", "FA_PARTE_DI", pid, "Programma", impl_id, "ALTA", "Organizzazione/Tecnologia_utilizzata", pname)

    # ---------- 14) Fonte ----------
    src_seen, next_src = {}, 1
    for r in rows:
        fp = r['Fonte_primaria'].strip()
        if fp not in src_seen:
            src_seen[fp] = f"SRC-{next_src:05d}"
            next_src += 1
        add_rel(r['ID_caso'], "Implementazione", "DOCUMENTATO_DA", src_seen[fp], "Fonte", r['ID_caso'], "ALTA", "Fonte_primaria", fp)
    _write(NODES_DIR + 'fonti.csv', ["id", "label", "nome"],
           [{"id": sid, "label": "Fonte", "nome": fp[:300]} for fp, sid in src_seen.items()])

    # ---------- relationships.csv ----------
    rel_fields = ["Relationship_ID", "Source_Node_ID", "Source_Node_Type", "Relationship_Type", "Target_Node_ID",
                  "Target_Node_Type", "Implementation_ID", "Confidence", "Evidence_Field", "Evidence_Value"]
    _write(RELS_DIR + 'relationships.csv', rel_fields, relationships)

    print("\nTotale relazioni:", len(relationships))
    counts = collections.Counter(r['Relationship_Type'] for r in relationships)
    for k, v in counts.most_common():
        print(f"  {v:5d}  {k}")


def _build_tag_nodes(rows, field, prefix, label, add_rel, rel_type=None, per_organization=False, node_path=None):
    """Costruisce nodi + relazioni per un campo multi-tag (semicolon-separated).
    Se per_organization=True, collega Organizzazione->rel_type->Nodo (una volta per
    organizzazione, usato solo per Categoria_organizzativa). Altrimenti collega
    Implementazione->rel_type->Nodo."""
    values = set()
    for r in rows:
        for t in r[field].split(';'):
            t = t.strip()
            if t and t != "NON_CLASSIFICATO":
                values.add(t)
    id_map = {v: f"{prefix}-{i+1:02d}" for i, v in enumerate(sorted(values))}
    _write(node_path, ["id", "label", "nome"],
           [{"id": vid, "label": label, "nome": v} for v, vid in id_map.items()])

    if per_organization:
        seen = set()
        for r in rows:
            v = r[field].strip()
            if v and v != "NON_CLASSIFICATO" and (r['Organization_ID'], v) not in seen:
                seen.add((r['Organization_ID'], v))
                add_rel(r['Organization_ID'], "Organizzazione", rel_type, id_map[v], label, r['ID_caso'], "ALTA", field, v)
    else:
        for r in rows:
            for t in r[field].split(';'):
                t = t.strip()
                if t and t != "NON_CLASSIFICATO":
                    add_rel(r['ID_caso'], "Implementazione", rel_type, id_map[t], label, r['ID_caso'], "MEDIA", field, t)
    print(f"{os.path.basename(node_path)}: {len(id_map)} nodi")


def _write(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
