# -*- coding: utf-8 -*-
"""
build_casi_export.py — produce casi.json: un record piatto per ciascun caso.

PERCHE': graph_data.json e' strutturato come grafo (nodi + archi) ed e' giusto cosi'
per la visualizzazione a rete, ma un catalogo consultabile e una ricerca testuale
hanno bisogno di un elenco piatto, dove ogni caso porta con se' tutto quello che
serve a trovarlo e a leggerlo. casi.json e' quell'elenco, generato dagli stessi
dati: nessuna duplicazione a mano, nessuna possibilita' di divergenza.

CONTIENE: i campi dell'Implementazione, inclusi i nove campi descrittivi aperti al
pubblico il 2026-10-20, piu' le entita' collegate gia' risolte in nomi leggibili
(organizzazione, paese, funzione, settore, tecnica, fornitore, tipo di beneficiario,
tipo di supervisione umana, fonti).

ORDINE NELLA PIPELINE: dopo build_knowledge_layer.py, insieme a build_graph_export.py.
COME: python3 build_casi_export.py
"""
import csv, json, collections

ND = 'knowledge_layer/nodes/'
RL = 'knowledge_layer/relationships/relationships.csv'
OUT = 'casi.json'

def nodi(f):
    with open(ND + f, newline='', encoding='utf-8') as x:
        return {r['id']: r for r in csv.DictReader(x)}

impl = nodi('implementazioni.csv')
orgs = nodi('organizzazioni.csv')
mappe = {
    'paesi':        ('paesi.csv', 'IMPLEMENTATO_IN', 'paesi'),
    'funzioni':     ('funzioni_organizzative.csv', 'HA_FUNZIONE', 'funzioni'),
    'settori':      ('settori_missione.csv', 'INDIRIZZA_SETTORE', 'settori'),
    'tecniche':     ('tecniche_ia.csv', 'USA_TECNICA', 'tecniche'),
    'fornitori':    ('fornitori.csv', 'USA_FORNITORE', 'fornitori'),
    'beneficiari':  ('tipi_beneficiario.csv', 'HA_BENEFICIARIO', 'beneficiari'),
    'supervisione': ('tipi_supervisione_umana.csv', 'COINVOLGE_UMANO', 'supervisione'),
    'benefici':     ('benefici.csv', 'RIPORTA_BENEFICIO', 'benefici'),
    'criticita':    ('criticita.csv', 'RIPORTA_CRITICITA', 'criticita'),
    'fonti':        ('fonti.csv', 'DOCUMENTATO_DA', 'fonti'),
}
dizionari = {k: nodi(v[0]) for k, v in mappe.items()}

with open(RL, newline='', encoding='utf-8') as f:
    rels = list(csv.DictReader(f))

collegati = {k: collections.defaultdict(list) for k in mappe}
org_di = {}
for r in rels:
    t = r['Relationship_Type']
    if t == 'HA_IMPLEMENTAZIONE':
        org_di[r['Target_Node_ID']] = r['Source_Node_ID']
        continue
    for chiave, (_, tipo, _) in mappe.items():
        if t == tipo:
            nome = dizionari[chiave].get(r['Target_Node_ID'], {}).get('nome')
            if nome and nome not in collegati[chiave][r['Source_Node_ID']]:
                collegati[chiave][r['Source_Node_ID']].append(nome)

casi = []
for iid, rec in impl.items():
    org = orgs.get(org_di.get(iid, ''), {})
    caso = {k: v for k, v in rec.items() if k not in ('label',) and v}
    caso['organizzazione'] = org.get('nome', '')
    caso['tipo_organizzazione'] = org.get('Tipo_organizzazione', '')
    caso['dimensione_organizzazione'] = org.get('Dimensione', '')
    for chiave in mappe:
        caso[chiave] = collegati[chiave].get(iid, [])
    casi.append(caso)

casi.sort(key=lambda c: c.get('id', ''))
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump({'generato': __import__('datetime').date.today().isoformat(),
               'n_casi': len(casi), 'casi': casi}, f, ensure_ascii=False, indent=1)

import os
print(f"Scritto {OUT}: {len(casi)} casi, {os.path.getsize(OUT)/1024:.0f} KB")
print("campi per caso:", len(casi[0]))
