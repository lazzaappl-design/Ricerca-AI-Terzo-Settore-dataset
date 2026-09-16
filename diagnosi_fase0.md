# Diagnosi Fase 0 — Ricerca AI Terzo Settore

Data diagnosi: 2026-09-16. Nessun file esistente è stato modificato, rinominato, spostato o rigenerato per produrre questo documento; nessuno script della pipeline è stato eseguito. Tutti i conteggi sotto sono calcolati con script di sola lettura scritti per questa diagnosi, sul file attualmente in uso (vedi §1), non stimati né arrotondati salvo indicazione esplicita.

---

## 1. PIPELINE

### 1.1 Sequenza completa, da corpus a pagine pubblicate

```
[ricerca settimanale automatica]
        |  (protocollo_ricerca_settimanale.md)
        v
revisione_settimanale/candidati_AAAA-MM-GG.{md,csv}   <- coda, MAI toccata automaticamente dopo
        |  (approvazione umana esplicita, sessione interattiva)
        v
database_casi.csv/json  +  corpus_working_389rec_2026-08-20.{csv,json,xlsx}
        |  aggiornati insieme, stessi ID_caso, in parallelo
        |
        |---> [4 script di tagging, letti manualmente e poi fusi come nuove colonne] (vedi §1.3)
        |       beneficiary_tagger.py, human_oversight_tagger.py, pbc_tagger.py,
        |       technology_parser.py, typology_parser.py, geo_parser.py
        |
        v
corpus_working_389rec_2026-08-20.csv  (57 colonne, comprese le Tags già fuse)
        |
        v  build_knowledge_layer.py   [legge CORPUS_CSV hardcoded]
        v
knowledge_layer/nodes/*.csv  +  knowledge_layer/relationships/relationships.csv
        |
        |-----------------------------------------------------------.
        v                                                            v
compute_observatory.py                                    build_graph_export.py
        v                                                            v
observatory_data.json                                      graph_data.json
        |                                                            |
        v  [INCOLLATO A MANO, nessuno script                         v  [automatico: knowledge_graph_template.html
        |   automatizza questo passaggio - vedi §1.4]                |   + graph_data.json -> knowledge_graph.html]
        v                                                            v
osservatorio_ai_terzo_settore.html                          knowledge_graph.html
        |                                                            |
        '------------------------.      .----------------------------'
                                  v      v
                    ripubblicazione Lovable + GitHub
                    (passo separato, esplicito, mai automatico — protocollo_ricerca_settimanale.md)
```

Indice pubblico derivato: `indice_fonti.csv/json` (407 righe, un sottoinsieme di colonne di `database_casi.csv` senza i campi di testo libero).

### 1.2 File `corpus_working` attualmente in uso

Il file realmente in uso da tutta la pipeline a valle (knowledge graph, osservatorio) è:

**`corpus_working_389rec_2026-08-20.csv`** — confermato da `build_knowledge_layer.py` riga 81: `CORPUS_CSV = "corpus_working_389rec_2026-08-20.csv"  # aggiornare al file corrente`.

Il nome del file è **obsoleto**: contiene oggi **407 righe di dati**, non 389 — il nome è rimasto quello del 20 agosto, ma il contenuto è stato aggiornato più volte da allora (ultima modifica: 15 settembre, ore 13:49). Lo stesso vale per `corpus_working_389rec_2026-08-20.json` e `.xlsx`. Non è un errore funzionale (lo script punta correttamente al file giusto), ma è un rischio di confusione per chiunque (incluso un futuro ciclo automatico) legga il nome alla lettera: se in un ciclo futuro qualcuno crea un nuovo file con un nome "aggiornato" senza cambiare la costante in `build_knowledge_layer.py`, la pipeline continuerebbe silenziosamente a leggere il file vecchio.

Confermato che i quattro file "caso" sono oggi allineati a 407 righe ciascuno: `corpus_working_389rec_2026-08-20.csv`, `database_casi.csv`, `indice_fonti.csv`, `knowledge_layer/nodes/implementazioni.csv`.

### 1.3 Un punto cieco reale nella pipeline di tagging

