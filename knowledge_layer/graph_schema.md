# Schema del grafo — Ricerca AI Terzo Settore

Data costruzione: 2026-08-20 — v2 italiano + TipoBeneficiario 2026-08-24 — v3 TipoBeneficiario a 3 livelli 2026-08-24 — **v4: gap-analysis pre-osservatorio pubblico, 2026-08-24 (Dimensione/N_dipendenti/Fatturato, Fonte_qualificata/Fallimenti, Collaboratore, TipoSupervisioneUmana)**
Fonte: `corpus_working_407rec_2026-09-16.csv` (389 unità di analisi, master empirico invariato)
Output: `knowledge_layer/nodes/*.csv` (17 file) + `knowledge_layer/relationships/relationships.csv` (1 file, 6.098 righe)

Il nodo centrale è **Implementazione**: tutte le informazioni empiriche (tecnologia, processo, beneficio, criticità, fonte, Paese) sono collegate all'Implementazione, non trasformate in relazioni dirette tra concetti generali (es. non si crea "ChatGPT -> PRODUCE -> Risparmio di tempo"; si crea "Implementazione -> USA_SOFTWARE -> ChatGPT" e "Implementazione -> RIPORTA_BENEFICIO -> Risparmio di tempo" separatamente, così il beneficio resta ancorato al caso specifico che lo documenta).

**Nota sulla versione italiana (2026-08-24)**: fino al 2026-08-20 i node label, i relationship type e i nomi delle proprietà (es. `Problem`, `Objective`, `HAS_IMPLEMENTATION`) erano in inglese per convenzione tecnica, mentre i valori (`canonical_name`, testo dei campi) erano già interamente in italiano. Su richiesta dell'utente, l'intera impalcatura del grafo — non solo i dati — è stata tradotta in italiano per essere leggibile direttamente in Neo4j Browser/Bloom senza bisogno di tradurre mentalmente i nomi dei campi. Questo È un cambio di schema (non additivo): chi ha già caricato la versione inglese deve svuotare il database e ricaricare (istruzioni in fondo).

## Classi di nodo

| Classe (label) | File | N. nodi | ID | Fonte nel corpus |
|---|---|---|---|---|
| Implementazione | implementazioni.csv | 389 | ID_caso originale (TS-AI-XXXXX, invariato) | riga del corpus |
| Organizzazione | organizzazioni.csv | 371 | ORG-NNNNN | Organization_ID (Entity Resolution) |
| Paese | paesi.csv | 79 | COU-NNN | Organization_Country / Implementation_Country |
| ModelloIA | modelli_ia.csv | 4 | MODEL-NNNN | Model_ID (solo prodotti nominati risolti) |
| Software | software.csv | 1 | SOFT-NNNN | Software_ID (solo prodotti nominati risolti) |
| CategoriaOrganizzativa | categorie_organizzative.csv | 9 | CAT-NN | Categoria_organizzativa |
| TecnicaIA | tecniche_ia.csv | 15 | TEC-NN | Tecnica_IA_Tags |
| Fornitore | fornitori.csv | 10 | VEN-NN | Fornitore_Piattaforma_Tags |
| FunzioneOrganizzativa | funzioni_organizzative.csv | 18 | FUNC-NN | Funzione_organizzativa_Tags |
| SettoreMissione | settori_missione.csv | 19 | SET-NN | Settore_missione_Tags |
| Beneficio | benefici.csv | 12 | BEN-NN | Beneficio_Tags |
| Criticita | criticita.csv | 14 | CRI-NN | Criticita_Tags |
| Programma | programmi.csv | 6 | PROG-NN | estratto da Organizzazione/Tecnologia_utilizzata (grant ricorrenti) |
| Fonte | fonti.csv | 275 | SRC-NNNNN | Fonte_primaria (dedup su stringa esatta) |
| **TipoBeneficiario** (nuovo 2026-08-24, 3 livelli) | tipi_beneficiario.csv | 3 | TBEN-NN | Tipo_beneficiario_Tags |
| **TipoSupervisioneUmana** (nuovo 2026-08-24, v4) | tipi_supervisione_umana.csv | 5 | SUP-NN | Supervisione_umana_Tags |
| **Collaboratore** (nuovo 2026-08-24, v4) | collaboratori.csv | 45 | COLLAB-NNN | organizzazioni/enti terzi co-menzionati nel campo Organizzazione |

