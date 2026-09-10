# Protocollo di ricerca settimanale automatica (AI manager)

Questo documento è il riferimento autosufficiente per il ciclo di ricerca automatico ricorrente. Ogni esecuzione deve leggerlo per intero e seguirlo senza deviazioni. Condensa la metodologia già applicata manualmente in 226 cicli e documentata in `registro_metodologico.md` (troppo lungo per essere riletto integralmente a ogni esecuzione).

## Obiettivo del ciclo

Individuare candidati per nuovi casi di adozione IA in organizzazioni del Terzo Settore (ambito globale), da proporre in una coda di revisione umana. Un ciclo automatico non inserisce mai un caso direttamente nel corpus pubblico.

## Unità di osservazione

Un caso valido è un'organizzazione del Terzo Settore (ONG, non-profit, fondazione, cooperativa sociale, ente caritatevole, associazione) che adotta/adatta/implementa un sistema di intelligenza artificiale in un proprio processo operativo specifico. Se la tecnologia è di un fornitore for-profit, il soggetto del record resta l'organizzazione TS adottante, non il fornitore.

## Criteri di esclusione (scarta il candidato se anche una sola condizione è vera)

- Ente pubblico, governativo o intergovernativo, salvo che sia nominato un partner TS chiaramente indipendente che implementa il sistema.
- Organizzazione for-profit, anche con missione sociale dichiarata (B-corp, Public Benefit Corporation, startup "impact").
- Incorporazione accademica/universitaria non autonoma come organizzazione TS.
- Nessuna fonte primaria verificabile (sito ufficiale dell'organizzazione, comunicato con dettagli verificabili, case study del fornitore tecnologico con organizzazione nominata, copertura giornalistica indipendente). Un comunicato auto-pubblicato senza organizzazione nominata non basta.
- Componente IA non confermata (automazione/RPA senza ML, help desk umano, hashing percettivo senza ML esplicito, ecc.).
- Descrizione troppo generica/vaga, priva di specificità tecnica sul workflow.
- Iniziativa di "AI literacy"/formazione, non adozione operativa nei propri processi.
- Documento di policy/governance sull'IA, non un caso di implementazione.
- Grant o programma di finanziamento senza un implementatore TS specifico e nominato.
- Solo intenzioni future/sperimentazioni annunciate, senza evidenza di utilizzo reale.
- Duplicato di un caso già presente nel database (vedi sotto).

## Criteri di inclusione

- Fonte primaria ufficiale sufficiente anche senza KPI quantitativi.
- Verificabilità classificata esplicitamente (alta/media/bassa) nei campi Livello_prova/Grado_verificabilita/Livello_confidenza — un caso con verificabilità bassa può essere incluso se il limite è dichiarato in modo trasparente nelle Osservazioni.
- Workflow operativo e documentabile, non solo dichiarazione d'intenti.

## Gerarchia delle fonti

1. Fonti primarie (sito/organo ufficiale dell'organizzazione) — sempre prevalenti e obbligatorie quando disponibili.
2. Fonti secondarie di approfondimento: PubMed, Candid, Consensus.
3. GitHub, se l'organizzazione sviluppa strumenti propri open source.

## Controllo duplicati (obbligatorio)

1. Prima di redigere un candidato, cerca (grep) il nome dell'organizzazione e parole chiave distintive in `database_casi.csv` e in `corpus_working_389rec_2026-08-20.csv` per intero — non solo nei candidati proposti nelle settimane precedenti.
2. Controlla anche i file già presenti in `revisione_settimanale/` (candidati proposti nei cicli automatici precedenti, non ancora approvati) per non riproporre lo stesso candidato due volte.
3. Dopo aver preparato la lista della settimana, ripeti la verifica incrociata sui nomi organizzazione.
4. In caso di dubbio, segnala il candidato come "possibile duplicato" nelle Osservazioni invece di scartarlo silenziosamente o includerlo senza avviso.

## Protocollo di resilienza per le chiamate a strumenti

1. Un'operazione fallita non è mai considerata completata.
2. Registra l'operazione fallita e l'ultimo punto verificato con successo prima di procedere.
3. Ripeti la chiamata fino a un massimo di 3 tentativi.
4. Applica un'attesa progressiva tra i tentativi quando possibile.
5. Se la fonte continua a non rispondere dopo 3 tentativi, prova una modalità alternativa (query equivalente, fonte istituzionale/scientifica alternativa, altra pagina dello stesso sito).
6. Non duplicare mai risultati già acquisiti.
7. Dopo un ripristino riprendi dall'ultimo elemento verificato, senza ripetere tutto da capo.
8. Prima di chiudere il ciclo verifica che tutte le operazioni previste risultino completate.

## Volume settimanale

Obiettivo indicativo: valutare 8-15 organizzazioni candidate grezze per proporne 3-6 che superano tutti i criteri (tasso di scarto storico del progetto). Non forzare il numero: se una settimana produce 0 casi validi va bene — va riportato onestamente nel log, senza abbassare i criteri per raggiungere una quota.

## Schema campi da compilare per ogni candidato proposto

`ID_caso_proposto` (prefisso "CAND-" + data + progressivo, mai un ID_caso definitivo), `Organization`, `Categoria_organizzativa`, `Status_legale_specifico`, `Paese`, `Anno`, `Problema_affrontato`, `Obiettivo_implementazione`, `Sottoprocesso`, `Workflow_dettagliato`, `Input`, `Output`, `Ruolo_operatore_umano`, `Livello_integrazione` (1-4: uso occasionale / uso strutturato / integrazione workflow / processo ampiamente automatizzato), `Tipo_utilizzo_IA` (vocabolario: ricerca documentale, estrazione dati, classificazione, sintesi, generazione contenuti, revisione, traduzione, analisi semantica, supporto decisionale, automazione workflow, chatbot, analisi predittiva, altro), `Benefici_documentati`, `KPI`, `Tempo_risparmiato`, `ROI`, `Livello_prova`, `Grado_completezza`, `Grado_verificabilita`, `Livello_confidenza`, `Osservazioni`, `Fonte_qualificata` (URL/citazione completa), `Fallimenti` (se noti).

## Cosa non fare mai

- Non modificare `corpus_working_389rec_2026-08-20.*`, `database_casi.*`, la cartella `knowledge_layer/`, `osservatorio_ai_terzo_settore.html`, `registro_metodologico.md`.
- Non inserire candidati direttamente nel corpus pubblico o nel grafo Neo4j.
- Non ripubblicare l'osservatorio o il repository GitHub.
- Non abbassare i criteri di esclusione per raggiungere un numero minimo di casi.

## Classificazione completa (non solo proposta grezza)

L'AI manager applica da solo tutti i criteri, comprese le classificazioni a tag multipli — l'utente non deve rifare questo lavoro caso per caso. Per ogni candidato che supera i criteri, oltre ai campi del PASSO base, compila anche i campi qui sotto così che il record sia già pronto per l'unione nel corpus pubblico (57 colonne di `corpus_working_389rec_2026-08-20.csv`), non solo una bozza.

Regola generale per tutti i campi a tag multipli: **non inventare mai un nuovo valore di tag.** Prima di assegnare un tag, leggi il file dei nodi corrispondente in `knowledge_layer/nodes/` e scegli solo tra i valori già esistenti in quel vocabolario controllato:

- `Tecnica_IA_Tags` → vocabolario in `knowledge_layer/nodes/tecniche_ia.csv`
- `Fornitore_Piattaforma_Tags` → `knowledge_layer/nodes/fornitori_piattaforma.csv` (se il fornitore non è nel file, va bene aggiungerlo solo se è un fornitore reale nominato nella fonte — segnalalo in Osservazioni come "nuovo fornitore proposto")
- `Funzione_organizzativa_Tags` → `knowledge_layer/nodes/funzioni_organizzative.csv`
- `Settore_missione_Tags` → `knowledge_layer/nodes/settori_missione.csv`
- `Beneficio_Tags` → `knowledge_layer/nodes/benefici.csv`
- `Criticita_Tags` → `knowledge_layer/nodes/criticita.csv`
- `Tipo_beneficiario_Tags` → esattamente una o più tra: "Beneficiario finale della missione", "Organizzazione/ente terzo/PA", "Organizzazione/interno" (vedi `beneficiary_tagger.py` per i pattern di riferimento)
- `Supervisione_umana_Tags` → esattamente uno o più tra i 5 valori in `knowledge_layer/nodes/tipi_supervisione_umana.csv` (vedi `human_oversight_tagger.py` per i pattern di riferimento)

Se un candidato non trova corrispondenza chiara in un vocabolario, non forzare un tag: lascialo vuoto per quel campo e spiega il motivo in Osservazioni. Vale lo stesso principio già enunciato sopra: mai abbassare il rigore per completare uno schema.

### Campi geografici
Compila `Organization_Country`, `Implementation_Country` (possono differire), `Geographic_Confidence` (Alta/Media/Bassa) e `Geographic_Evidence_Note` (frase che giustifica la scelta). Imposta `Requires_Human_Review_Geo` = TRUE solo se resta un'ambiguità reale non risolvibile dalla fonte, con nota esplicativa; altrimenti FALSE.

### Entità (Organizzazione/Modello/Software)
Prima di creare una nuova entità, cerca una corrispondenza già esistente in `knowledge_layer/nodes/organizzazioni.csv`, `modelli_ai.csv`, `software.csv` (stesso principio di entity resolution già applicato al corpus: nomi equivalenti, alias noti, stessa organizzazione con grafia diversa). Se trovi corrispondenza, riusa lo stesso ID; altrimenti proponi un nuovo ID nella stessa serie (es. `ORG-NNN`, `MOD-NNN`, `SOFT-NNN` a seconda della convenzione già in uso nei file) e segnala "nuova entità proposta" in Osservazioni.

### Campi non derivabili dalla ricerca
`Dimensione`, `N_dipendenti`, `Fatturato`, `Stato_implementazione`: compila solo se la fonte lo riporta esplicitamente; altrimenti lascia vuoto (mai stimare o inventare). `Tecnologia_utilizzata`, `Modello_AI`, `Software_utilizzato`, `Processo_organizzativo`, `Settore_attivita`, `Tipologia_organizzativa`, `Categoria_organizzativa`, `Status_legale_specifico`: compilali con lo stesso criterio testuale già usato nei 389 record esistenti (valori il più possibile coerenti con quelli già presenti nel corpus, non nuove formulazioni libere).

## Output di ogni ciclo

1. `revisione_settimanale/candidati_AAAA-MM-GG.md` — elenco completo dei candidati proposti (solo quelli che superano tutti i criteri), ciascuno con tutti i campi sopra e un paragrafo di motivazione con citazione della fonte.
2. `revisione_settimanale/candidati_AAAA-MM-GG.csv` — le **stesse 57 colonne, nello stesso ordine, di `corpus_working_389rec_2026-08-20.csv`** (usa quel file come intestazione di riferimento), una riga per candidato approvato, già pronta per essere accodata al corpus. `ID_caso` va lasciato con il prefisso provvisorio `CAND-AAAA-MM-GG-N` (mai un ID_caso definitivo: l'assegnazione dell'ID finale avviene solo in fase di merge).
3. Un'entry in fondo a `log_cicli_automatici.md` con: data, N organizzazioni valutate, N candidati proposti, N scartati con motivo sintetico per categoria di esclusione, eventuali attivazioni del protocollo di resilienza, eventuali possibili duplicati segnalati, eventuali nuove entità/fornitori proposti.
4. Se zero candidati validi: crea comunque l'entry di log con "0 candidati proposti questa settimana" e il motivo — non è un errore, è saturazione locale temporanea di un filone di ricerca.

## Come avviene l'approvazione (una volta a settimana, non caso per caso)

Il ciclo automatico non tocca mai il corpus pubblico, il grafo o l'osservatorio pubblicato: prepara solo i candidati già completamente classificati e pronti. L'utente non deve rivalutare l'inclusione/esclusione di ogni caso (l'ha già fatta l'AI manager) — deve solo dare un'approvazione complessiva del lotto settimanale con un messaggio tipo "approva il ciclo del AAAA-MM-GG". A quel punto, in una sessione interattiva, i candidati approvati vengono accodati a `database_casi.csv` e `corpus_working_389rec_2026-08-20.*` con ID_caso definitivi, si rieseguono gli script di tagging/entity-resolution già esistenti sui nuovi record, si rigenera `knowledge_layer/` con `build_knowledge_layer.py` e `observatory_data.json` con `compute_observatory.py`, e si registra il nuovo ciclo in `registro_metodologico.md`. La ripubblicazione dell'osservatorio (Lovable) e del repository GitHub resta un passo separato ed esplicito, non automatico nemmeno dopo l'approvazione del lotto.
