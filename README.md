# Ricerca AI Terzo Settore

Un osservatorio di ricerca sull'adozione dell'intelligenza artificiale nelle organizzazioni del Terzo Settore (ONG, non-profit, fondazioni, cooperative sociali) a livello globale: 407 casi documentati e ricercati uno per uno, ciascuno con fonte primaria citata e livello di verificabilità dichiarato esplicitamente (non tutti i casi sono ugualmente verificabili né già operativi — vedi "Come è costruito il corpus" più sotto e `registro_metodologico.md`).

**Osservatorio pubblico (14 analisi guidate, grafici):** https://osservatorio-ai-terzo-settore.lovable.app

## Cosa questo dataset NON è

Prima di leggere qualunque numero: questo non è un censimento e non stima la prevalenza reale dell'adozione IA nel Terzo Settore. È una raccolta di casi pubblicamente documentabili, costruita caso per caso a partire da fonti pubbliche esistenti (siti ufficiali, case study di fornitori tecnologici, giornalismo indipendente). Il metodo è strutturalmente distorto verso organizzazioni con presenza web in lingua inglese/europee maggiori e capacità di comunicazione — un risultato pari a zero per un paese o settore significa "non trovato con questo metodo", mai "non esiste". Gli Stati Uniti da soli coprono il 40,5% delle occorrenze-paese; il 78,1% dei record è classificato genericamente "ONG". Il dettaglio completo dei limiti è in [`tassonomia_interpretativa.md`](tassonomia_interpretativa.md) §0 e in `registro_metodologico.md`.

## Cosa c'è in questo repository

- `observatory_data.json` — i 14 aggregati statistici alla base dell'osservatorio (tecniche IA più diffuse, ruolo della supervisione umana, chi beneficia realmente delle implementazioni, distribuzione geografica, trend temporale e altro), in formato riusabile da chiunque.
- `tassonomia_interpretativa.md` — un'analisi interpretativa oltre il semplice conteggio: una tassonomia dell'adozione basata su chi beneficia (non sul livello tecnico, che risulta indipendente), e un finding controintuitivo sulla supervisione umana che cresce, non diminuisce, con la maturità tecnica del sistema.
- `indice_fonti.csv` / `indice_fonti.json` — indice pubblico dei 407 casi con organizzazione, paese, anno, categoria, settore, fonte primaria e fonte qualificata (URL), per verificare ogni caso alla fonte originale. Non include i campi di testo libero del corpus (workflow, osservazioni, problema affrontato): quelli restano non pubblicati per la ragione spiegata sotto.
- `knowledge_layer/graph_schema.md` e `knowledge_layer/import.cypher` — lo schema del knowledge graph (Neo4j) su cui è costruita l'analisi: 17 tipi di nodo, le relazioni tra organizzazioni, implementazioni, tecniche, benefici, criticità, supervisione umana, collaborazioni. Importabile in qualunque istanza Neo4j (anche il piano gratuito AuraDB Free).
- `knowledge_graph.html` / `graph_data.json` — versione pubblica e statica dello stesso knowledge graph, esplorabile nel browser senza bisogno di Neo4j: cerca un'organizzazione, un paese o una tecnica e clicca per espandere i collegamenti diretti. `graph_data.json` esclude gli stessi campi di testo libero dell'Implementazione non pubblicati altrove (vedi sotto); generato da `build_graph_export.py`.
- `registro_metodologico.md` — il registro completo, ciclo per ciclo, di come il corpus è stato costruito: criteri di inclusione/esclusione applicati, casi scartati e perché, correzioni metodologiche in corsa, e una nota esplicita sui limiti del campione (non è un censimento, e l'assenza di nuove categorie di tecnica in un ciclo non è mai stata interpretata come segnale di saturazione della varietà reale finché continuavano a emergere nuove organizzazioni).
- `protocollo_ricerca_settimanale.md` — il protocollo che guida i cicli di ricerca ricorrenti che continuano ad ampliare il corpus.
- Script Python (`*_tagger.py`, `*_parser.py`, `applica_tag_al_corpus.py`, `riclassifica_funzione_organizzativa.py`, `normalizza_corpus.py`, `build_knowledge_layer.py`, `compute_observatory.py`, `build_graph_export.py`, `build_observatory_export.py` — la sequenza di esecuzione è documentata in `protocollo_ricerca_settimanale.md`) — la pipeline riusabile con cui i dati grezzi vengono classificati, taggati e trasformati nel knowledge graph e negli aggregati dell'osservatorio.

## Cosa NON c'è (per scelta, non per dimenticanza)

Il corpus grezzo (i 407 record con i campi di testo libero — problema affrontato, workflow, osservazioni) non è ancora pubblico. Contiene, in un sottoinsieme di casi, riferimenti a persone reali in contesti sensibili (superstiti di violenza, rifugiati, pazienti), che richiedono una revisione dedicata prima di una pubblicazione integrale. Finché quella revisione non è completa, restano pubblici solo i dati aggregati — nessuna narrazione a livello di singolo individuo.

## Come è costruito il corpus

Ogni caso è verificato contro una fonte primaria (sito ufficiale dell'organizzazione, case study del fornitore tecnologico con organizzazione nominata, copertura giornalistica indipendente) prima di essere incluso. Vengono sistematicamente esclusi: enti pubblici o intergovernativi senza un partner del Terzo Settore chiaramente nominato, organizzazioni for-profit anche a missione sociale, iniziative di sola formazione/"AI literacy" senza adozione operativa, documenti di policy senza un caso di implementazione reale, dichiarazioni di intenti prive di evidenza d'uso. I dettagli completi, incluse le correzioni metodologiche applicate in corso d'opera, sono in `registro_metodologico.md`.

**Casi selezionati da un programma di finanziamento ma non ancora operativi.** Una parte dei casi (circa il 31% del corpus) documenta organizzazioni selezionate o finanziate da un programma esterno (es. AWS Imagine Grant, Patrick J. McGovern Foundation, Google.org Accelerator, Salesforce Accelerator, IBM Sustainability/Impact Accelerator) il cui sistema IA è ancora in fase di sviluppo, non ancora pienamente operativo. Questi casi sono inclusi solo quando la fonte descrive un workflow tecnico specifico e nominato (non una semplice dichiarazione di interesse generico verso l'IA), in coerenza con il criterio di esclusione delle "dichiarazioni di intenti prive di evidenza d'uso" sopra. Quando i dati quantitativi riportati sono obiettivi dichiarati dal finanziatore al momento della selezione — non ancora risultati misurati sul campo — questo è segnalato esplicitamente nel dataset (campo interno `Criticita_documentate`, e nel knowledge graph pubblico nel campo `KPI_tipo` quando applicabile) invece di essere presentato come un risultato osservato.

La ricerca non si è fermata al 389° caso: un ciclo automatico ricorrente (vedi `protocollo_ricerca_settimanale.md`) continua a cercare nuovi casi con lo stesso rigore, proponendoli in una coda di revisione prima di ogni inclusione nel corpus pubblicato.

## Contribuire

Segnalazioni di casi mancanti, correzioni a casi esistenti o osservazioni sulla metodologia sono benvenute tramite le Issue di questo repository.

## Licenza

Codice sotto licenza MIT, dati e documentazione sotto licenza CC BY 4.0 — vedi [LICENSE](LICENSE).