**Totale nodi**: 389 + 371 + 79 + 4 + 1 + 9 + 15 + 10 + 18 + 19 + 12 + 14 + 6 + 275 + 3 + 5 + 45 = **1.275**

### Proprietà del nodo Implementazione
`id, nome, Anno, Stato, Problema, Obiettivo, Sottoprocesso, Workflow_dettagliato, Input, Output, Ruolo_umano, Livello_integrazione, KPI, Tempo_risparmiato, ROI, Livello_prova, Grado_completezza, Grado_verificabilita, Livello_confidenza, Osservazioni, Fonte_qualificata, Fallimenti`

(equivalenti italiani di `id, canonical_name, Year, Status, Problem, Objective, Subprocess, Detailed_Workflow, Input, Output, Human_Role, Integration_Level, KPI, Time_Saved, ROI, Evidence_Level, Completeness, Verifiability, Confidence_Level, Notes` della v1 inglese — stesso contenuto, chiavi tradotte. `Fonte_qualificata` e `Fallimenti` aggiunte in v4: erano nel corpus originale ma non erano mai state portate sul grafo — vedi sezione "Gap analysis v4" più sotto.)

### Proprietà del nodo Organizzazione
`id, nome, Tipo_organizzazione, Status_legale, Dimensione, Dimensione_dettaglio, N_dipendenti, Fatturato`

`Dimensione` è normalizzata in 7 categorie (Molto Piccola/Piccola/Piccola-Media/Media/Media-Grande/Grande/Molto Grande/Non disponibile) estraendo la categoria guida dal testo libero originale (es. "Grande (13.000 volontari, quasi 80 istituzioni sanitarie...)" → "Grande"); `Dimensione_dettaglio` conserva il testo integrale originale. `N_dipendenti`/`Fatturato` aggiunti in v4: dati già puliti nel corpus ma con fill rate basso (rispettivamente 5% e 1% dei 389 record) — utili quando presenti, non affidabili per aggregazioni sistematiche.

Campi lasciati come proprietà testuali e NON trasformati in nodi perché verificati come descrizioni quasi-uniche per record (`Sottoprocesso` 100% unico, `Benefici_documentati`/`Criticita_documentate` 95-97% unici anche dopo normalizzazione — le versioni categorizzate vivono nei tag `Beneficio_Tags`/`Criticita_Tags`, non nel testo integrale).

### Elementi volutamente NON modellati come nodi
- Testo integrale di `Sotto_processo`, `Benefici_documentati`, `Criticita_documentate`, `Problema_affrontato`, `Obiettivo_implementazione`, `Workflow_dettagliato` → restano proprietà di Implementazione (frammentazione 90-100%, non sono entità ricorrenti).
- Wikidata QID → non applicabile, Step 2/Wikidata saltato di comune accordo con l'utente (basso ritorno atteso per un corpus di piccole ONG locali).
- `Fallimenti` → non modellato (59% dei valori sono variazioni di "nessuno documentato"; non aggiunge dimensione analitica distinta da Criticita).

## Nuova dimensione: TipoBeneficiario (2026-08-24)

Il grafo v1 non distingueva esplicitamente **chi** riceve il beneficio di un'implementazione (il beneficiario finale/utente vs. l'organizzazione/staff interno). Costruita con lo stesso metodo bottom-up già usato per Funzione/Settore/Beneficio/Criticità: lettura di `Problema_affrontato` + `Obiettivo_implementazione` + `Benefici_documentati` per tutti i 389 record, estrazione di pattern testuali, verifica.

Campo multi-tag (come Beneficio_Tags/Criticita_Tags): un'Implementazione può avere più relazioni `HA_BENEFICIARIO` quando il testo indica sia un beneficiario esterno sia un beneficio organizzativo interno (es. libera tempo al personale E accelera l'assistenza ai rifugiati) — nessun nodo artificiale "Entrambi", solo due edge distinti.

