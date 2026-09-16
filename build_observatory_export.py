# -*- coding: utf-8 -*-
"""
build_observatory_export.py

Rigenera osservatorio_ai_terzo_settore.html a partire da:
  1. knowledge_layer/nodes/*.csv + relationships.csv  (dati aggiornati)
  2. compute_observatory.py                            (calcola le statistiche -> observatory_data.json)
  3. osservatorio_template.html                        (template con placeholder __OBSERVATORY_DATA_JSON__)

Uso analogo a come build_graph_export.py + knowledge_graph_template.html
generano knowledge_graph.html: qui non serve piu' copiare a mano il JSON
dentro l'HTML dell'Osservatorio.

Esecuzione:
    python3 compute_observatory.py        # aggiorna observatory_data.json
    python3 build_observatory_export.py   # inietta il JSON nel template e scrive l'HTML finale
"""
import json
import sys

TEMPLATE = "osservatorio_template.html"
DATA = "observatory_data.json"
OUTPUT = "osservatorio_ai_terzo_settore.html"
PLACEHOLDER = "__OBSERVATORY_DATA_JSON__"


def main():
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)  # valida che il JSON sia corretto

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()

    if PLACEHOLDER not in template:
        sys.exit(f"ERRORE: placeholder '{PLACEHOLDER}' non trovato in {TEMPLATE}. "
                  f"Il template potrebbe essere stato modificato manualmente: controllare prima di procedere.")

    if template.count(PLACEHOLDER) != 1:
        sys.exit(f"ERRORE: il placeholder compare {template.count(PLACEHOLDER)} volte, atteso 1.")

    data_json_compact = json.dumps(data, ensure_ascii=False, indent=1)
    output_html = template.replace(PLACEHOLDER, data_json_compact)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(output_html)

    print(f"Fatto. {OUTPUT} rigenerato da {TEMPLATE} + {DATA}.")
    print(f"Dimensione file: {len(output_html)} caratteri.")


if __name__ == "__main__":
    main()
