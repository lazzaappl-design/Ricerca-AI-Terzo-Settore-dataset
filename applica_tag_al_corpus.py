# -*- coding: utf-8 -*-
"""
applica_tag_al_corpus.py — scrive nel corpus i tag prodotti dalle regole di pbc_tagger.py.

PERCHE' ESISTE: fino al 2026-09-16 pbc_tagger.py produceva un file intermedio (pbc_audit.csv)
che andava "unito manualmente" al corpus con un copia-incolla. Quel passaggio manuale ha prodotto
una deriva silenziosa: i tag salvati nel corpus provenivano da una versione piu' vecchia delle
regole (38 record divergenti su Settore, Beneficio e Criticita' al momento della scoperta), senza
che nulla lo segnalasse. Questo script sostituisce il passaggio manuale, cosi' il corpus e le
regole non possono piu' separarsi. Vedi decisioni_fase0.md, decisione D12.

COSA FA: applica le regole di pbc_tagger.py ai campi sorgente del corpus e riscrive in place le
quattro colonne di tag, senza toccare nessun campo originale:
    Processo_organizzativo  -> Funzione_organizzativa_Tags
    Settore_attivita        -> Settore_missione_Tags
    Benefici_documentati    -> Beneficio_Tags
    Criticita_documentate   -> Criticita_Tags
Stampa un riepilogo dei record modificati rispetto ai valori precedenti, per non applicare mai
cambiamenti invisibili.

ORDINE NELLA PIPELINE: eseguire PRIMA di riclassifica_funzione_organizzativa.py, che interviene
sui casi NON_CLASSIFICATO della funzione organizzativa e va quindi applicato dopo il tagger.

COME: da terminale, dalla cartella del progetto:   python3 applica_tag_al_corpus.py
Riscrive il corpus in place: fare una copia di sicurezza prima di eseguirlo su dati non salvati.
Idempotente: rieseguirlo senza cambiare le regole lascia il file identico.

Prima stesura: 2026-09-16 (fase 0c).
"""
import csv
import importlib.util

CORPUS = "corpus_working_407rec_2026-09-16.csv"

spec = importlib.util.spec_from_file_location("pbc_tagger", "pbc_tagger.py")
pbc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pbc)

MAPPATURA = [
    ("Processo_organizzativo", "Funzione_organizzativa_Tags", pbc.PROC_TAGS),
    ("Settore_attivita",       "Settore_missione_Tags",       pbc.SETTORE_TAGS),
    ("Benefici_documentati",   "Beneficio_Tags",              pbc.BENEFIT_TAGS),
    ("Criticita_documentate",  "Criticita_Tags",              pbc.CRIT_TAGS),
]

with open(CORPUS, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    rows = list(reader)

print(f"Record letti: {len(rows)}")
for sorgente, colonna, tagset in MAPPATURA:
    if colonna not in fieldnames:
        fieldnames.append(colonna)
    cambiati = 0
    non_class_prima = sum(1 for r in rows if "NON_CLASSIFICATO" in r.get(colonna, ""))
    for r in rows:
        nuovo, _ = pbc.tag_field(r.get(sorgente, ""), tagset)
        if nuovo != r.get(colonna, ""):
            cambiati += 1
        r[colonna] = nuovo
    non_class_dopo = sum(1 for r in rows if "NON_CLASSIFICATO" in r[colonna])
    print(f"  {colonna:<32} record modificati: {cambiati:>4} | NON_CLASSIFICATO {non_class_prima} -> {non_class_dopo}")

with open(CORPUS, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nCorpus riscritto: {CORPUS} ({len(fieldnames)} colonne)")
print("Passo successivo della pipeline: python3 riclassifica_funzione_organizzativa.py")