**Evoluzione in 3 tappe (stessa sessione)**:
1. *v1*: 3 categorie via solo regex (diretto/utente finale, organizzazione/staff interno, causa ambientale/non umana) — 60/389 (15%) NON_CLASSIFICATO.
2. *v2*: ridotta a 2 label su richiesta dell'utente (diretto/esterno, fondendo "diretto" e "causa ambientale"; indiretto/organizzazione), con i 60 casi non catturati dal pattern-matching letti singolarmente e classificati per giudizio — 0 NON_CLASSIFICATO.
3. *v3 (attuale)*: l'utente ha chiesto una proposta di classificazione alternativa, notando che "diretto/esterno" mescolava concetti diversi (persone/comunità/causa ambientale insieme a partner aziendali o enti pubblici). Scelta tra due alternative proposte: **3 livelli** invece di 2, con le due varianti di etichetta richieste dall'utente ("/PA" sul secondo livello, "Organizzazione/interno" sul terzo).

| Tag | N. record (su 389, multi-tag) |
|---|---|
| Beneficiario finale della missione | 326 |
| Organizzazione/interno | 200 |
| Organizzazione/ente terzo/PA | 46 |

**Criteri di distinzione**:
- *Beneficiario finale della missione*: persone, comunità o causa ambientale/non umana che sono il target ultimo dichiarato (rifugiati, pazienti, comunità vulnerabili, biodiversità, clima).
- *Organizzazione/ente terzo/PA*: il beneficio dichiarato va a un'entità organizzata esterna diversa dal target finale della missione — azienda partner, governo locale/ministero, altra organizzazione no-profit cliente di una piattaforma, redazione/media, istituzione finanziaria.
- *Organizzazione/interno*: il beneficio dichiarato è la capacità operativa, i costi, il tempo del personale o la sostenibilità finanziaria dell'organizzazione che ha realizzato l'implementazione.

Tutti i 389 record sono stati riletti sotto la nuova lente a 3 vie: i 60 già letti manualmente in v2 sono stati riclassificati (es. Fair Trade USA e Ceres, prima "diretto/esterno" perché servono partner commerciali, ora correttamente "Organizzazione/ente terzo/PA"; Stand.earth, riletto con più attenzione, risultava rafforzare le *proprie* capacità di ricerca — spostato da "diretto" a "Organizzazione/interno"). Inoltre, rimuovendo i termini aziendali/PA dal pattern generico di v2, sono emersi 27 ulteriori record con match istituzionale tra quelli già auto-classificati nelle prime 329: di questi, 10 dopo lettura individuale richiedevano davvero il tag "Organizzazione/ente terzo/PA" (es. VolunteerMatch: le piccole ONG clienti ottengono più visibilità; American Cancer Society/OncoScope: ricercatori accademici e industriali esterni), 17 erano falsi positivi lessicali (es. "aziend" in "cittadinanza" o termini simili) e restano invariati. Risultato: **ancora 0 NON_CLASSIFICATO su 389**. Tutte le classificazioni manuali (70 ID totali) sono documentate con motivazione in commento nel dizionario `MANUAL_OVERRIDES` di `beneficiary_tagger.py`.

## Relazioni

