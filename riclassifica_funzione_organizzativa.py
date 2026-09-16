# -*- coding: utf-8 -*-
"""
riclassifica_funzione_organizzativa.py — riduzione dei casi NON_CLASSIFICATO in Funzione_organizzativa_Tags.

COSA FA: legge corpus_working_407rec_2026-09-16.csv e riclassifica i casi marcati
NON_CLASSIFICATO nella colonna Funzione_organizzativa_Tags, in due passaggi:
  1. verifica se il testo rientra in una delle categorie gia' esistenti (erano casi mal etichettati);
  2. se descrive un servizio erogato direttamente a un beneficiario finale, assegna la categoria
     "Erogazione diretta", introdotta perche' le 18 categorie originali coprivano solo funzioni
     di back-office (decisione D6, fase 0).

Esito della prima esecuzione (2026-09-16): 162 casi NON_CLASSIFICATO -> 45 (39,8% -> 11,1%).
45 casi rientrati in categorie esistenti, 72 taggati "Erogazione diretta", 45 lasciati
deliberatamente non classificati perche' il testo non consente una classificazione sicura.

QUANDO ESEGUIRLO: dopo pbc_tagger.py e prima di build_knowledge_layer.py.
La categoria "Erogazione diretta" e' stata aggiunta anche a PROC_TAGS dentro pbc_tagger.py,
quindi i casi nuovi dovrebbero gia' nascere classificati: questo script resta come rete di sicurezza
e per riprodurre la riclassificazione storica.

COME: da terminale, dalla cartella del progetto:   python3 riclassifica_funzione_organizzativa.py
Riscrive il corpus in place: fare una copia di sicurezza prima di eseguirlo su dati non salvati.

Prima stesura: 2026-09-16 (fase 0 di pulizia dati). Vedi decisioni_fase0.md e diagnosi_fase0.md.
"""
import csv, re, collections

IN_FILE = "corpus_working_407rec_2026-09-16.csv"

with open(IN_FILE, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    rows = list(reader)

RULES = [
    ("Accessibilità/produzione contenuti accessibili",
     r"accessibil|non veden|ipoveden|sordociech|disabilit[aà].{0,15}(uditiv|cognitiv)|formati accessibili|autonomia digitale delle persone con disabilit"),
    ("Servizi legali",
     r"giuridic|consulenza legale|servizi legali"),
    ("Gestione volontari/HR",
     r"coordinamento dei volontari|logistica.{0,10}volontari|risorse umane"),
    ("Gestione documentale/knowledge management",
     r"documentazione clinica|cartelle clinich|digitalizzazione delle cartelle|digitalizzazione di dati raccolti|trascrizione di documenti storici|curatela di dat|gestione delle cartelle cliniche"),
    ("Analisi dati/supporto decisionale",
     r"^analisi (di|dei) dat|^mappatura|^modellazione|rilevamento e analisi di immagini|raccolta e analisi di dati|analisi di video|analisi di sentenze|analisi di reclami|analisi dell.ambiente|analisi di dati aggregati|analisi di dati su|elaborazione e analisi di dati"),
    ("Gestione casi (case management)",
     r"gestione delle cartelle e dei percorsi di cura|screening e assegnazione dei beneficiari ai servizi"),
    ("Fundraising/raccolta fondi",
     r"outreach ai donatori|rendicontazione.{0,15}donatori|impatto umanitario ai donatori"),
    ("CRM/gestione relazioni",
     r"relazioni con i partner|gestione delle relazioni con i clienti"),
    ("Amministrazione/gestione finanziaria",
     r"processi finanziari per il finanziamento|rendicontazione ai finanziatori|dati e rendicontazione ai finanziatori"),
]

def try_existing(text):
    tl = text.lower()
    for label, pattern in RULES:
        if re.search(pattern, tl):
            return label
    return None

# segnali che indicano un servizio/intervento diretto a una persona/gruppo beneficiario identificabile
DIRETTA_KW = re.compile(
    r"erogazione di (servizi|informazioni|percorsi|risorse|coaching|contenuti|sessioni|supporto)"
    r"|screening|triage|diagnos|orientamento|educazione|insegnamento|tutoring|coaching"
    r"|supporto (a|alle|ai|conversazionale|tecnico e consulenza|all.accesso)"
    r"|identificazione delle vittime|prevenzione e risposta alla tratta|investigazione dei casi di tratta"
    r"|accoglienza e screening|intake|dispatch delle emergenze|allerta precoce e azione anticipatoria"
    r"|accesso a (diagnostica|servizi|cure)|connessione dei pazienti|indirizzamento"
    r"|produzione di apparecchi acustici|imaging cardiaco|interpretazione dell.attivit[aà] cardiaca"
    r"|diagnostica di laboratorio|diagnosi di malattie|screening del cancro|screening diagnostico"
    r"|verifica fattuale|risposta rapida alle emergenze|iscrizione e indirizzamento"
    r"|caregiver|cura domiciliare|supporto conversazionale alle vittime"
    r"|erogazione di contenuti sanitari|informazioni sanitarie tramite lavoratrici comunitarie"
    r"|informazioni finanziarie e climatiche|accesso al credito|verifica dell.identit[aà] per piccoli agricoltori"
    r"|prevenzione della tratta di esseri umani nelle offerte di lavoro"
    r"|informazioni giuridiche e supporto all.advocacy"
)

still_unresolved = []
reclass_existing = collections.Counter()
new_diretta = 0

for r in rows:
    if r['Funzione_organizzativa_Tags'].strip() != 'NON_CLASSIFICATO':
        continue
    testo = r['Processo_organizzativo']
    esiste = try_existing(testo)
    if esiste:
        r['Funzione_organizzativa_Tags'] = esiste
        reclass_existing[esiste] += 1
    elif DIRETTA_KW.search(testo.lower()):
        r['Funzione_organizzativa_Tags'] = 'Erogazione diretta'
        new_diretta += 1
    else:
        still_unresolved.append((r['ID_caso'], testo))

print(f"Riclassificati su categoria ESISTENTE (bug/pattern mancante nel tagger originale): {sum(reclass_existing.values())}")
for k, v in reclass_existing.most_common():
    print(f"  {v:3d}  -> {k}")
print(f"\nEtichettati 'Erogazione diretta' (nuova categoria): {new_diretta}")
print(f"\nAncora NON_CLASSIFICATO (nessuna corrispondenza sicura, da rivedere manualmente): {len(still_unresolved)}")
for id_, txt in still_unresolved:
    print(f"  {id_} | {txt}")

with open(IN_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nFile riscritto: {IN_FILE}")
