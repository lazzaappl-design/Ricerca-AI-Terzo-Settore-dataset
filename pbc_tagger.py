# -*- coding: utf-8 -*-
"""
Normalizzazione additiva multi-tag per Processo_organizzativo, Settore_attivita,
Benefici_documentati, Criticita_documentate.

Vocabolario costruito dal basso (2026-08-20) leggendo tutti i valori reali del
corpus, poi verificato contro framework esistenti:
- Processo_organizzativo -> Funzione_organizzativa_Tags (rif. APQC Process
  Classification Framework, corrispondenza parziale/debole - APQC troppo
  generico per la varietà di missioni del terzo settore)
- Settore_attivita -> Settore_missione_Tags (nuovo, introdotto per coprire la
  varietà di missione settoriale non catturata da Funzione_organizzativa)
- Benefici_documentati -> Beneficio_Tags (rif. criteri OECD-DAC: Effectiveness/
  Efficiency/Impact - corrispondenza parziale, i nostri tag sono sotto-categorie
  più granulari)
- Criticita_documentate -> Criticita_Tags (rif. NIST AI Risk Management
  Framework, 7 caratteristiche di trustworthy AI - corrispondenza forte per le
  criticita' che riguardano il sistema IA in se'; la categoria dominante
  "gap di fonte" e' una categoria metodologica propria del progetto, non NIST)

Valori originali dei 4 campi NON modificati. Fallback "NON_CLASSIFICATO" quando
nessun pattern matcha (nessuna forzatura, nessuna perdita di informazione: il
valore originale resta comunque leggibile nel campo sorgente).

Uso: esegui su database_casi.csv (l'intero corpus, non solo i nuovi record -
i pattern sono deterministici e a costo trascurabile anche su tutto il corpus).
Dopo l'esecuzione, unire manualmente i risultati come nuove colonne nel foglio
CORPUS di corpus_working_*.xlsx e come righe nel foglio PROCESS_BENEFIT_CRIT_AUDIT,
poi cancellare l'eventuale CSV/JSON intermedio (nessun file duplicato persistente).
"""
import re
import csv
import json
import collections

BENEFIT_TAGS = [
    ("Risparmio di tempo / maggiore velocità", r"tempo risparmiat|risparmi[a-z]*\s+(fino a\s+)?[\d.,]*\s*(ore|minuti|giorni|tempo)|pi[uù] (rapid|veloc)|riduzione del tempo|tempo di (attesa|onboarding|risposta|preparazione|conversione|documentazione)[^.;]{0,30}ridott|ridott[ao] (da|del)[^.;]{0,25}(ore|minuti|giorni|settiman|mes[ei]|anno)|da (ore|giorni|settiman|un anno|circa)[^.;]{0,20}a (minuti|ore|mes[ei]|sei mesi)|velocit[aà] (di|aument|quasi)"),
    ("Riduzione di costi/sforzo operativo", r"riduzione dei costi|risparmio (stimato|economico)|costo per acquisizione|riduzione del costo|meno costos|riduzione (stimata )?del [\d-]+% (dello sforzo|del)|sforzo[^.;]{0,20}ridott"),
    ("Impatto economico/finanziario quantificato", r"[\$€]\s?[\d.,]+|[\d.,]+\s?(\$|€|euro|dollari)|budget|sovvenzion|fondi (raccolti|erogati|distribuiti)"),
    ("Aumento di scala/copertura/volume di utilizzo", r"\boltre [\d.,]+|pi[uù] di [\d.,]+|quasi [\d.,]+|\b[\d][\d.,]{2,}\s*(utenti|persone|famiglie|rifugiati|volontari|casi|richieste|interazioni|contatti|conversazioni|colloqui|documenti|petizioni|donatori|studenti|abbinamenti|donne|messaggi|sussidi|Paesi|scuole|partecipanti|beneficiari|soggetti|SMS|aree protette)|copertura di|scalat[oa]|espans|dispiegat[oa] (da|in)"),
    ("Miglioramento accuratezza/qualità", r"accuratezza|precisione|qualit[aà] (dei dati|del|migliorat)|affidabilit[aà]|livello di confidenza"),
    ("Aumento entrate/donazioni/ROI", r"\broi\b|incremento[^.;]{0,15}ricav|donazioni|tasso di risposta|tasso di conversione|brand lift|notoriet[aà] del marchio"),
    ("Disponibilità/accessibilità H24", r"24/7|24 ore su 24|accesso (immediato|istantaneo|rapido e trasparente|gratuito e anonimo)|nessun messaggio[^.;]{0,20}senza risposta"),
    ("Soddisfazione utenti/feedback positivo", r"feedback (qualitativo )?positiv|soddisfazione|valutat[oi] (significativamente )?meglio|tasso di efficacia"),
    ("Capacità organizzativa/competenze acquisite", r"sviluppare competenze|capacit[aà] organizzativ|apprendimento organizzativ|competenze sull'uso|evidenza pubblica[^.;]{0,20}a supporto di policy"),
    ("Riduzione stress/carico di lavoro personale", r"riduzione dello stress|carico di lavoro|liberat[ei] per la vita associativa|energie liberate|equivalente al tempo che \d+ persone"),
    ("Beneficio dichiarato ma non quantificato", r"non quantificat|dichiarat[oa],? non|dettaglio quantitativo non disponibile|nessun (dato|beneficio) quantificat"),
    ("Miglioramento esiti sociali/impatto diretto sui beneficiari", r"insicurezza alimentare ridotta|reddito[^.;]{0,15}raddoppiat|occupazione|effetto significativo su|impatto anno su anno|riduzione del danno"),
]

