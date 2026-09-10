# Ricerca AI Terzo Settore

Un osservatorio di ricerca sull'adozione dell'intelligenza artificiale nelle organizzazioni del Terzo Settore (ONG, non-profit, fondazioni, cooperative sociali) a livello globale: 389 casi verificati manualmente, uno per uno, con fonte primaria citata per ciascuno.

**Osservatorio pubblico (14 analisi guidate, grafici):** https://osservatorio-ai-terzo-settore.lovable.app

## Cosa c'è in questo repository

- `observatory_data.json` — i 14 aggregati statistici alla base dell'osservatorio (tecniche IA più diffuse, ruolo della supervisione umana, chi beneficia realmente delle implementazioni, distribuzione geografica, trend temporale e altro), in formato riusabile da chiunque.
- `knowledge_layer/graph_schema.md` e `knowledge_layer/import.cypher` — lo schema del knowledge graph (Neo4j) su cui è costruita l'analisi: 17 tipi di nodo, le relazioni tra organizzazioni, implementazioni, tecniche, benefici, criticità, supervisione umana, collaborazioni.
- `registro_metodologico.md` — il registro completo, ciclo per ciclo, di come il corpus è stato costruito: criteri di inclusione/esclusione applicati, casi scartati e perché, correzioni metodologiche in corsa, e una nota esplicita sui limiti del campione (non è un censimento, e l'assenza di nuove categorie di tecnica in un ciclo non è mai stata interpretata come segnale di saturazione della varietà reale finché continuavano a emergere nuove organizzazioni).
- `protocollo_ricerca_settimanale.md` — il protocollo che guida i cicli di ricerca ricorrenti che continuano ad ampliare il corpus.
- Script Python (`*_tagger.py`, `*_parser.py`, `build_knowledge_layer.py`, `compute_observatory.py`) — la pipeline riusabile con cui i dati grezzi vengono classificati, taggati e trasformati nel knowledge graph e negli aggregati dell'osservatorio.

## Cosa NON c'è (per scelta, non per dimenticanza)

Il corpus grezzo (i 389 record con i campi di testo libero — problema affrontato, workflow, osservazioni) non è ancora pubblico. Contiene, in un sottoinsieme di casi, riferimenti a persone reali in contesti sensibili (superstiti di violenza, rifugiati, pazienti), che richiedono una revisione dedicata prima di una pubblicazione integrale. Finché quella revisione non è completa, restano pubblici solo i dati aggregati — nessuna narrazione a livello di singolo individuo.

## Come è costruito il corpus

Ogni caso è verificato contro una fonte primaria (sito ufficiale dell'organizzazione, case study del fornitore tecnologico con organizzazione nominata, copertura giornalistica indipendente) prima di essere incluso. Vengono sistematicamente esclusi: enti pubblici o intergovernativi senza un partner del Terzo Settore chiaramente nominato, organizzazioni for-profit anche a missione sociale, iniziative di sola formazione/"AI literacy" senza adozione operativa, documenti di policy senza un caso di implementazione reale, dichiarazioni di intenti prive di evidenza d'uso. I dettagli completi, incluse le correzioni metodologiche applicate in corso d'opera, sono in `registro_metodologico.md`.

La ricerca non si è fermata al 389° caso: un ciclo automatico ricorrente (vedi `protocollo_ricerca_settimanale.md`) continua a cercare nuovi casi con lo stesso rigore, proponendoli in una coda di revisione prima di ogni inclusione nel corpus pubblicato.

## Contribuire

Segnalazioni di casi mancanti, correzioni a casi esistenti o osservazioni sulla metodologia sono benvenute tramite le Issue di questo repository.

## Licenza

Codice sotto licenza MIT, dati e documentazione sotto licenza CC BY 4.0 — vedi [LICENSE](LICENSE).
