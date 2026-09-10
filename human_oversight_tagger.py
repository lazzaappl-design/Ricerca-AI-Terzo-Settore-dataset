# -*- coding: utf-8 -*-
"""
Dimensione additiva "Supervisione_umana_Tags" (che tipo di ruolo/controllo
umano e' descritto nel workflow), costruita bottom-up dal campo
Ruolo_operatore_umano (100% valorizzato su 389 record, nessun vuoto).

Nasce da una lacuna identificata dall'utente in vista dell'osservatorio
pubblico: Ruolo_operatore_umano esisteva solo come testo libero (proprieta'
del nodo Implementazione), senza un vocabolario controllato interrogabile in
aggregato - a differenza di tutte le altre dimensioni interpretative
(Beneficio, Criticita, Funzione, Settore, Tipo_beneficiario). Tema rilevante
per un observatory pubblico (governance IA / "human-in-the-loop" e' un
argomento di forte interesse LinkedIn).

Campo multi-tag: un record puo' descrivere piu' forme di coinvolgimento umano
contemporaneamente (es. sia validazione pre-uso sia gestione delle eccezioni).

5 tag (bottom-up, poi ampliati per copertura):
- Validazione/correzione umana pre-uso
- Decisione finale umana
- Supervisione per eccezioni/escalation
- Interpretazione/analisi umana dei risultati
- Esecuzione/relazione diretta mantenuta da umano

Metodologia: pattern regex iterati fino a un residuo NON_CLASSIFICATO del 5%
(20/389), poi i 20 casi residui letti singolarmente e classificati per
giudizio (MANUAL_OVERRIDES) - stesso standard di qualita' applicato a
Tipo_beneficiario_Tags. Un solo caso (TS-AI-00036) resta genuinamente
NON_CLASSIFICATO: la fonte dichiara esplicitamente "non specificato".
"""
import re

VALIDAZIONE = re.compile(r"valid|verific|corregg|controll|revision|rivede|rived|rivalut|modific|cura(no)? (il|i|la|le)|aggiorna", re.IGNORECASE)
DECISIONE = re.compile(r"decid|decisor|decision|approv|autorizz|seleziona(no)?( il)? match finale|scelgono|conferma", re.IGNORECASE)
ESCALATION = re.compile(r"escalation|casi (non risolvibili|complessi|non risolti|difficili)|supervision|limite dell.?(ia|intelligenza)", re.IGNORECASE)
INTERPRETAZIONE = re.compile(r"interpreta|analizza|valuta( criticamente)?|genera(no)? scenari|contestualizza", re.IGNORECASE)
ESECUZIONE = re.compile(
    r"esegue|effettua|conduce(no)? i colloqui|contatta(no)?|chiamate|eroga(zione)?|gestisce (la relazione|l[ao] )|gestiscono|"
    r"mantengono la relazione|intervengono|intervent|agisce|riceve(no)? (notifiche|allert)|"
    r"utilizza(no)?( la lista| gli insight| come assistente)?|riceve(no)? un volume|"
    r"applica(no)?|restano (responsabili|al centro|primario)|continua(no)? a (operare|gestire|seguire)|"
    r"guida(no)?|co-progett|hanno contribuito|contribui(scono)?|support(a|ano)|"
    r"restano il canale|responsabili della (cura|risposta)", re.IGNORECASE)

VALIDAZIONE_TAG = "Validazione/correzione umana pre-uso"
DECISIONE_TAG = "Decisione finale umana"
ESCALATION_TAG = "Supervisione per eccezioni/escalation"
INTERPRETAZIONE_TAG = "Interpretazione/analisi umana dei risultati"
ESECUZIONE_TAG = "Esecuzione/relazione diretta mantenuta da umano"