CRIT_TAGS = [
    ("Nessuna criticità/limite documentato (gap di fonte)", r"non riporta|non specificat|non dettagliat|non document|non fornisc|dettagli limitat|nessun dato|nessuna criticit|dati (quantitativi|indipendenti)[^.;]{0,20}(non disponibil|assent)|le fonti (disponibili )?(non|sono)|non è (possibile|disponibile)"),
    ("Limiti della fonte / mancanza di valutazione indipendente", r"fonte (esclusivamente |unicamente |principale )?(è )?(un case study )?vendor|fonte unica|mancano valutazioni indipendenti|senza conferma (diretta|indipendente)|non pi[uù] raggiungibile|comunicazioni dell'organizzazione stessa|comunicat[oi] (ufficial[ei] )?(dell'organizzazione|di google)"),
    ("Necessità di supervisione/controllo umano (NIST: Accountable & Transparent)", r"supervision[ei] uman|controllo uman|human[- ]in[- ]the[- ]loop|revisione uman|escalation (a )?operatori|i bot non sono la soluzione"),
    ("Bias/qualità dei dati (NIST: Fair, bias managed)", r"\bbias\b|dati distort|dati difettos|qualit[aà][^.;]{0,15}dati|dati (di )?scarsa qualit|pulizia dei dati"),
    ("Privacy/sicurezza dei dati (NIST: Privacy-Enhanced/Secure)", r"privacy|sicurezza dei dati|protezione dei dati|dati sensibil"),
    ("Scalabilità/adozione limitata", r"scalabilit|scalare|ostacoli tecnici[^.;]{0,20}scalabilit|adozione[^.;]{0,15}limitat|difficolt[aà][^.;]{0,15}adozione|sostenibilit[aà][^.;]{0,15}tecnologia"),
    ("Fase pilota/dati preliminari", r"fase pilota|ancora in fase di|progetto pilota|dati preliminari|troppo recente|hackathon"),
    ("Governance/etica richiesta (NIST: Accountable & Transparent)", r"governance|etic[ao]|safeguarding|inquietante"),
    ("Errori/malfunzionamenti occasionali (NIST: Safe/Valid&Reliable)", r"commette errori|malfunzionament|errore (occasionale|di interpretazione)|interpretando[^.;]{0,30}error"),
    ("Risorse/costi limitati", r"risorse limitat|costi elevat|assenza di dati sui costi|mancanza di (fondi|risorse)|budget limitat"),
    ("Dipendenza da fornitore tecnologico unico", r"dipendenza da|fornitore (tecnologico )?unico"),
    ("Alfabetizzazione digitale/adozione da parte degli utenti", r"alfabetizzazione digitale|adattamento[^.;]{0,20}utenti|competenze digitali degli utenti"),
    ("Efficacia/risultati limitati o modesti", r"risultat[oi][^.;]{0,15}modest|effetti[^.;]{0,15}modest|impatt[oi][^.;]{0,15}modest|efficacia limitat|base di prova[^.;]{0,20}limitat"),
    ("Necessità di calibrazione/contesto locale", r"calibrazione|contesto locale|adattamento (al|del) contesto"),
]

