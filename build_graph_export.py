#!/usr/bin/env python3
"""
build_graph_export.py

Esporta una versione pubblica e sanitizzata del knowledge graph (knowledge_layer/)
per la visualizzazione interattiva statica (knowledge_graph.html), senza dipendere
da un'istanza Neo4j live.

Privacy: il nodo Implementazione nel corpus interno porta campi di testo libero
(Problema, Obiettivo, Sottoprocesso, Workflow_dettagliato, Input, Output,
Ruolo_umano, Osservazioni, Fallimenti) che in alcuni record nominano persone reali
in contesti sensibili (superstiti di violenza, rifugiati, pazienti) — la stessa
ragione per cui knowledge_layer/nodes/ e knowledge_layer/relationships/ sono
esclusi da .gitignore. Questo script NON include mai quei campi nell'export
pubblico: solo proprieta' strutturate/categoriali (Anno, Stato, livelli di
integrazione/prova/confidenza, fonte qualificata) che sono gia' pubbliche altrove
nel repository (indice_fonti.csv, osservatorio).

Tutti gli altri tipi di nodo (Organizzazione, Paese, TecnicaIA, Beneficio,
Criticita, Fornitore, ecc.) hanno solo id/label/nome nel CSV sorgente: nessun
campo di testo libero da filtrare, gia' sicuri per costruzione.
"""

import csv
import datetime
import json
import os

BASE = "knowledge_layer"
NODES_DIR = os.path.join(BASE, "nodes")
REL_FILE = os.path.join(BASE, "relationships", "relationships.csv")
OUT_FILE = "graph_data.json"
TEMPLATE_FILE = "knowledge_graph_template.html"
HTML_OUT_FILE = "knowledge_graph.html"

# Campi di testo libero SEMPRE esclusi dal nodo Implementazione (dati sensibili)
IMPLEMENTAZIONE_EXCLUDE = {
    "Problema", "Obiettivo", "Sottoprocesso", "Workflow_dettagliato",
    "Input", "Output", "Ruolo_umano", "Osservazioni", "Fallimenti",
}

# File nodo -> (label da usare, se diverso dalla colonna 'label' nel CSV)
NODE_FILES = [
    "benefici.csv", "categorie_organizzative.csv", "collaboratori.csv",
    "criticita.csv", "fonti.csv", "fornitori.csv", "funzioni_organizzative.csv",
    "implementazioni.csv", "modelli_ia.csv", "organizzazioni.csv", "paesi.csv",
    "programmi.csv", "settori_missione.csv", "software.csv", "tecniche_ia.csv",
    "tipi_beneficiario.csv", "tipi_supervisione_umana.csv",
]


def load_nodes():
    nodes = {}
    for fname in NODE_FILES:
        path = os.path.join(NODES_DIR, fname)
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_id = row["id"]
                node_type = row["label"]
                props = {}
                for k, v in row.items():
                    if k in ("id", "label", "nome"):
                        continue
                    if node_type == "Implementazione" and k in IMPLEMENTAZIONE_EXCLUDE:
                        continue
                    if v is None or v == "":
                        continue
                    props[k] = v
                nodes[node_id] = {
                    "id": node_id,
                    "type": node_type,
                    "name": row.get("nome", node_id),
                    "props": props,
                }
    return nodes


def load_edges():
    edges = []
    with open(REL_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges.append({
                "source": row["Source_Node_ID"],
                "target": row["Target_Node_ID"],
                "type": row["Relationship_Type"],
            })
    return edges


def friendly_implementazione_names(nodes, edges):
    """Sostituisce il nome (id grezzo TS-AI-xxxxx) delle Implementazioni con
    'Nome organizzazione (Anno)', usando l'edge HA_IMPLEMENTAZIONE."""
    impl_to_org = {}
    for e in edges:
        if e["type"] == "HA_IMPLEMENTAZIONE":
            impl_to_org[e["target"]] = e["source"]

    for node_id, node in nodes.items():
        if node["type"] != "Implementazione":
            continue
        org_id = impl_to_org.get(node_id)
        org_name = nodes.get(org_id, {}).get("name") if org_id else None
        anno = node["props"].get("Anno", "")
        if org_name:
            node["name"] = f"{org_name} ({anno})" if anno else org_name
        # comunque teniamo l'id originale visibile come proprieta'
        node["props"]["ID_caso"] = node_id


def main():
    nodes = load_nodes()
    edges = load_edges()
    friendly_implementazione_names(nodes, edges)

    # scarta edge che puntano a nodi non presenti (robustezza)
    node_ids = set(nodes.keys())
    clean_edges = [e for e in edges if e["source"] in node_ids and e["target"] in node_ids]

    type_counts = {}
    for n in nodes.values():
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1

    out = {
        "generated": datetime.date.today().isoformat(),
        "n_nodes": len(nodes),
        "n_edges": len(clean_edges),
        "type_counts": type_counts,
        "nodes": list(nodes.values()),
        "edges": clean_edges,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(OUT_FILE) / 1024
    print(f"Nodi: {len(nodes)} | Archi: {len(clean_edges)} (scartati {len(edges) - len(clean_edges)})")
    print(f"Tipi di nodo: {type_counts}")
    print(f"File scritto: {OUT_FILE} ({size_kb:.1f} KB)")

    # Rigenera anche knowledge_graph.html iniettando i dati aggiornati nel template
    # (stesso pattern di osservatorio_ai_terzo_settore.html: script id="graph-data").
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, encoding="utf-8") as f:
            tpl = f.read()
        html = tpl.replace("__GRAPH_DATA_JSON__", json.dumps(out, ensure_ascii=False, separators=(",", ":")))
        with open(HTML_OUT_FILE, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"File scritto: {HTML_OUT_FILE} ({os.path.getsize(HTML_OUT_FILE)/1024:.1f} KB)")
    else:
        print(f"ATTENZIONE: {TEMPLATE_FILE} non trovato, knowledge_graph.html non rigenerato.")


if __name__ == "__main__":
    main()
