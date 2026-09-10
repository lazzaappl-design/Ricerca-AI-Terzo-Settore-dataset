# -*- coding: utf-8 -*-
"""
Dimensione additiva "Tipo_beneficiario_Tags" (chi riceve il beneficio
dell'implementazione IA), costruita con metodo bottom-up sui 389 record
(lettura Problema_affrontato + Obiettivo_implementazione + Benefici_documentati).

STORIA (per trasparenza metodologica):
- v1 (2026-08-24): 3 categorie via regex (diretto/utente finale, organizzazione/
  staff interno, causa ambientale/non umana) -> 60/389 (15%) NON_CLASSIFICATO.
- v2 (stessa sessione): ridotta a 2 label (diretto/esterno, indiretto/
  organizzazione), fondendo "diretto" e "causa ambientale" in una sola label;
  i 60 NON_CLASSIFICATO letti singolarmente e classificati per giudizio ->
  0 NON_CLASSIFICATO.
- v3 (stessa sessione, su richiesta esplicita dell'utente "fammi una proposta
  di classificazione alternativa" -> scelta Alternativa A, 3 livelli, con le
  varianti richieste "/PA" e "Organizzazione/interno"): la vecchia label
  "diretto/esterno" mescolava beneficiari finali della missione (persone,
  comunita', causa ambientale) con partner istituzionali esterni (aziende,
  governi, altre ONG-clienti di una piattaforma) - due categorie concettualmente
  diverse. Separate in 3 label definitive:
    1. "Beneficiario finale della missione"      (persone/comunita'/causa amb.)
    2. "Organizzazione/ente terzo/PA"            (aziende, governi, altre ONG,
                                                   agenzie pubbliche, media)
    3. "Organizzazione/interno"                  (staff/capacita'/costi/
                                                   sostenibilita' dell'org. che
                                                   ha realizzato l'implementazione)
  Tutti i 389 record riletti/riclassificati con questo schema (i 60 gia' letti
  manualmente in v2 sono stati riletti sotto la nuova lente a 3 vie; inoltre,
  rimuovendo i termini aziendali/PA dal pattern generico "esterno", sono emersi
  27 ulteriori record con match istituzionale tra quelli gia' auto-classificati:
  di questi, 10 richiedevano davvero il tag TERZO_PA dopo lettura individuale,
  17 erano falsi positivi lessicali e restano invariati). Risultato: ancora
  0 NON_CLASSIFICATO su 389.

Campo multi-tag: un record puo' avere piu' label contemporaneamente (es.
Croce Rossa Americana: beneficio interno di qualita' dati E migliore risposta
a comunita' colpite da disastro = missione + interno).
"""
import re

MISSIONE_PAT = re.compile(
    r"rifugiat|sfollat|richiedent[ie]( di)?( asilo)?|migrant|pazient[ei]|beneficiar|"
    r"utent[ei] final|famigli[ae]|bambin[oi]|minori( a rischio)?|"
    r"orfan[ei]|student[ei]( seguit)?|discent[ei]|comunit[aà]|"
    r"popolazion[ei]|person[ea] (colpit|vulnerabil|in difficolt|senza dimora|"
    r"con disabilit|in situazioni|affette|bisognose)|cittadin[ei]|donn[ae]|vittim[ea]|assistit[ei]|"
    r"clienti finali|persone in (coda|lista d'attesa)|malat[ei]|anziani|"
    r"disoccupat[ei]|persone senza (accesso|lavoro)|agricoltori|contadini|piccoli agricoltori|"
    r"veteran[ei]|sopravvissut[ei]|resident[ei]|giovani|lavoratric[ei]|lavorator[ei]|"
    r"caregiver|genitori|adolescent[ei]|coppie|inquilin[ei]|pubblico|disabili|"
    r"immigrat[ei]|detenut[ei]|incarcerat[ei]|ex-militari|senzatetto|coetane[oi]|badanti|colf|nanny|"
    r"abitanti|villaggi remoti|contesti a risorse limitate|paesi a reddito medio-basso|"
    r"fauna selvatica|biodiversit|barrier[ae] corallin|foreste|mangrovie|specie( animali)?|"
    r"ecosistem|pesca illegale|bracconaggio|disboscamento|incendi boschivi|emissioni di gas serra|"
    r"copertura arborea|orsi|uccelli|plastica oceanica|specie ittiche|habitat|conservazione"
)