I sei script di tagging/parsing (`beneficiary_tagger.py`, `human_oversight_tagger.py`, `pbc_tagger.py`, `technology_parser.py`, `typology_parser.py`, `geo_parser.py`) **non scrivono mai direttamente** in `corpus_working` o `database_casi`: producono file di audit separati (`pbc_audit.csv`, `technology_audit.csv`, `*_classification_map.json`, ecc.) pensati per una fusione manuale successiva (documentata esplicitamente nel docstring di `pbc_tagger.py`: "Dopo l'esecuzione, unire manualmente i risultati come nuove colonne..."). Le colonne `*_Tags` che oggi vedi in `corpus_working` sono quindi il risultato di quella fusione manuale già avvenuta in passato — non rigenerabile con un solo comando, e non riproducibile automaticamente se il corpus cresce, a meno di rifare la fusione a mano ogni volta.

Due di questi script (`beneficiary_tagger.py` riga 191, `human_oversight_tagger.py` riga 102) hanno inoltre un **percorso assoluto hardcoded** di una sessione Cowork precedente ormai chiusa:
`/sessions/wonderful-focused-faraday/mnt/Ricerca AI Terzo Settore/database_casi.csv`
Questo percorso non esiste in questa sessione (né esisterà in una sessione futura): se questi due script venissero rilanciati così come sono, fallirebbero subito con un errore "file non trovato". Non è un problema per la diagnosi (non li ho eseguiti), ma è un fatto da sapere prima di un futuro ciclo di pulizia che dovesse rilanciarli.

`geo_parser.py` (riga 392) legge invece `corpus_freeze_391rec_2026-08-20.csv` — lo snapshot congelato del 20 agosto, **391 righe**, ormai diverso e più vecchio del corpus attuale (407 righe): se rilanciato oggi produrrebbe una classificazione geografica calcolata su un sottoinsieme che manca dei 16 casi più recenti, salvo che (probabile, da verificare con te) sia già stato eseguito una volta soltanto e i suoi risultati siano già confluiti manualmente nelle colonne `Organization_Country`/`Implementation_Country`/`Geographic_Confidence` già presenti in `corpus_working`.

### 1.4 Il punto debole più importante della pipeline: `osservatorio_ai_terzo_settore.html`

A differenza di `knowledge_graph.html` — rigenerato **automaticamente** da `build_graph_export.py` iniettando `graph_data.json` dentro `knowledge_graph_template.html` — **non esiste alcuno script che generi `osservatorio_ai_terzo_settore.html`**. Il file contiene un blob JSON incollato a mano in `<script id="obs-data" type="application/json">` (riga 106) che deve restare sincronizzato manualmente con l'output di `compute_observatory.py` (`observatory_data.json`). Ho verificato che oggi i due sono identici (stesso campo `meta`), quindi non c'è un disallineamento *in questo momento* — ma è un passaggio manuale silenzioso, non un passo di pipeline riproducibile: se in futuro `observatory_data.json` viene rigenerato e ci si dimentica di incollare il nuovo JSON nell'HTML, la pagina pubblicata mostrerebbe dati vecchi senza nessun avviso.

`database_ai_terzo_settore.xlsx` non è referenziato da nessuno script: sembra un export manuale non più aggiornato automaticamente (citato solo in `registro_metodologico.md`, non nel README come file "vivo" della pipeline).

---

## 2. STATO (colonna `Stato_implementazione`)

Il campo è testo libero: **310 valori distinti su 407 righe** (nessun vocabolario controllato). Ho applicato una categorizzazione euristica — **proposta, non definitiva** — basata sulla prima porzione di testo di ciascun valore:

| Categoria proposta | N | % |
|---|---|---|
| Operativo | 225 | 55,3% |
| Annunciato/selezionato in un programma (non ancora operativo) | 128 | 31,4% |
| In sviluppo/pilota (generico, non legato a un grant nominato) | 44 | 10,8% |
| In sviluppo/pilota (annunciato/selezionato, ambiguo per formulazione) — vedi nota | +2 | +0,5% |
| Concluso | 4 | 1,0% |
| Abbandonato | 3 | 0,7% |
| Ambiguo/non determinabile | 3 | 0,7% |

