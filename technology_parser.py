# -*- coding: utf-8 -*-
"""
STEP 1 (estensione) - Normalizzazione additiva multi-tag per Tecnologia_utilizzata /
Modello_AI / Software_utilizzato.

A differenza di Tipologia_organizzativa (categoria singola), questi 3 campi sono
descrizioni tecniche quasi-uniche (364/345/374 valori distinti su 389 record) e
Modello_AI/Software_utilizzato si sovrappongono largamente come concetto (nome
prodotto/piattaforma). Per questo l'estensione usa 2 dimensioni additive multi-tag
anziche' 3 tassonomie a categoria singola parallele:

- Tecnica_IA_Tags: tecnica/metodo IA (estratta dal contesto completo del record:
  Tecnologia_utilizzata, Tipo_utilizzo_IA, Workflow_dettagliato, Modello_AI,
  Software_utilizzato, Obiettivo_implementazione - non solo dal singolo campo
  Tecnologia_utilizzata, perche' spesso la tecnica e' resa esplicita altrove nel
  record anche quando Tecnologia_utilizzata resta generica).
- Fornitore_Piattaforma_Tags: fornitore/piattaforma nominata (estratta da
  Tecnologia_utilizzata + Modello_AI + Software_utilizzato).

Entrambi multi-label (piu' tag per record, separati da '; '). Valori originali dei
3 campi non modificati.
"""
import re
import csv
import json
import collections

TECNICA_TAGS = [
    ("Chatbot conversazionale", r"chatbot|conversazional|assistente virtuale"),
    ("AI generativa / LLM", r"\bllm\b|generativ|large language model|\bgpt\b|claude|modello linguistic|digital human|avatar digital|generazione (di contenuti|automatizzata|di documenti|di testo|di piani)"),
    ("NLP (testo)", r"\bnlp\b|elaborazione del linguaggio naturale|named entity recognition|analisi (del )?testo|traduzion"),
    ("Computer vision / analisi immagini", r"computer vision|immagini (satellitari|aeree|radiografich|etichettate)|riconoscimento (di )?immagini|riconoscimento facciale|analisi di foto|foto aeree|visione artificiale|fotografie|sensori (infrarossi|multispettral)|fotomosaic|stitching"),
    ("Riconoscimento vocale / audio", r"riconoscimento (ottico|vocale)|\bocr\b|speech-to-text|trascrizione automatica|pattern (acustici|sonori)|bioacustic|analisi (di segnali )?audio"),
    ("Machine learning predittivo", r"machine learning predittivo|\bml predittivo\b|modello predittivo|propensity|previsione|forecasting|analisi predittiva|lookalike"),
    ("Machine learning (generico)", r"machine learning|apprendimento automatico"),
    ("Agentic AI / agenti AI", r"agentic|agente ai|agenti ai"),
    ("Reinforcement learning / bandit", r"reinforcement|apprendimento per rinforzo|bandit"),
    ("Sistema di raccomandazione / matching", r"raccomandazione|recommender|sistema esperto|geomatch|matching"),
    ("Automazione/RPA/orchestrazione", r"\brpa\b|automazione (documentale|di processo|istantanea|workflow)|robotic process automation|orchestrazione"),
    ("Analisi geospaziale", r"geospazial|dati satellitari|analisi satellitare"),
    ("Scoring/classificazione automatica", r"scoring|classificazione (automatica|di contenuti)|ranking|catalogazione automatizzata"),
    ("Ottimizzazione algoritmica", r"ottimizzazione|integer optimization|algoritmo di (ranking|matching)"),
]

VENDOR_TAGS = [
    ("Salesforce (Agentforce/Einstein)", r"salesforce|agentforce|einstein"),
    ("Microsoft (Copilot/Azure)", r"microsoft|copilot|azure"),
    ("Google (Gemini/DeepMind/Vertex)", r"\bgoogle\b|gemini|deepmind|vertex ai"),
    ("Amazon/AWS (Bedrock/Personalize)", r"\baws\b|amazon|bedrock"),
    ("OpenAI (GPT/ChatGPT)", r"openai|\bgpt\b|chatgpt"),
    ("Anthropic (Claude)", r"anthropic|\bclaude\b"),
    ("IBM (Watson/Garage)", r"\bibm\b|watson"),
    ("Proprietario/sviluppato internamente", r"propriet|sviluppat[oa] (internamente|dal team|dal ceo)|in-house|interno all'organizzazione"),
    ("Open source", r"open source|open-source"),
]

