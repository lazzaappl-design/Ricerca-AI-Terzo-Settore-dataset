# -*- coding: utf-8 -*-
"""
STEP 1 - Normalizzazione di Tipologia_organizzativa in due livelli additivi:
- Categoria_organizzativa: vocabolario controllato piccolo, funzionale (non giuridico),
  costruito dal basso osservando le forme ricorrenti nei 393 valori (354 distinti).
- Status_legale_specifico: forma giuridica puntuale quando esplicitamente presente nel
  testo (es. 501(c)(3), ONLUS/ETS, Asociacion Civil, ANBI, charity UK, Stiftung, ecc.),
  altrimenti NOT_AVAILABLE. Non inventato, non dedotto da paese.
Il valore originale (Tipologia_originale) è sempre preservato.
"""
import re
import csv
import collections

# Ordine di priorità: pattern più specifici prima. Ogni voce: (Categoria, [regex case-insensitive])
CATEGORY_RULES = [
    ("Società nazionale Croce Rossa/Mezzaluna Rossa", [r"croce rossa", r"mezzaluna rossa", r"red cross", r"red crescent", r"\bifrc\b"]),
    ("Organizzazione internazionale/intergovernativa", [r"agenzia (delle nazioni unite|onu)", r"\bonu\b", r"\bwho\b", r"organizzazione mondiale della sanit", r"intergovernativ"]),
    ("Cooperativa sociale", [r"cooperativa sociale", r"cooperativa"]),
    ("Impresa sociale", [r"impresa sociale", r"social enterprise", r"social business"]),
    ("Fondazione", [r"fondazione", r"foundation", r"fundaci[oó]n", r"stiftung"]),
    ("Ente religioso/caritativo", [r"\bcharity\b", r"ente religioso", r"caritat", r"ente ecclesiastico", r"congregazione"]),
    ("Rete/Coalizione/Consorzio", [r"\brete\b", r"coalizione", r"consorzio", r"alleanza", r"network", r"alliance"]),
    ("Organizzazione di ricerca no-profit", [r"organizzazione di ricerca", r"centro di ricerca no-?profit", r"research organization"]),
    ("Organizzazione della società civile", [r"societ[aà] civile", r"civil society"]),
    ("Associazione", [r"associazione", r"asociaci[oó]n", r"association\b", r"aps\b", r"aisbl"]),
    ("ONG / organizzazione non governativa", [r"\bong\b", r"\bngo\b", r"organizzazione non governativa", r"nonprofit", r"non-profit", r"no-profit", r"no profit"]),
]

STATUS_PATTERNS = [
    ("501(c)(3) USA", r"501\s*\(?c\)?\s*\(?3\)?"),
    ("Charity registrata UK", r"charity\s*(commission|number|registrat\w*)|registered charity"),
    ("ONLUS/ETS Italia", r"\bonlus\b|\bets\b|ente del terzo settore"),
    ("Asociación Civil (diritto sudamericano)", r"asociaci[oó]n civil"),
    ("ANBI Paesi Bassi", r"\banbi\b"),
    ("Stiftung/diritto tedesco-svizzero", r"\bstiftung\b|gGmbH"),
    ("Legge 1901 Francia", r"loi 1901|legge 1901"),
    ("Public Benefit Corporation (PBC)", r"\bpbc\b|public benefit corporation"),
    ("Charity Company Limited by Guarantee UK", r"limited by guarantee"),
    ("Registrazione governativa esplicita (altro)", r"registrat[ao] (come|presso|dal|con)|status confermato|EIN \d"),
]


def classify(text):
    t = text.strip()
    tl = t.lower()

    category = None
    for cat, patterns in CATEGORY_RULES:
        if any(re.search(p, tl) for p in patterns):
            category = cat
            break

    status = "NOT_AVAILABLE"
    for label, pat in STATUS_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            status = label
            break

    review = "NO"
    if category is None:
        category = "NON_CLASSIFICATO"
        review = "YES"

    return {
        "Tipologia_originale": t,
        "Categoria_organizzativa": category,
        "Status_legale_specifico": status,
        "Requires_Human_Review": review,
    }


if __name__ == "__main__":
    with open("database_casi.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    distinct = {}
    for r in rows:
        v = r["Tipologia_organizzativa"]
        if v not in distinct:
            distinct[v] = classify(v)

    cat_counts = collections.Counter(c["Categoria_organizzativa"] for c in distinct.values())
    status_counts = collections.Counter(c["Status_legale_specifico"] for c in distinct.values())
    n_review = sum(1 for c in distinct.values() if c["Requires_Human_Review"] == "YES")

    print("Valori distinti:", len(distinct))
    print("\nDistribuzione Categoria_organizzativa (per valore distinto):")
    for k, v in cat_counts.most_common():
        print(f"  {v:4d}  {k}")
    print("\nDistribuzione Status_legale_specifico (per valore distinto):")
    for k, v in status_counts.most_common():
        print(f"  {v:4d}  {k}")
    print("\nValori non classificati (NON_CLASSIFICATO):", n_review)

    with open("typology_classification_preview.tsv", "w", encoding="utf-8") as out:
        out.write("Tipologia_originale\tCategoria_organizzativa\tStatus_legale_specifico\tReview\n")
        for v, c in sorted(distinct.items()):
            out.write(f"{v}\t{c['Categoria_organizzativa']}\t{c['Status_legale_specifico']}\t{c['Requires_Human_Review']}\n")

    import json
    with open("typology_classification_map.json", "w", encoding="utf-8") as f:
        json.dump(distinct, f, ensure_ascii=False, indent=1)