Nota: 2 valori contengono la locuzione "in fase **iniziale** di sviluppo" (invece di "in fase di sviluppo") e non sono stati intercettati dalla regola automatica per una differenza di una sola parola, pur appartenendo chiaramente alla categoria "Annunciato/selezionato in un programma" (es. TS-AI-00247, TS-AI-00253, TS-AI-00254, TS-AI-00255, TS-AI-00319 — tutti "…nell'ambito del premio AWS Imagine Grant…" o "…con finanziamento Patrick J. McGovern Foundation…"). Li segnalo qui perché è un esempio concreto di quanto sia fragile qualunque classificazione automatica su questo campo: bastano variazioni minime di formulazione per sfuggire a una regola.

**Casi ambigui elencati a parte** (non riconducibili con sicurezza a nessuna delle categorie sopra):

- `TS-AI-00008` (GiveDirectly) — "Scalato (pilota esteso a più Paesi)": è operativo su scala o ancora in fase pilota estesa? Il testo non lo scioglie.
- `TS-AI-00066` (Respond Crisis Translation) — "Valutazione IA condotta e documentata pubblicamente; adozione operativa di IA non supervisionata esplicitamente **respinta** nel workflow di traduzione principale": questo è probabilmente un caso che documenta una **non-adozione** (l'organizzazione ha valutato e scartato l'uso di IA non supervisionata), non un'implementazione attiva — da rivedere se debba restare nel corpus con questo framing.
- `TS-AI-00176` (Steel Hearts) — "In uso attivo da parte del co-fondatore e direttore esecutivo dall'inizio del 2025, in fase di valutazione comparativa con altri strumenti di IA generativa": uso attivo ma da parte di una sola persona (non un processo organizzativo), in valutazione — ambiguo tra "Operativo" e "Pilota".

---

## 3. ANNO (colonna `Anno_implementazione`)

**258 valori su 407 (63,4%) NON sono un anno singolo pulito né un intervallo pulito di due anni** (es. "2020-2021"). La maggioranza di questi 258 mescola nello stesso campo più eventi temporali distinti: anno di fondazione dell'organizzazione, anno di lancio del progetto originario, anno di introduzione della componente IA specifica, anno dell'ultimo aggiornamento noto. Esempi rappresentativi (elenco completo dei 258 ID disponibile nello script usato per questa diagnosi, non riportato qui per intero):

- `TS-AI-00104`: `'2013 (fondazione organizzazione) - 2025 (annuncio collaborazione IA con AWS, luglio 2025)'`
- `TS-AI-00108`: `'1875 (fondazione organizzazione) - 2022-2024 (partnership IA con Google.org...)'`
- `TS-AI-00220`–`TS-AI-00255` (blocco di 36 record AWS Imagine Grant 2025-2026): quasi tutti nella forma `'Dicembre 2025 (selezione nell'ambito del premio...)'` — qui l'"anno" registrato è la data di **selezione/annuncio del grant**, non un anno di implementazione osservata.