PROC_TAGS = [
    ("Fundraising/raccolta fondi", r"fundraising|raccolta fondi|acquisizione donatori|retention donatori|gestione donatori"),
    ("Comunicazione/marketing", r"comunicazion|marketing|campagn|sensibilizzazione"),
    ("Analisi dati/supporto decisionale", r"analisi (dei )?dati|supporto decisionale|analisi predittiva|business intelligence|analisi e interpretazione di dati"),
    ("Gestione documentale/knowledge management", r"gestione documentale|knowledge management|gestione della conoscenza|catalogazione|archiviazione"),
    ("CRM/gestione relazioni", r"\bcrm\b|gestione relazioni"),
    ("Formazione/capacity building", r"formazione|capacity building|alfabetizzazione|tutoraggio|apprendimento"),
    ("Assistenza diretta/supporto psicologico/helpline", r"assistenza|supporto psicologic|helpline|servizio.{0,10}assistenza clienti|supporto sanitario|supporto informativo|servizio informativo"),
    ("Monitoraggio e valutazione (M&E)", r"monitoraggio|valutazione|sorveglianza|controllo qualit[aà]"),
    ("Gestione volontari/HR", r"gestione volontari|risorse umane|\bhr\b|personale"),
    ("Progettazione/sviluppo prodotto", r"progettazione|sviluppo (di )?prodott"),
    ("Gestione delle emergenze/risposta a disastri", r"gestione delle emergenze|risposta a disastri|risposta umanitaria|gestione del rischio disastri"),
    ("Amministrazione/gestione finanziaria", r"amministrazion|gestione finanziaria|contabilit|valutazione del rischio di credito"),
    ("Matching/abbinamento beneficiari-risorse", r"abbinamento|matching|allocazione (delle )?risorse|collocamento"),
    ("Servizi legali", r"legal|atti legali|consulenza legale|revisione di casi"),
    ("Traduzione/interpretariato", r"traduzione|interpretariato"),
    ("Accessibilità/produzione contenuti accessibili", r"content[i]? accessibil|document[i]? accessibil"),
    ("Gestione casi (case management)", r"gestione dei casi|case management|targeting dei beneficiari|valutazione dei bisogni"),
    ("Governance/gestione IA interna", r"governance ia|governance dei dati|gestione dei dati"),
]