TERZO_PA_PAT = re.compile(
    r"aziend[ae]|partner commercial[ei]|partner aziendal[ei]|govern[oi] (locale|municipale|regionale)|"
    r"ministero|agenzi[ae] (di sanit|governative)|ent[ei] pubblic|pubblica amministrazione|"
    r"comune di|amministrazion[ei] comunal|citt[aà] (di [A-Z]|indonesiane|secondari)|"
    r"altre organizzazioni no-?profit|organizzazioni no-?profit( clienti)?|redazioni|"
    r"organizzazioni mediatiche|istituzioni finanziarie|\bcdfi\b|imprese|"
    r"dipartimento (governativo|federale)|autorit[aà] (locali|governative)|"
    r"marchi|enti di settore|catena[e]? di fornitura"
)

INTERNAL_PAT = re.compile(
    r"person[ae]l[ei]|staff|team (interno|di)|operator[ei]( umano)?|volontari|dipendenti|"
    r"coach volontari|capacit[aà] organizzativ|processo (interno|manuale)|"
    r"produttivit[aà]( del personale| interna)?|efficienza operativa|tempo del personale|"
    r"carico di lavoro (del personale|interno|dei fact-checker)|analisti|case manager|fundraiser|donatori|"
    r"campagn[ae] (di )?(direct mail|raccolta fondi)|budget interno|risorse interne|"
    r"ricercatori|specialisti dei centri|team umanitari|operatrici sanitarie comunitarie|"
    r"finanziare l'organizzazione|sostenibilit[aà] finanziaria dell'organizzazione|"
    r"fonte di finanziamento per (l'organizzazione|crisis text line)|quota di ricavi"
)

MISSIONE = "Beneficiario finale della missione"
TERZO_PA = "Organizzazione/ente terzo/PA"
INTERNO = "Organizzazione/interno"

# Letture manuali (fase 2 e fase 3, 2026-08-24): ogni record e' stato letto per
# intero e classificato in base a CHI riceve concretamente il beneficio
# descritto - non solo tramite regex. Include sia i 60 casi non catturati dal
# pattern-matching sia 10 casi (su 27 riesaminati) in cui il pattern
# istituzionale TERZO_PA_PAT segnalava un beneficiario aziendale/PA reale
# tra i record gia' auto-classificati.
MANUAL_OVERRIDES = {
    "TS-AI-00009": [MISSIONE],
    "TS-AI-00021": [MISSIONE],
    "TS-AI-00024": [MISSIONE, INTERNO],
    "TS-AI-00038": [INTERNO],
    "TS-AI-00056": [TERZO_PA, MISSIONE],   # piccole ONG piu' visibilita' (terzo) + volontari abbinati equamente (missione)
    "TS-AI-00059": [MISSIONE],
    "TS-AI-00065": [MISSIONE],
    "TS-AI-00070": [MISSIONE, INTERNO],
    "TS-AI-00076": [MISSIONE],
    "TS-AI-00114": [MISSIONE],
    "TS-AI-00126": [TERZO_PA, MISSIONE],   # piccole imprese/forze dell'ordine (terzo) + vittime di tratta (missione)
    "TS-AI-00133": [TERZO_PA, MISSIONE],   # aziende clienti (terzo) + deforestazione/causa ambientale (missione)
    "TS-AI-00145": [MISSIONE],
    "TS-AI-00185": [TERZO_PA],             # aziende e responsabili politici, destinatari diretti del tool
    "TS-AI-00187": [TERZO_PA, INTERNO],    # marchi partner (Apple, Starbucks...) + tempo amministrativo personale
    "TS-AI-00192": [TERZO_PA, MISSIONE],   # governo locale Samarinda + resilienza cittadina
    "TS-AI-00196": [MISSIONE],
    "TS-AI-00205": [TERZO_PA, MISSIONE, INTERNO],  # aziende partner + studenti + personale
    "TS-AI-00210": [TERZO_PA],             # partner commerciali certificati Fair Trade
    "TS-AI-00212": [TERZO_PA],             # aziende partner Ceres
    "TS-AI-00220": [TERZO_PA, INTERNO],    # ricercatori accademici/industriali + personale ACS
    "TS-AI-00236": [TERZO_PA, MISSIONE],   # agenzie di sanita' pubblica + comunita' resilienti
    "TS-AI-00245": [MISSIONE, INTERNO],
    "TS-AI-00248": [MISSIONE],
    "TS-AI-00251": [MISSIONE],
    "TS-AI-00259": [MISSIONE],
    "TS-AI-00261": [MISSIONE],
    "TS-AI-00263": [MISSIONE],
    "TS-AI-00278": [MISSIONE],
    "TS-AI-00281": [MISSIONE],
    "TS-AI-00284": [MISSIONE],
    "TS-AI-00287": [MISSIONE],
    "TS-AI-00288": [MISSIONE],
    "TS-AI-00289": [MISSIONE],
    "TS-AI-00290": [MISSIONE],
    "TS-AI-00293": [MISSIONE],
    "TS-AI-00294": [MISSIONE],
    "TS-AI-00295": [TERZO_PA, MISSIONE],   # NIH (co-leadership) + salute pubblica
    "TS-AI-00296": [TERZO_PA, MISSIONE],   # organizzazioni no-profit BIPOC-led + comunita' BIPOC servite
    "TS-AI-00299": [MISSIONE],
    "TS-AI-00300": [MISSIONE],
    "TS-AI-00301": [MISSIONE],
    "TS-AI-00303": [TERZO_PA, MISSIONE],   # organizzazioni per i diritti umani (utenti diretti) + vittime (causa)
    "TS-AI-00306": [TERZO_PA],             # utenti non tecnici di organizzazioni no-profit/sociali
    "TS-AI-00308": [TERZO_PA],             # giornalisti/redazioni di fact-checking
    "TS-AI-00312": [TERZO_PA],             # organizzazioni mediatiche
    "TS-AI-00314": [TERZO_PA, MISSIONE],   # Ministero della Salute Indonesia + popolazione a rischio malaria
    "TS-AI-00315": [MISSIONE],
    "TS-AI-00319": [MISSIONE],
    "TS-AI-00326": [TERZO_PA],             # redazioni no-profit associate a INN
    "TS-AI-00329": [MISSIONE],
    "TS-AI-00330": [TERZO_PA, MISSIONE],   # citta'/governi locali (CityCatalyst) + causa climatica
    "TS-AI-00331": [INTERNO, MISSIONE],    # capacita' di ricerca di Stand.earth stessa + causa climatica
    "TS-AI-00337": [INTERNO, MISSIONE],    # carico fact-checker interni + disinformazione sanitaria pubblica
    "TS-AI-00338": [MISSIONE],
    "TS-AI-00342": [TERZO_PA, MISSIONE],   # aiutare i governi + richiedenti indennita' disoccupazione
    "TS-AI-00348": [TERZO_PA, MISSIONE],   # governi locali municipali + cittadini serviti
    "TS-AI-00352": [TERZO_PA],             # operatori sanitari comunitari Ruanda (forza lavoro esterna/PA)
    "TS-AI-00354": [MISSIONE],
    "TS-AI-00355": [MISSIONE],
    "TS-AI-00356": [MISSIONE],
    "TS-AI-00361": [MISSIONE],
    "TS-AI-00367": [MISSIONE],
    "TS-AI-00368": [TERZO_PA],             # aziende, decisori politici, dispositivi IoT
    "TS-AI-00377": [MISSIONE, TERZO_PA],   # donne vittime di violenza + sistema giudiziario/tribunali
    "TS-AI-00382": [TERZO_PA],             # marchi, enti di settore, societa' civile (utenti della piattaforma)
    "TS-AI-00385": [TERZO_PA, MISSIONE],   # CDFI (istituzioni finanziarie) + comunita' storicamente svantaggiate
    "TS-AI-00392": [TERZO_PA, MISSIONE],   # organizzazioni umanitarie/autorita' locali + comunita' in crisi
    "TS-AI-00393": [MISSIONE],
    "TS-AI-00397": [TERZO_PA, MISSIONE],   # negozi al dettaglio + causa spreco alimentare
}