GENERIC_AI_MENTION = r"intelligenza artificiale|\bai\b|\bia\b"


def classify_record(r):
    tecnica_context = ' '.join([
        r.get('Tecnologia_utilizzata', ''), r.get('Tipo_utilizzo_IA', ''),
        r.get('Workflow_dettagliato', ''), r.get('Modello_AI', ''),
        r.get('Software_utilizzato', ''), r.get('Obiettivo_implementazione', ''),
    ]).lower()

    tecnica_tags = [tag for tag, pat in TECNICA_TAGS if re.search(pat, tecnica_context)]
    review = "NO"
    if not tecnica_tags:
        # fallback: alcuni record descrivono l'IA con termini impliciti nei campi
        # tecnici principali (es. "intelligence ambientale", "supporto decisionale
        # automatizzato") senza il token letterale AI/IA in quei campi; prima di
        # marcare NON_CLASSIFICATO si allarga il contesto a Problema_affrontato e
        # Osservazioni, dove il case study descrive esplicitamente la natura IA
        # del progetto (tutti i record del corpus soddisfano il criterio di
        # inclusione esplicita di IA/ML a monte della raccolta originale).
        wide_context = tecnica_context + ' ' + r.get('Problema_affrontato', '').lower() + ' ' + r.get('Osservazioni', '').lower()
        if re.search(GENERIC_AI_MENTION, wide_context):
            tecnica_tags = ["IA generica / non specificata"]
        else:
            tecnica_tags = ["NON_CLASSIFICATO"]
            review = "YES"

    vendor_context = ' '.join([
        r.get('Tecnologia_utilizzata', ''), r.get('Modello_AI', ''), r.get('Software_utilizzato', ''),
    ]).lower()
    vendor_tags = [tag for tag, pat in VENDOR_TAGS if re.search(pat, vendor_context)]
    if not vendor_tags:
        vendor_tags = ["Non specificato / non nominato"]

    return {
        "ID_caso": r["ID_caso"],
        "Organizzazione": r["Organizzazione"],
        "Tecnologia_originale": r["Tecnologia_utilizzata"],
        "Modello_originale": r["Modello_AI"],
        "Software_originale": r["Software_utilizzato"],
        "Tecnica_IA_Tags": "; ".join(tecnica_tags),
        "Fornitore_Piattaforma_Tags": "; ".join(vendor_tags),
        "Requires_Human_Review_Tech": review,
    }


if __name__ == "__main__":
    with open("database_casi.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [classify_record(r) for r in rows]

    tecnica_counts = collections.Counter()
    for res in results:
        for t in res["Tecnica_IA_Tags"].split("; "):
            tecnica_counts[t] += 1

    vendor_counts = collections.Counter()
    for res in results:
        for t in res["Fornitore_Piattaforma_Tags"].split("; "):
            vendor_counts[t] += 1

    n_review = sum(1 for res in results if res["Requires_Human_Review_Tech"] == "YES")

    print("Record totali:", len(results))
    print("\nDistribuzione Tecnica_IA_Tags:")
    for k, v in tecnica_counts.most_common():
        print(f"  {v:4d}  {k}")
    print("\nDistribuzione Fornitore_Piattaforma_Tags:")
    for k, v in vendor_counts.most_common():
        print(f"  {v:4d}  {k}")
    print("\nRecord NON_CLASSIFICATO (revisione umana):", n_review)

    with open("technology_audit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ID_caso", "Organizzazione", "Tecnologia_originale",
                                          "Modello_originale", "Software_originale",
                                          "Tecnica_IA_Tags", "Fornitore_Piattaforma_Tags",
                                          "Requires_Human_Review_Tech"])
        w.writeheader()
        w.writerows(results)

    with open("technology_classification_map.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