SETTORE_TAGS = [
    ("Aiuti umanitari/rifugiati/disastri", r"umanitari|rifugiat|sfollat|disastr|emergenz|early warning|risposta a|acqua potabile"),
    ("Ambiente/conservazione natura", r"ambient|conservazion|natura|biodiversit|fauna|clima|forest|oceano|specie|economia circolare|sostenibil"),
    ("Salute/sanità", r"salute|sanit|medic|clinic|malatt|diagnos|ospedal|cancro|oncolog|farmac|dipendenz|sostanze"),
    ("Istruzione/formazione", r"istruzion|educaz|scuola|universit|apprendiment|mentoring|alfabetizzazione|formazione (professional|educativ)|successo formativo|coaching educativo"),
    ("Violenza di genere/protezione vulnerabili", r"violenza|abuso|tratta di esseri umani|protezione dell'infanzia|maltrattament|sfruttamento sessuale|welfare minorile|affidatari"),
    ("Inclusione sociale/povertà/assistenza sociale", r"inclusione sociale|povert|assistenza sociale|servizi sociali|senzatetto|homeless|senza tetto|informazione sociale|consulenza al cittadino|anzian|isolamento sociale|reinserimento sociale|settore sociale"),
    ("Disabilità/accessibilità", r"disabilit|accessibilit|non vedent|sordociech|ipoveden"),
    ("Diritti umani/giustizia/legale", r"diritti umani|giustizia|legal|giudiziari|criminalit|carcerari|discriminazion|accountability delle forze|recidiva"),
    ("Sviluppo economico/finanza inclusiva/lavoro", r"sviluppo economic|inclusione finanziaria|microfinanza|\blavoro\b|occupazion|impiego|credito|agricoltura|agricol|imprenditoria|collocamento lavorativo|mobilit[aà] economica|catene di fornitura|diritti dei lavoratori|sicurezza alimentare|spreco alimentare"),
    ("Cultura/arte/patrimonio", r"cultura|arte|patrimonio|museal|danza|spettacol|genealogia|preservazione document|servizi bibliotecari"),
    ("Animali/benessere animale", r"animal|adozion.{0,10}animal|benessere animale"),
    ("Salute mentale/supporto psicologico", r"salute mentale|supporto psicolog|benessere psicolog|crisi (emotiva|suicidar)|prevenzione del suicidio|disturbi alimentari"),
    ("Giornalismo/informazione/disinformazione", r"giornalis|disinformazion|fact-checking|verifica dei fatti|informazione elettorale|contenuti mediatici|trasparenza politica"),
    ("Edilizia sociale/housing", r"edilizia (abitativa|popolare)|assistenza abitativa|senza tetto"),
    ("Governance urbana/sviluppo città", r"governance urbana|sviluppo delle citt|sviluppo urbano|gestione pubblica locale|trasformazione digitale del settore pubblico|dialogo civico|depolarizzazione"),
    ("Linguistica/preservazione lingue", r"linguistic|preservazione delle lingue|lingue minoritarie"),
    ("Cybersicurezza/protezione digitale", r"cybersicurezza|sicurezza informatica|protezione digitale"),
    ("Veterani/militari", r"veteran|militar"),
    ("Terzo settore/capacity building organizzativo", r"capacity building|rafforzamento organizzativ|\bterzo settore\b|no-?profit|integrazione dati"),
]


def tag_field(text, tagset):
    tl = (text or "").lower()
    hits = [tag for tag, pat in tagset if re.search(pat, tl)]
    review = "NO"
    if not hits:
        hits = ["NON_CLASSIFICATO"]
        review = "YES"
    return "; ".join(hits), review


def classify_record(r):
    ben_tags, ben_rev = tag_field(r['Benefici_documentati'], BENEFIT_TAGS)
    crit_tags, crit_rev = tag_field(r['Criticita_documentate'], CRIT_TAGS)
    proc_tags, proc_rev = tag_field(r['Processo_organizzativo'], PROC_TAGS)
    sett_tags, sett_rev = tag_field(r['Settore_attivita'], SETTORE_TAGS)
    return {
        "ID_caso": r['ID_caso'], "Organizzazione": r['Organizzazione'],
        "Processo_originale": r['Processo_organizzativo'], "Funzione_organizzativa_Tags": proc_tags,
        "Settore_originale": r['Settore_attivita'], "Settore_missione_Tags": sett_tags,
        "Benefici_originale": r['Benefici_documentati'], "Beneficio_Tags": ben_tags,
        "Criticita_originale": r['Criticita_documentate'], "Criticita_Tags": crit_tags,
        "Requires_Human_Review": "YES" if "NON_CLASSIFICATO" in (proc_tags + sett_tags + ben_tags + crit_tags) else "NO",
    }


if __name__ == "__main__":
    with open("database_casi.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [classify_record(r) for r in rows]
    n_review = sum(1 for r in results if r["Requires_Human_Review"] == "YES")
    print("Record totali:", len(results), "| almeno un campo NON_CLASSIFICATO:", n_review)

    with open("pbc_audit.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = list(results[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results)

    print("Scritto pbc_audit.csv - da unire manualmente a corpus_working_*.xlsx")
    print("(colonne in CORPUS + righe in PROCESS_BENEFIT_CRIT_AUDIT), poi cancellare questo CSV intermedio.")
