# -*- coding: utf-8 -*-
import csv, collections, json

ND = 'knowledge_layer/nodes/'
RL = 'knowledge_layer/relationships/relationships.csv'

def load_nodes(fname):
    with open(ND + fname, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_rels():
    with open(RL, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

impl = load_nodes('implementazioni.csv')
orgs = {r['id']: r for r in load_nodes('organizzazioni.csv')}
countries = {r['id']: r for r in load_nodes('paesi.csv')}
categories = {r['id']: r for r in load_nodes('categorie_organizzative.csv')}
techniques = {r['id']: r for r in load_nodes('tecniche_ia.csv')}
vendors = {r['id']: r for r in load_nodes('fornitori.csv')}
functions = {r['id']: r for r in load_nodes('funzioni_organizzative.csv')}
sectors = {r['id']: r for r in load_nodes('settori_missione.csv')}
benefits = {r['id']: r for r in load_nodes('benefici.csv')}
criticities = {r['id']: r for r in load_nodes('criticita.csv')}
programs = {r['id']: r for r in load_nodes('programmi.csv')}
beneficiary_types = {r['id']: r for r in load_nodes('tipi_beneficiario.csv')}
oversight_types = {r['id']: r for r in load_nodes('tipi_supervisione_umana.csv')}
collaborators = {r['id']: r for r in load_nodes('collaboratori.csv')}
impl_by_id = {r['id']: r for r in impl}

rels = load_rels()
by_type = collections.defaultdict(list)
for r in rels:
    by_type[r['Relationship_Type']].append(r)

out = {}

# 1. Tecniche IA piu' diffuse
c = collections.Counter(r['Target_Node_ID'] for r in by_type['USA_TECNICA'])
out['tecniche_diffuse'] = [{"nome": techniques[tid]['nome'], "n": n, "pct": round(100*n/389,1)} for tid,n in c.most_common(10)]

# 2. Tecniche associate a servizi rivolti ai beneficiari finali (vs interno)
missione_id = [k for k,v in beneficiary_types.items() if v['nome']=='Beneficiario finale della missione'][0]
impl_missione = set(r['Source_Node_ID'] for r in by_type['HA_BENEFICIARIO'] if r['Target_Node_ID']==missione_id)
tec_by_impl = collections.defaultdict(set)
for r in by_type['USA_TECNICA']:
    tec_by_impl[r['Source_Node_ID']].add(r['Target_Node_ID'])
c_missione = collections.Counter()
for iid in impl_missione:
    for tid in tec_by_impl.get(iid, []):
        c_missione[tid]+=1
out['tecniche_beneficiari_finali'] = [{"nome": techniques[tid]['nome'], "n": n, "pct_su_missione": round(100*n/len(impl_missione),1)} for tid,n in c_missione.most_common(8)]
out['n_implementazioni_beneficiario_finale'] = len(impl_missione)

# 3. Cooperative vs Fondazioni
def category_org_ids(catname):
    catid = [k for k,v in categories.items() if v['nome']==catname][0]
    return set(r['Source_Node_ID'] for r in by_type['HA_TIPO'] if r['Target_Node_ID']==catid)
coop_orgs = category_org_ids('Cooperativa sociale')
found_orgs = category_org_ids('Fondazione')
def impls_of_orgs(orgset):
    return set(r['Target_Node_ID'] for r in by_type['HA_IMPLEMENTAZIONE'] if r['Source_Node_ID'] in orgset)
coop_impls = impls_of_orgs(coop_orgs)
found_impls = impls_of_orgs(found_orgs)
def top_tec(implset, n=5):
    cc = collections.Counter()
    for r in by_type['USA_TECNICA']:
        if r['Source_Node_ID'] in implset:
            cc[techniques[r['Target_Node_ID']]['nome']] += 1
    return cc.most_common(n)
out['cooperative_vs_fondazioni'] = {
    "cooperative": {"n_org": len(coop_orgs), "n_impl": len(coop_impls), "top_tecniche": top_tec(coop_impls)},
    "fondazioni": {"n_org": len(found_orgs), "n_impl": len(found_impls), "top_tecniche": top_tec(found_impls)},
}

# 4. Organizzazioni con piu' implementazioni
c = collections.Counter(r['Source_Node_ID'] for r in by_type['HA_IMPLEMENTAZIONE'])
multi = [(orgs[oid]['nome'], n) for oid,n in c.items() if n>1]
multi.sort(key=lambda x:-x[1])
out['organizzazioni_multi_implementazione'] = [{"nome": nome, "n": n} for nome,n in multi[:12]]
out['n_organizzazioni_multi_implementazione'] = len(multi)

# 5. Fornitori che ricorrono in piu' settori
vendor_sectors = collections.defaultdict(set)
impl_sectors = collections.defaultdict(set)
for r in by_type['INDIRIZZA_SETTORE']:
    impl_sectors[r['Source_Node_ID']].add(r['Target_Node_ID'])
for r in by_type['USA_FORNITORE']:
    iid = r['Source_Node_ID']
    for sid in impl_sectors.get(iid, []):
        vendor_sectors[r['Target_Node_ID']].add(sid)
vs = [(vendors[vid]['nome'], len(s)) for vid,s in vendor_sectors.items()]
vs.sort(key=lambda x:-x[1])
out['fornitori_multi_settore'] = [{"nome": n, "n_settori": s} for n,s in vs[:10]]

# 6. Paesi con maggiore varieta' di utilizzi IA
country_tec = collections.defaultdict(set)
impl_countries = collections.defaultdict(set)
for r in by_type['IMPLEMENTATO_IN']:
    impl_countries[r['Source_Node_ID']].add(r['Target_Node_ID'])
for r in by_type['USA_TECNICA']:
    iid = r['Source_Node_ID']
    for cid in impl_countries.get(iid, []):
        country_tec[cid].add(r['Target_Node_ID'])
ct = [(countries[cid]['nome'], len(s)) for cid,s in country_tec.items()]
ct.sort(key=lambda x:-x[1])
out['paesi_varieta_tecniche'] = [{"nome": n, "n_tecniche": s} for n,s in ct[:10]]

# 7. Combinazioni Categoria+Funzione+Tecnica piu' comuni
org_cat = {}
for r in by_type['HA_TIPO']:
    org_cat[r['Source_Node_ID']] = categories[r['Target_Node_ID']]['nome']
impl_org = {}
for r in by_type['HA_IMPLEMENTAZIONE']:
    impl_org[r['Target_Node_ID']] = r['Source_Node_ID']
impl_func = collections.defaultdict(set)
for r in by_type['HA_FUNZIONE']:
    impl_func[r['Source_Node_ID']].add(functions[r['Target_Node_ID']]['nome'])
combo_counter = collections.Counter()
for iid in impl_by_id:
    oid = impl_org.get(iid)
    cat = org_cat.get(oid, None)
    if not cat: continue
    for func in impl_func.get(iid, []):
        for tid in tec_by_impl.get(iid, []):
            combo_counter[(cat, func, techniques[tid]['nome'])] += 1
out['combinazioni_frequenti'] = [{"categoria": c1, "funzione": c2, "tecnica": c3, "n": n} for (c1,c2,c3),n in combo_counter.most_common(10)]

# 8. Programmi di finanziamento ricorrenti
c = collections.Counter(r['Target_Node_ID'] for r in by_type['FA_PARTE_DI'])
out['programmi_ricorrenti'] = [{"nome": programs[pid]['nome'], "n": n} for pid,n in c.most_common(10)]

# 9. Livello di supervisione umana
c = collections.Counter(r['Target_Node_ID'] for r in by_type['COINVOLGE_UMANO'])
out['supervisione_umana'] = [{"nome": oversight_types[tid]['nome'], "n": n, "pct": round(100*n/389,1)} for tid,n in c.most_common()]

# 10. Chi beneficia
c = collections.Counter(r['Target_Node_ID'] for r in by_type['HA_BENEFICIARIO'])
out['tipo_beneficiario'] = [{"nome": beneficiary_types[tid]['nome'], "n": n, "pct": round(100*n/389,1)} for tid,n in c.most_common()]

# 11. Collaborazioni multi-stakeholder
collab_impls = set(r['Source_Node_ID'] for r in by_type['REALIZZATO_CON'])
c = collections.Counter(r['Target_Node_ID'] for r in by_type['REALIZZATO_CON'])
out['collaborazioni'] = {
    "n_implementazioni_con_collaboratore": len(collab_impls),
    "pct": round(100*len(collab_impls)/389,1),
    "top_collaboratori": [{"nome": collaborators[cid]['nome'], "n": n} for cid,n in c.most_common(10)]
}

# 12. Distribuzione dimensione organizzativa
c = collections.Counter(o['Dimensione'] for o in orgs.values())
out['dimensione_organizzativa'] = [{"nome": k, "n": v, "pct": round(100*v/len(orgs),1)} for k,v in c.most_common()]

# 13. Settori missione piu' indirizzati
c = collections.Counter(r['Target_Node_ID'] for r in by_type['INDIRIZZA_SETTORE'])
out['settori_missione_diffusi'] = [{"nome": sectors[sid]['nome'], "n": n, "pct": round(100*n/389,1)} for sid,n in c.most_common(10)]

# 14. Anno / trend temporale
c = collections.Counter(r['Anno'] for r in impl if r['Anno'])
out['trend_anno'] = sorted([{"anno": a, "n": n} for a,n in c.items() if a.isdigit()], key=lambda x: x['anno'])

# meta
out['meta'] = {
    "n_implementazioni": len(impl),
    "n_organizzazioni": len(orgs),
    "n_paesi": len(countries),
    "n_tecniche": len(techniques),
    "n_fornitori": len(vendors),
    "n_fonti": len(load_nodes('fonti.csv')),
    "data_costruzione": "2026-08-24",
}

with open('/sessions/wonderful-focused-faraday/mnt/outputs/observatory_data.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("Fatto.")
for k in out:
    print(" -", k)