def classify_tags(id_caso, text):
    if id_caso in MANUAL_OVERRIDES:
        return "; ".join(MANUAL_OVERRIDES[id_caso])
    t = text.lower()
    tags = []
    if MISSIONE_PAT.search(t):
        tags.append(MISSIONE)
    if TERZO_PA_PAT.search(t):
        tags.append(TERZO_PA)
    if INTERNAL_PAT.search(t):
        tags.append(INTERNO)
    if not tags:
        return "NON_CLASSIFICATO"
    return "; ".join(tags)


def classify_record(r):
    text = ' '.join([r.get('Problema_affrontato', ''), r.get('Obiettivo_implementazione', ''), r.get('Benefici_documentati', '')])
    tags = classify_tags(r['ID_caso'], text)
    return {
        "ID_caso": r["ID_caso"],
        "Tipo_beneficiario_Tags": tags,
        "Requires_Human_Review_Benef": "YES" if tags == "NON_CLASSIFICATO" else "NO",
    }


if __name__ == "__main__":
    import csv, collections
    with open('/sessions/wonderful-focused-faraday/mnt/Ricerca AI Terzo Settore/database_casi.csv', newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    results = [classify_record(r) for r in rows]
    counts = collections.Counter()
    for res in results:
        for t in res["Tipo_beneficiario_Tags"].split("; "):
            counts[t] += 1
    for k, v in counts.most_common():
        print(f"{v:4d}  {k}")
    n_review = sum(1 for res in results if res["Requires_Human_Review_Benef"] == "YES")
    print("\nRecord totali:", len(results), " | NON_CLASSIFICATO:", n_review)