| Relazione | Da → A | N. edge | Cardinalità | Origine empirica |
|---|---|---|---|---|
| HA_IMPLEMENTAZIONE | Organizzazione → Implementazione | 389 | 1 org : N implementazione | Organizzazione |
| HA_SEDE_IN | Organizzazione → Paese | 380 (395 righe generate nel CSV, 15 duplicate perché un'organizzazione con più implementazioni genera la stessa coppia più volte — MERGE le unifica correttamente in Neo4j) | N:N (multi-sede) | Organization_Country |
| IMPLEMENTATO_IN | Implementazione → Paese | 467 | N:N (multi-Paese) | Implementation_Country |
| HA_TIPO | Organizzazione → CategoriaOrganizzativa | 371 | N:1 | Categoria_organizzativa |
| USA_MODELLO | Implementazione → ModelloIA | 22 | N:N | Modello_AI (solo risolti) |
| USA_SOFTWARE | Implementazione → Software | 15 | N:N | Software_utilizzato (solo risolti) |
| USA_TECNICA | Implementazione → TecnicaIA | 635 | N:N | Tecnica_IA_Tags |
| USA_FORNITORE | Implementazione → Fornitore | 478 | N:N | Fornitore_Piattaforma_Tags |
| HA_FUNZIONE | Implementazione → FunzioneOrganizzativa | 263 | N:N | Funzione_organizzativa_Tags |
| INDIRIZZA_SETTORE | Implementazione → SettoreMissione | 517 | N:N | Settore_missione_Tags |
| RIPORTA_BENEFICIO | Implementazione → Beneficio | 365 | N:N | Beneficio_Tags |
| RIPORTA_CRITICITA | Implementazione → Criticita | 386 | N:N | Criticita_Tags |
| DOCUMENTATO_DA | Implementazione → Fonte | 389 | N:1 (per Fonte_primaria) | Fonte_primaria |
| FA_PARTE_DI | Implementazione → Programma | 171 | N:1 | estratto da Organizzazione/Tecnologia_utilizzata |
| **HA_BENEFICIARIO** (nuovo) | Implementazione → TipoBeneficiario | 572 | N:N (multi-tag) | Tipo_beneficiario_Tags |
| **COINVOLGE_UMANO** (nuovo v4) | Implementazione → TipoSupervisioneUmana | 613 | N:N (multi-tag) | Supervisione_umana_Tags |
| **REALIZZATO_CON** (nuovo v4) | Implementazione → Collaboratore | 50 | N:N | organizzazioni/enti co-menzionati in Organizzazione |

**Totale relazioni**: 6.083 dopo deduplica MERGE (6.098 righe generate nel CSV sorgente; 15 duplicate su HA_SEDE_IN, correttamente unificate da Neo4j — stessa dinamica già osservata e verificata nella v1 il 2026-08-21).

Formato `relationships.csv` (invariato, resta in inglese — file interno di elaborazione, mai visualizzato in Neo4j): `Relationship_ID, Source_Node_ID, Source_Node_Type, Relationship_Type, Target_Node_ID, Target_Node_Type, Implementation_ID, Confidence, Evidence_Field, Evidence_Value`. Le proprietà scritte sulle relazioni in Neo4j da `import.cypher` sono invece in italiano: `ID_Caso, Affidabilita, Campo_evidenza, Valore_evidenza`.

### Decisioni di modellazione
- Nessun edge creato per valori `NON_CLASSIFICATO`/tag mancanti: un'assenza di relazione è più onesta di un nodo fittizio.
- Nessun nodo creato per il sentinel geografico `GLOBAL_MULTI_COUNTRY_UNSPECIFIED`: le implementazioni "globali senza elenco Paesi" restano semplicemente senza edge `IMPLEMENTATO_IN` verso un Paese specifico, invece di puntare a un nodo-Paese fittizio.
- `HA_TIPO` collega Organizzazione (non Implementazione) a CategoriaOrganizzativa, perché la categoria è un attributo dell'organizzazione, non del singolo caso.
- Programma modellato con `Implementazione -[:FA_PARTE_DI]-> Programma` (non `Organizzazione -[:PARTECIPA_A]-> Programma`) perché nel corpus il programma di finanziamento è legato al singolo progetto/round di grant, non necessariamente a tutta l'attività dell'organizzazione.
- `HA_BENEFICIARIO` è multi-tag (come RIPORTA_BENEFICIO/RIPORTA_CRITICITA): un'Implementazione può avere edge verso più label di TipoBeneficiario contemporaneamente.
- `COINVOLGE_UMANO` è multi-tag per lo stesso motivo: un'Implementazione descrive spesso più forme di coinvolgimento umano nello stesso workflow (es. sia validazione pre-uso sia gestione delle eccezioni).
- `REALIZZATO_CON` collega solo organizzazioni/enti esplicitamente co-menzionati nel campo `Organizzazione` con marcatori strutturali ("tramite", "in collaborazione con", "in partnership con", "in co-sviluppo con") — non è Entity Resolution completa (nessun fuzzy-matching contro Organizzazione/Fornitore/Programma già risolti): dimensione di arricchimento con dedup solo su stringa pulita, non primaria.

## Rappresentazione testuale dello schema

```
Organizzazione
  |-- HA_IMPLEMENTAZIONE --> Implementazione
  |-- HA_SEDE_IN ----------> Paese
  |-- HA_TIPO -------------> CategoriaOrganizzativa

Implementazione
  |-- USA_TECNICA ---------> TecnicaIA
  |-- USA_FORNITORE -------> Fornitore
  |-- USA_MODELLO ---------> ModelloIA
  |-- USA_SOFTWARE --------> Software
  |-- HA_FUNZIONE ---------> FunzioneOrganizzativa
  |-- INDIRIZZA_SETTORE ---> SettoreMissione
  |-- RIPORTA_BENEFICIO ---> Beneficio
  |-- RIPORTA_CRITICITA ---> Criticita
  |-- DOCUMENTATO_DA ------> Fonte
  |-- IMPLEMENTATO_IN -----> Paese
  |-- FA_PARTE_DI ---------> Programma
  |-- HA_BENEFICIARIO -----> TipoBeneficiario
  |-- COINVOLGE_UMANO -----> TipoSupervisioneUmana   [NUOVO v4]
  |-- REALIZZATO_CON ------> Collaboratore           [NUOVO v4]
```

## Esempio concreto (TS-AI-00031, Nederlandse Rode Kruis / 510)

```
(ORG-00xxx:Organizzazione {nome:"Nederlandse Rode Kruis..."})-[:HA_IMPLEMENTAZIONE]->(TS-AI-00031:Implementazione)
(ORG-00xxx)-[:HA_SEDE_IN]->(COU-xxx:Paese {nome:"Paesi Bassi"})
(TS-AI-00031)-[:USA_TECNICA]->(TEC-xx:TecnicaIA {nome:"Machine learning predittivo"})
(TS-AI-00031)-[:RIPORTA_BENEFICIO]->(BEN-xx:Beneficio {nome:"Aumento di scala/copertura/volume di utilizzo"})
(TS-AI-00031)-[:HA_BENEFICIARIO]->(TBEN-xx:TipoBeneficiario {nome:"Beneficiario finale della missione"})
(TS-AI-00031)-[:DOCUMENTATO_DA]->(SRC-xxxxx:Fonte {nome:"https://www.rodekruis.nl/..."})
```

## Gap analysis pre-osservatorio pubblico (2026-08-24, v4)

L'utente ha chiesto quali dimensioni di analisi restassero scoperte in vista della pubblicazione di un observatory pubblico interrogabile (guided questions + free-text "ask the dataset"). Identificate e verificate 6 lacune, risolte con esiti diversi:

| Lacuna | Esito |
|---|---|
| Dimensione organizzativa (Dimensione/N_dipendenti/Fatturato) | **Risolto** — dati già puliti nel corpus, mai portati sul grafo; aggiunti a Organizzazione. |
| Fonte_qualificata | **Risolto** — aggiunta come proprietà testuale di Implementazione (non un flag di qualità come inizialmente ipotizzato: è una seconda fonte/citazione). |
| Fallimenti | **Risolto parzialmente** — aggiunta come proprietà testuale grezza di Implementazione, NON come dimensione taggata (59% dei valori sono varianti di "nessuno documentato", non giustifica un vocabolario dedicato). |
| Livello di supervisione umana | **Risolto** — nuova dimensione multi-tag TipoSupervisioneUmana da `Ruolo_operatore_umano` (100% valorizzato, 0 vuoti nel corpus). |
| Collaborazioni multi-stakeholder | **Risolto** — nuovo nodo Collaboratore da organizzazioni/enti esplicitamente co-menzionati nel campo Organizzazione (45 entità, 50 relazioni su 35 record). |
| Funder/Donatore generico | **Non modellato** — vedi nota metodologica sotto. |

**Perché il Funder/Donatore generico non è stato modellato**: un primo tentativo di estrazione libera da `Osservazioni` (pattern "Foundation/Fondazione/Trust/Fund/Institute/Accelerator") ha prodotto ~85 candidati, ma la lettura manuale di quelli con più occorrenze ha mostrato che quasi tutti erano falsi positivi per gli scopi di un "chi finanzia" dimension: duplicati dei 6 Programmi già modellati (AWS, McGovern, Google.org, Salesforce, IBM, data.org), finanziatori della RICERCA/case study invece che dell'implementazione IA (es. "Gates Foundation" nel caso Crisis Text Line finanzia Project Evident, non il progetto IA), o il destinatario dei fondi raccolti invece che la fonte (es. "Global Fund" nel caso (RED): (RED) genera fondi PER il Global Fund, non riceve fondi DA esso). Su ~15 candidati verificati riga per riga, un solo caso si è confermato un finanziamento reale non già coperto (SkillUp Coalition, consorzio di 5 fondazioni filantropiche — Gates, Cognizant, Schultz Family, Charles Koch, Michael & Susan Dell — TS-AI-00139): troppo poco per giustificare una dimensione dedicata con dedup/canonicalizzazione. **Conclusione onesta**: il panorama dei finanziatori nel corpus, oltre ai 6 programmi ricorrenti già modellati, non è sistematicamente documentato nelle fonti primarie raccolte — è un limite dei dati, non una scelta di modellazione. Se l'utente vuole comunque rappresentare il caso SkillUp, può farlo manualmente in un secondo momento.

## Quality check eseguiti (2026-08-24, dopo v4: gap-analysis pre-osservatorio)

- ID_caso del master == ID in implementazioni.csv: **389 = 389** ✓
- Implementazioni duplicate: **0** ✓
- ID nodo duplicati cross-file: **0** ✓
- Relazioni che puntano a nodo inesistente: **0** ✓
- Implementazione senza Organizzazione: **0** ✓
- Implementazione senza Fonte: **0** ✓
- HA_SEDE_IN: 395 righe generate / 380 coppie distinte — dinamica di dedup MERGE identica e già verificata nella v1
- Distribuzione HA_BENEFICIARIO riprodotta identica al run diagnostico: 326 missione / 200 interno / 46 terzo-PA / **0 NON_CLASSIFICATO** (70 ID totali classificati per giudizio — vedi `MANUAL_OVERRIDES` in `beneficiary_tagger.py`)
- Distribuzione COINVOLGE_UMANO: 237 esecuzione/relazione diretta / 120 validazione pre-uso / 103 decisione finale / 92 escalation / 61 interpretazione / **1 solo NON_CLASSIFICATO** (TS-AI-00036, fonte dichiara esplicitamente "non specificato" — gap onesto, non un errore di classificazione) — 19 ID classificati per giudizio, vedi `MANUAL_OVERRIDES` in `human_oversight_tagger.py`
- Organizzazioni con Dimensione valorizzata: 368/371 (99%)
- Collaboratore: 45 nodi, 50 relazioni su 35 record (9%) — coerente con l'attesa: solo i record con marcatori strutturali espliciti nel campo Organizzazione
- Nessuna tassonomia interpretativa nuova introdotta oltre a TipoSupervisioneUmana (i vocabolari delle altre dimensioni sono quelli già approvati negli step precedenti)

## Istruzioni di import in Neo4j (v2 — schema italiano)

Script pronto: `knowledge_layer/import.cypher` (Cypher standard, nessuna dipendenza da APOC — 15 blocchi `LOAD CSV` per i nodi + 15 per le relazioni).

**Se il database Neo4j contiene già la versione inglese (2026-08-20)**: la traduzione non è additiva (i node label e i relationship type sono cambiati, es. `Organization`→`Organizzazione`), quindi il modo più semplice e sicuro è svuotare e ricaricare da zero, invece di rinominare label/relazioni una per una su un grafo già popolato:
1. Aprire Neo4j Browser/Query sul database e lanciare `MATCH (n) DETACH DELETE n;` (cancella tutti i nodi e le relazioni, il database resta).
2. Copiare i nuovi file di `knowledge_layer/nodes/*.csv` e `knowledge_layer/relationships/relationships.csv` nella cartella `import/` del database Neo4j, **sostituendo** i vecchi file inglesi (nomi diversi: es. `implementations.csv` → `implementazioni.csv`, quindi si può anche lasciare la cartella con entrambe le versioni senza conflitto, ma è più pulito rimuovere le vecchie).
3. Eseguire `import.cypher` per intero (sezioni CONSTRAINTS, NODI, RELAZIONI).
4. Verifica rapida post-import con le due query di conteggio in fondo al file — attesi **1.275 nodi** e **6.083 relazioni** in totale.

**Se è il primo import**: saltare il punto 1, il resto è identico.

## Casi che richiedono revisione umana

Non gestiti con un nuovo foglio `MANUAL_REVIEW`: si riusa `DATA_QUALITY_ISSUES` dentro `corpus_working_407rec_2026-09-16.xlsx` (stesso principio di non moltiplicare fogli/file). I 254 record con almeno un tag `NON_CLASSIFICATO` in Funzione/Settore/Beneficio/Criticità (già segnalati in `PROCESS_BENEFIT_CRIT_AUDIT`) semplicemente non generano l'edge corrispondente — nessuna azione bloccante per il caricamento in Neo4j. Tipo_beneficiario_Tags non ha più casi NON_CLASSIFICATO (vedi sezione dedicata sopra).