# 20 casi non catturati dal pattern-matching, letti singolarmente (2026-08-24).
# TS-AI-00036 resta NON_CLASSIFICATO: fonte dichiara esplicitamente "non specificato".
MANUAL_OVERRIDES = {
    "TS-AI-00029": [VALIDAZIONE_TAG],                          # team ha curato/addestrato i contenuti del sistema
    "TS-AI-00032": [ESECUZIONE_TAG],                            # accompagnamento diretto mantenuto dagli assistenti sociali
    "TS-AI-00051": [DECISIONE_TAG, ESECUZIONE_TAG],             # gestisce il processo finale di adozione
    "TS-AI-00063": [VALIDAZIONE_TAG],                           # "human-in-the-loop" esplicito, correzione dei volontari
    "TS-AI-00081": [ESCALATION_TAG],                            # "experts-in-the-loop", infermiere rispondono a ciò che il sistema non gestisce
    "TS-AI-00087": [ESECUZIONE_TAG],                            # personale gestisce ammissione/distribuzione
    "TS-AI-00094": [ESECUZIONE_TAG, DECISIONE_TAG],             # volontari eseguono con piena discrezionalità di accettare/rifiutare
    "TS-AI-00116": [ESECUZIONE_TAG],                            # team mantiene la cura diretta degli animali
    "TS-AI-00122": [ESECUZIONE_TAG],                            # operatori gestiscono le operazioni di piantumazione automatizzata
    "TS-AI-00131": [ESCALATION_TAG],                            # gestisce i casi non risolvibili dal chatbot
    "TS-AI-00155": [ESCALATION_TAG],                            # interviene quando l'IA raggiunge il limite della propria conoscenza
    "TS-AI-00160": [ESECUZIONE_TAG, ESCALATION_TAG],            # operatori eseguono acquisizione; rinvio telemedico a specialisti per casi complessi
    "TS-AI-00161": [ESECUZIONE_TAG],                            # insegnanti integrano lo strumento come supplemento, non sostituzione
    "TS-AI-00189": [ESECUZIONE_TAG],                            # personale gestisce i casi, volontari raccolgono dati
    "TS-AI-00231": [ESCALATION_TAG, ESECUZIONE_TAG],            # esperti rispondono alle richieste instradate dal triage IA
    "TS-AI-00316": [VALIDAZIONE_TAG],                           # medici rivedono le versioni semplificate prima della condivisione
    "TS-AI-00330": [ESECUZIONE_TAG],                            # funzionari usano le indicazioni per orientare le proprie politiche
    "TS-AI-00351": [ESCALATION_TAG, ESECUZIONE_TAG],            # counselor ricevono gli utenti indirizzati dal chatbot
    "TS-AI-00358": [ESECUZIONE_TAG],                            # mentori mantengono la relazione di mentoring, con più tempo disponibile
}


def classify_tags(id_caso, text):
    if id_caso in MANUAL_OVERRIDES:
        return "; ".join(MANUAL_OVERRIDES[id_caso])
    tags = []
    if VALIDAZIONE.search(text): tags.append(VALIDAZIONE_TAG)
    if DECISIONE.search(text): tags.append(DECISIONE_TAG)
    if ESCALATION.search(text): tags.append(ESCALATION_TAG)
    if INTERPRETAZIONE.search(text): tags.append(INTERPRETAZIONE_TAG)
    if ESECUZIONE.search(text): tags.append(ESECUZIONE_TAG)
    if not tags:
        return "NON_CLASSIFICATO"
    return "; ".join(tags)


def classify_record(r):
    text = r.get('Ruolo_operatore_umano', '')
    tags = classify_tags(r['ID_caso'], text)
    return {
        "ID_caso": r["ID_caso"],
        "Supervisione_umana_Tags": tags,
        "Requires_Human_Review_Sup": "YES" if tags == "NON_CLASSIFICATO" else "NO",
    }


if __name__ == "__main__":
    import csv, collections
    with open('/sessions/wonderful-focused-faraday/mnt/Ricerca AI Terzo Settore/database_casi.csv', newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    results = [classify_record(r) for r in rows]
    counts = collections.Counter()
    for res in results:
        for t in res["Supervisione_umana_Tags"].split("; "):
            counts[t] += 1
    for k, v in counts.most_common():
        print(f"{v:4d}  {k}")
    n_review = sum(1 for res in results if res["Requires_Human_Review_Sup"] == "YES")
    print("\nRecord totali:", len(results), " | NON_CLASSIFICATO:", n_review)