**Proposta di distinzione** (per la pulizia dati, non ancora applicata):
1. `Anno_implementazione_effettiva` — l'anno in cui il sistema IA specifico descritto nel record è (o è stato) effettivamente in uso, quando desumibile.
2. `Anno_annuncio_o_selezione` — l'anno in cui l'organizzazione è stata selezionata/finanziata da un programma, quando il record proviene da una fonte "a lista" (AWS Imagine Grant, McGovern Foundation, Google.org Accelerator, Salesforce Accelerator, IBM Sustainability/Impact Accelerator, Microsoft AI for Good — cioè gran parte dei 258 casi sopra).
3. `Anno_fondazione_organizzazione` — quando il record lo riporta come contesto (spesso non pertinente all'IA specifica, andrebbe forse rimosso dal campo Anno e lasciato solo nella descrizione narrativa).

Senza questa separazione, qualunque grafico "trend temporale" costruito su questo campo (come quello già presente in `compute_observatory.py`, sezione 14, `trend_anno`) mescola anni di fondazione, anni di annuncio-grant e anni di uso operativo reale nello stesso asse — un problema di validità del grafico, non solo di pulizia estetica.

---

## 4. LIVELLO_CONFIDENZA e GRADO_VERIFICABILITA

### Livello_confidenza — 10 valori distinti letterali, ma solo 5 categorie di fatto:

| Valore letterale | N |
|---|---|
| Medio | 165 |
| Alto | 157 |
| Medio-alto | 55 |
| Medio-Alto | 14 |
| Basso-Medio | 10 |
| Medio-basso | 2 |
| Basso | 1 |
| Molto alto | 1 |
| Basso-medio | 1 |
| Medio-Basso | 1 |

Raggruppando per sola differenza di maiuscole/ordine parole (proposta): **Alto/Molto alto = 158 (38,8%)**, **Medio = 165 (40,5%)**, **Medio-alto (tutte le varianti) = 69 (17,0%)**, **Basso-medio (tutte le varianti) = 14 (3,4%)**, **Basso = 1 (0,2%)**. La sola causa della frammentazione in 10 valori invece di 5 è l'incoerenza di maiuscole/ordine ("Medio-Alto" vs "Medio-alto", "Basso-Medio" vs "Medio-basso" vs "Basso-medio") — un problema di normalizzazione stringa, non di sostanza.

### Grado_verificabilita — 67 valori distinti letterali, per lo stesso motivo ma più marcato:

Qui il campo non è solo incoerente nel casing: nella maggioranza dei 67 valori, alla categoria di base (Alta/Media-Alta/Media/Bassa/Molto alta) è stata **allegata una motivazione discorsiva tra parentesi** (es. "Alta (fonte primaria diretta dell'organizzazione, pagina dedicata al progetto)"), diversa per quasi ogni riga — cosa preziosa come nota interna, ma che rende il conteggio per valore letterale sostanzialmente inutile senza normalizzazione. Normalizzando alla sola parola prima della prima parentesi:

| Categoria normalizzata | N |
|---|---|
| Alta | 207 |
| Media-Alta | 117 |
| Media | 64 |
| Media-alta *(stesso valore di "Media-Alta", solo casing diverso)* | 14 |
| Bassa | 2 |
| Molto alta | 2 |
| Medio-bassa | 1 |

**Proposta di uniformazione**: fissare 5 etichette canoniche (`Alta`, `Media-Alta`, `Media`, `Bassa-Media`, `Bassa`) sia per `Livello_confidenza` sia per `Grado_verificabilita`, spostando ogni nota discorsiva oggi tra parentesi in un campo separato (es. `Note_verificabilita`) invece di lasciarla dentro il valore categoriale.

---

## 5. KPI: casi in cui riporta selezione/obiettivo dichiarato invece di un risultato

**67 record su 407 (16,5%)** hanno nel campo `KPI` un contenuto che descrive una **selezione in un programma di finanziamento** o un **obiettivo dichiarato/atteso** (parole chiave: "selezione tra", "vincitori", "obiettivo dichiarato", "atteso/attesi", "non ancora disponibili", "pianificato") invece di un risultato osservato. Esempi:

- `TS-AI-00204`–`TS-AI-00216` (9 record, coorte Salesforce Agents for Impact): il campo KPI riporta letteralmente `"Selezione tra le organizzazioni della coorte Salesforce Agents for Impact 2025, focus istruzione"` — non un indicatore di prestazione, ma la descrizione dell'evento di selezione.
- `TS-AI-00220`–`TS-AI-00251` (gran parte dei 36 record AWS Imagine Grant 2025-2026): pattern ricorrente `"Selezione tra i vincitori del premio [nome premio] dell'AWS Imagine Grant 2025-2026"`.
- `TS-AI-00187`, `TS-AI-00188`: `"Aumento atteso del 10%..."`, `"Miglioramento atteso dell'80%..."` — proiezioni dichiarate dal finanziatore, non misurazioni.
- `TS-AI-00240`, `TS-AI-00248`, `TS-AI-00289`, `TS-AI-00327`: `"Obiettivo dichiarato di..."` esplicito.

Questo è coerente con il criterio metodologico "anticipated impact" che hai introdotto nel Ciclo 186 (vedi §7) — quindi non è un errore di compilazione, ma **è un fatto rilevante per la comunicazione pubblica**: quasi 1 caso su 6 nel dataset riporta come "KPI" un obiettivo o una selezione, non un risultato misurato. Se il KPI viene mostrato al pubblico senza questa distinzione esplicita, il lettore può leggerlo come un risultato ottenuto.

---

## 6. FUNZIONE ORGANIZZATIVA (colonna `Funzione_organizzativa_Tags`)

**Zero righe hanno il campo vuoto** (0/407) — ma **162 righe su 407 (39,8%)** contengono il valore sentinella `NON_CLASSIFICATO`, il fallback esplicito prodotto da `pbc_tagger.py` quando nessun pattern del vocabolario controllato (`PROC_TAGS`, 18 voci, applicate al campo sorgente `Processo_organizzativo`) trova corrispondenza nel testo.

**Causa verificata, non solo ipotizzata**: ho controllato tutte le 162 righe con `NON_CLASSIFICATO` — **0 su 162 hanno il campo sorgente `Processo_organizzativo` vuoto**. Il campo sorgente contiene sempre una descrizione specifica e leggibile (es. "Erogazione di informazioni e servizi agli utenti finali", "Screening sanitario di comunità (case finding attivo)", "Produzione di contenuti accessibili", "Documentazione clinica", "Prevenzione e risposta alla tratta di esseri umani"). Il problema non è un campo di origine vuoto: è che il **vocabolario di 18 voci è costruito prevalentemente su funzioni di back-office/amministrative** (fundraising, comunicazione/marketing, CRM, HR, servizi legali, amministrazione, governance IA...) — coerente con il riferimento dichiarato nel docstring di `pbc_tagger.py` all'APQC Process Classification Framework, un framework pensato per processi aziendali generici — e **non copre le funzioni di erogazione diretta del servizio alla missione** (assistenza sanitaria diretta, contrasto alla tratta, produzione di contenuti per categorie specifiche di beneficiari, documentazione clinica) che sono proprio il cuore di molte organizzazioni del Terzo Settore. Non è un vocabolario "quasi giusto con qualche buco": per una parte sostanziale dei casi manca l'intera categoria semantica.

Per confronto, lo stesso meccanismo di fallback sulle altre colonne Tag prodotte dallo stesso script:

| Campo | NON_CLASSIFICATO | % |
|---|---|---|
| Funzione_organizzativa_Tags | 162/407 | **39,8%** |
| Beneficio_Tags | 112/407 | **27,5%** |
| Criticita_Tags | 66/407 | 16,2% |
| Supervisione_umana_Tags | 1/407 | 0,2% |
| Settore_missione_Tags | 0/407 | 0,0% |
| Tipo_beneficiario_Tags | 0/407 | 0,0% |

### Confronto con l'affermazione pubblica dell'Osservatorio

`osservatorio_ai_terzo_settore.html` (riga 96) dichiara: *"Alcune dimensioni hanno una quota di casi 'non classificabili' dal testo delle fonti disponibili (varia dal 5% al 15% a seconda della dimensione)"*.

**I dati non confermano questo intervallo per due delle dimensioni verificate**: Funzione_organizzativa_Tags è al 39,8% (più del doppio del limite superiore dichiarato) e Beneficio_Tags al 27,5% (quasi il doppio). Solo Criticita_Tags (16,2%) è vicino al limite superiore. C'è inoltre un meccanismo tecnico non menzionato dalla frase pubblica: `build_knowledge_layer.py` (riga 19 del proprio docstring, confermato nel codice) **non crea alcun nodo o relazione per i valori NON_CLASSIFICATO** — quindi ogni statistica aggregata calcolata su questi tag nel grafo o nell'osservatorio è silenziosamente calcolata solo sul sottoinsieme classificato, senza che la percentuale di esclusione sia visibile nel grafico stesso (compare solo come nota testuale generica, con un intervallo che qui risulta sottostimato).

---

## 7. CRITERIO DI INCLUSIONE: progetti selezionati in un programma di finanziamento ma non ancora operativi

**La decisione esiste ed è documentata esplicitamente.** Si trova in `registro_metodologico.md`, **Ciclo 186 (2026-08-06)**, righe 1018–1031, a proposito della coorte "natura" 2025 del Salesforce Accelerator:

> "I dati quantitativi riportati per questi 5 record (percentuali di riduzione/aumento, numero di agricoltori/azioni) sono obiettivi dichiarati ('anticipated impact') dalla fonte ufficiale Salesforce al momento dell'annuncio del programma (aprile 2025), non risultati operativi già misurati e verificati. Questo è stato esplicitamente segnalato nel campo Criticita_documentate di ciascun record, in coerenza con il rigore metodologico del dataset."

Il criterio — che qui chiamo "anticipated impact" seguendo la tua stessa terminologia nel registro — viene poi richiamato esplicitamente in cicli successivi (es. riga 1134, Ciclo ~192-193, sui 15 candidati AWS Imagine Grant 2025-2026): *"tutti i dati quantitativi assenti o dichiarati come obiettivi non ancora misurati sono stati esplicitamente flagged in Criticita_documentate secondo il criterio 'anticipated impact' introdotto nel Ciclo 186."*

In sintesi, la regola applicata è: **un caso selezionato/finanziato da un programma esterno può essere incluso anche se non ancora operativo, a condizione che i dati quantitativi non ancora misurati siano esplicitamente segnalati come tali nel campo `Criticita_documentate`** (non semplicemente omessi o presentati come risultati).

### Coerenza con il criterio del README

Il README dichiara di escludere sistematicamente *"dichiarazioni di intenti prive di evidenza d'uso"*. Il criterio "anticipated impact" **non è in contraddizione diretta** con questa frase, a una condizione: che il record documenti comunque un workflow tecnico specifico e descritto (non solo l'intenzione di adottare IA in generale) — ed è così per la maggior parte dei casi controllati in §5 (es. i record AWS Imagine Grant descrivono uno strumento nominato con un workflow tecnico specifico, non solo un'intenzione generica).

**Tuttavia c'è una tensione pratica che vale la pena risolvere prima della pubblicazione**, non a livello di criterio ma a livello di *come viene letto dall'esterno*: un lettore che apre il dataset pubblico e trova un record con `Stato_implementazione` = "In fase di sviluppo, nell'ambito del premio AWS Imagine Grant 2025-2026" e `KPI` = "Selezione tra i vincitori del premio..." (il pattern più comune tra i 128 casi di §2 e i 67 casi di §5, spesso sovrapposti) può leggerlo esattamente come il tipo di "dichiarazione di intenti priva di evidenza d'uso" che il README dice di escludere — perché la distinzione fine (workflow tecnico descritto vs. intenzione generica) non è visibile guardando solo Stato e KPI, è visibile solo leggendo `Criticita_documentate` per esteso, campo che nella pubblicazione attuale (knowledge graph, indice fonti) **non è incluso** (è tra i campi di testo libero esclusi per privacy, insieme a Osservazioni — vedi la conversazione precedente su questo stesso punto). Il criterio metodologico è quindi solido e documentato, ma **il modo in cui questi ~128 casi vengono presentati nei materiali pubblici non porta con sé la spiegazione che li rende legittimi secondo il criterio**.

---

## 8. FORMULAZIONI PUBBLICHE: "implementazioni verificate" e formule equivalenti

Occorrenze trovate nei file pubblicati:

1. `README.md` riga 3: *"407 casi verificati manualmente, uno per uno, con fonte primaria citata per ciascuno"*.
2. `post_linkedin.md` riga 5: *"un dataset di 407 implementazioni verificate di intelligenza artificiale..."*.
3. `post_linkedin.md` riga 28: *"407 casi verificati di adozione dell'IA nel Terzo Settore globale, uno per uno, con fonte primaria citata per ciascuno"*.

**Come è calcolato il numero 407**: è il conteggio letterale delle righe dati (`len(rows)`) in `corpus_working_389rec_2026-08-20.csv`, `database_casi.csv`, `indice_fonti.csv` e `knowledge_layer/nodes/implementazioni.csv` — tutti e quattro concordano esattamente su 407 alla data di questa diagnosi (15-16 settembre 2026). Non è una stima: è verificabile riaprendo qualunque di questi quattro file. Questo numero, in sé, è corretto e riproducibile.

**Ciò che non è immediatamente verificabile dal solo numero "407 verificati" è cosa intende "verificato"**, ed è qui che i risultati delle sezioni precedenti diventano rilevanti:
- Il 39,8% dei casi (§6) non ha una classificazione di funzione organizzativa utilizzabile.
- Il 16,5% dei casi (§5) riporta come "KPI" un obiettivo dichiarato o una selezione in un programma, non un risultato osservato.
- Il 31,4% dei casi (§2) non è ancora operativo secondo il proprio stesso campo Stato.
- Un caso (`TS-AI-00001`, non ricontrollato singolarmente ma rappresentativo di `Livello_confidenza` = "Basso" — 1 caso — e `Grado_verificabilita` variante "Bassa" — 2 casi, §4) ha una verificabilità dichiarata esplicitamente bassa nello stesso record.

Nessuno di questi fatti rende falsa la frase "407 casi verificati" nel senso stretto in cui l'hai definita internamente (fonte primaria citata, criteri di esclusione applicati, processo documentato in `registro_metodologico.md`) — quello standard è stato effettivamente applicato, ciclo per ciclo, in modo tracciabile. Ma "verificato" nella frase pubblica rischia di essere letto da un pubblico ampio (LinkedIn, enti, finanziatori, ricercatori — il tuo target dichiarato) come "verificato che il sistema IA sia operativo e ne siano stati misurati i risultati", mentre per una parte non piccola dei 407 casi significa "verificato che l'organizzazione esiste, sia stata selezionata/finanziata per un progetto IA specifico, e non stia dichiarando un'intenzione generica priva di workflow" — una forma di verifica reale, ma più debole di quella che il lettore medio probabilmente assume leggendo "407 implementazioni verificate".

Non è stato possibile verificare (e quindi non lo affermo) se questa distinzione sia già esplicitata da qualche parte nel testo attuale dell'Osservatorio Lovable pubblicato online (`https://osservatorio-ai-terzo-settore.lovable.app`), perché quella pagina live non è stata controllata in questa diagnosi (ho lavorato solo sui file locali/GitHub, come richiesto).

---

## Riepilogo dei numeri di questa diagnosi (nessuno stimato o arrotondato)

- Righe nel corpus in uso: 407 (corpus_working_389rec_2026-08-20.csv, database_casi.csv, indice_fonti.csv, implementazioni.csv — tutti allineati)
- Stato_implementazione: 310 valori distinti; categorizzazione proposta 225 operativo / 128 annunciato-selezionato / 44 sviluppo-pilota generico / 4 concluso / 3 abbandonato / 3 ambiguo (+2 malclassificati per variante testuale, riassegnabili ad "annunciato-selezionato")
- Anno_implementazione: 258/407 (63,4%) non è un anno singolo o intervallo pulito
- Livello_confidenza: 10 valori letterali, 5 categorie reali dopo normalizzazione maiuscole/ordine
- Grado_verificabilita: 67 valori letterali, 5-6 categorie reali dopo normalizzazione
- KPI con selezione/obiettivo dichiarato invece di risultato: 67/407 (16,5%)
- Funzione_organizzativa_Tags NON_CLASSIFICATO: 162/407 (39,8%) — 0 di questi con campo sorgente vuoto
- Beneficio_Tags NON_CLASSIFICATO: 112/407 (27,5%); Criticita_Tags: 66/407 (16,2%)
- Claim pubblico Osservatorio "5-15% non classificabili": non confermato per Funzione_organizzativa_Tags né per Beneficio_Tags
- Criterio "anticipated impact": documentato in registro_metodologico.md, Ciclo 186 (2026-08-06)
- "407 casi/implementazioni verificate": 3 occorrenze pubbliche (README.md x1, post_linkedin.md x2), numero riproducibile, definizione di "verificato" non esplicitata nel testo pubblico stesso
