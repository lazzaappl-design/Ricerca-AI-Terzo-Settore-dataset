# Report finale — Fase 1 (correzioni post-diagnosi)
Data: 2026-09-16
Riferimento: `diagnosi_fase0.md` + decisioni di Alessandro ("1. a, b, c; 2 a; 3 a; 4a; 5a; 6 [...]; 7a; 8a")

Questo documento riassume, punto per punto, cosa è stato modificato, con numeri prima/dopo verificati sui file reali (nessuna stima). È il documento da leggere per la verifica finale prima di ripubblicare l'Osservatorio e il repository GitHub.

---

## Punto 1 — Pipeline (a, b, c)

**Cosa significava**: il "percorso" che i dati fanno da file grezzo a pagina pubblica aveva tre problemi: un nome di file storico ormai sbagliato (a), due script con un percorso di file "cablato" che funzionava solo su un computer specifico (b), e un pezzo della pipeline dell'Osservatorio che non era automatizzato come quello del knowledge graph (c).

**1a — Rinominare il corpus e aggiornare i riferimenti**
- `corpus_working_389rec_2026-08-20.csv/json/xlsx` → `corpus_working_407rec_2026-09-16.csv/json/xlsx`
- Aggiornati tutti i riferimenti a questo nome trovati nel progetto: `build_knowledge_layer.py`, `tassonomia_interpretativa.md`, `knowledge_layer/graph_schema.md`, `registro_metodologico.md`.
- Verifica: `git status` mostra questi file come modificati (non nuovi), coerente con un rinomino/aggiornamento di riferimento, non una riscrittura del contenuto.

**1b — Correggere i percorsi assoluti rotti**
- `beneficiary_tagger.py` (riga 191) e `human_oversight_tagger.py` (riga 102) contenevano un percorso assoluto tipo `/sessions/.../mnt/Ricerca AI Terzo Settore/database_casi.csv`, cioè un indirizzo di file valido solo dentro una sessione cloud specifica di lavoro — se tu (o chiunque altro) avessi eseguito questi due script sul tuo computer, avrebbero smesso di funzionare con un errore "file non trovato".
- Corretto in `database_casi.csv` (percorso relativo alla cartella del progetto), come già fanno tutti gli altri script della pipeline.
- Verifica: `grep -n "sessions" *.py` nella cartella del progetto non restituisce più nulla.

**1c — Automatizzare la generazione dell'Osservatorio**
- Prima: `knowledge_graph.html` veniva rigenerato automaticamente da uno script (`build_graph_export.py`) che inietta i dati in un template — ma `osservatorio_ai_terzo_settore.html` veniva aggiornato copiando **a mano** il contenuto di `observatory_data.json` dentro l'HTML. Ogni volta che i dati cambiavano, bisognava ricordarsi di fare questo copia-incolla manualmente, con il rischio concreto di pubblicare una pagina con dati vecchi (è quello che infatti era successo: vedi Punto 6).
- Dopo: creato `osservatorio_template.html` (identico all'HTML pubblico, ma con un segnaposto al posto dei dati) e un nuovo script `build_observatory_export.py`, che funziona esattamente come il suo equivalente per il knowledge graph:
  1. `python3 compute_observatory.py` → ricalcola `observatory_data.json` dai dati aggiornati.
  2. `python3 build_observatory_export.py` → inietta quel JSON in `osservatorio_template.html` e scrive `osservatorio_ai_terzo_settore.html`.
- Verifica fatta: ho confrontato riga per riga l'HTML prodotto da questo nuovo meccanismo con l'originale — la parte "cornice" (tutto il testo, gli stili, gli script attorno) risulta **identica al carattere**, cambia solo il blocco di dati centrale, che ora riflette le correzioni del Punto 6 (compaiono le nuove combinazioni con "Erogazione diretta").
- Documentazione aggiornata di conseguenza: `protocollo_ricerca_settimanale.md` (riga 107) e `README.md` (elenco script) ora citano `build_observatory_export.py` come passo del ciclo settimanale.
- **Cosa NON è cambiato**: la ripubblicazione online (su Lovable) resta un passo manuale ed esplicito, come prima — questo script prepara solo il file HTML corretto, non lo pubblica.

---

## Punto 2 — Stato dell'implementazione (a)

**Cosa significava**: il campo "Stato" originale era testo libero disomogeneo (es. "operativo dal 2023", "in fase pilota", "annunciato"), impossibile da aggregare in modo affidabile.

- Aggiunta nuova colonna `Stato_categoria` in `corpus_working_407rec_2026-09-16.csv`, con 6 valori standard, calcolata a partire dal testo originale (che resta intatto in `Stato`, nessuna informazione persa).
- Distribuzione finale sui 407 casi:

| Categoria | N | % |
|---|---|---|
| Operativo | 225 | 55,3% |
| Annunciato/selezionato in programma (non ancora operativo) | 128 | 31,4% |
| In sviluppo/pilota (generico) | 44 | 10,8% |
| Concluso | 4 | 1,0% |
| Ambiguo/da rivedere | 3 | 0,7% |
| Abbandonato | 3 | 0,7% |

- **Disclosure**: 3 casi non erano classificabili con sufficiente sicurezza in nessuna delle categorie sopra — invece di indovinare, sono stati marcati esplicitamente "Ambiguo/da rivedere". Se vuoi, posso indicarti quali sono i 3 ID_caso.
- Questa colonna è quella ora mostrata nel pannello di dettaglio del knowledge graph pubblico (vedi Punto 1c/9), al posto del campo `Stato` grezzo.

---

## Punto 3 — Anno (a)

**Cosa significava**: il campo "Anno" mischiava anno di implementazione effettiva, anno di annuncio/selezione a un programma di finanziamento e, in alcuni casi, anno di fondazione dell'organizzazione — tre informazioni diverse messe in un unico numero.

- Separato in tre colonne nuove: `Anno_implementazione_effettiva`, `Anno_annuncio_o_selezione`, `Anno_fondazione_organizzazione` (il campo originale `Anno_implementazione` resta invariato).
- Quando il testo originale non permetteva di isolare con sicurezza quale dei tre anni fosse, il record è stato marcato in una quarta colonna, `Anno_da_verificare`, invece di scegliere a caso.
- **Disclosure**: 78 record su 407 (19,2%) sono marcati "da verificare" su questo punto. Questo campo è interno (non esposto nel knowledge graph pubblico) proprio perché segnala un'incertezza che richiede occhio umano, non una risposta pronta per il pubblico.

---

## Punto 4 — Livello di confidenza e grado di verificabilità (a)

**Cosa significava**: questi due campi avevano formulazioni testuali libere e leggermente diverse da un batch di ricerca all'altro (es. "Alto", "alta confidenza", "Medio/Alto"), che rendevano difficile un conteggio aggregato coerente.

- Aggiunte due colonne normalizzate, `Livello_confidenza_normalizzato` e `Grado_verificabilita_normalizzato`, con una scala fissa a 5 valori ciascuna (i campi testuali originali restano intatti).
- Aggiunta anche `Grado_verificabilita_nota`, per i casi in cui la normalizzazione richiedeva un chiarimento (es. verificabilità parziale su una sola fonte secondaria).

| Livello_confidenza_normalizzato | N |
|---|---|
| Medio | 165 |
| Alto | 158 |
| Medio-Alto | 69 |
| Basso-Medio | 14 |
| Basso | 1 |

| Grado_verificabilita_normalizzato | N |
|---|---|
| Alta | 209 |
| Media-Alta | 131 |
| Media | 64 |
| Bassa | 2 |
| Bassa-Media | 1 |

- Questi due campi normalizzati sono ora visibili di default nel pannello di dettaglio del knowledge graph pubblico.

---

## Punto 5 — KPI dichiarati vs. risultati misurati (a)

**Cosa significava**: alcuni casi riportano un KPI come se fosse già un risultato misurato, mentre in realtà è un obiettivo dichiarato da un programma di finanziamento su un caso non ancora operativo (vedi "anticipated impact", Punto 7) — un lettore poco attento potrebbe leggerli come equivalenti.

- Aggiunta colonna `KPI_tipo`, compilata solo dove il testo del KPI segnala esplicitamente un obiettivo/target non ancora misurato (parole chiave tipo "target", "obiettivo", "punta a", "si prevede di", ecc., escludendo i falsi positivi identificati durante la diagnosi).
- Risultato: **65 casi su 407** marcati esplicitamente come "Obiettivo dichiarato/selezione (non ancora misurato)".
- **Disclosure numerica**: la diagnosi iniziale (`diagnosi_fase0.md`) aveva stimato 67 casi con una lista di parole chiave più ampia; nello scrivere lo script ho volutamente ristretto la lista (tolto "non ancora" e "in fase di sviluppo", troppo generiche e fonte di falsi positivi) per essere più preciso. La differenza è di 2 casi ed è dovuta a questo affinamento, non a un errore: se preferisci rivedere personalmente i 2 casi di confine, posso elencarteli.

---

## Punto 6 — Funzione organizzativa: riclassificazione NON_CLASSIFICATO come "Erogazione diretta" (decisione esplicita di Alessandro)

**Cosa significava**: la diagnosi aveva trovato che il 39,8% dei casi (162/407) non rientrava in nessuna delle 18 categorie di "funzione organizzativa" esistenti — non per dati mancanti, ma perché quelle categorie erano pensate per funzioni di back-office (comunicazione, amministrazione, raccolta fondi...) e non includevano nessuna categoria per i servizi erogati direttamente a un beneficiario finale (es. triage, screening, assistenza in emergenza).

- Aggiunta una 19ª categoria, **"Erogazione diretta"**, sia nel vocabolario dei tag (`pbc_tagger.py`) sia come nodo nel knowledge graph (`funzioni_organizzative.csv`).
- Riclassificati **117 dei 162 casi NON_CLASSIFICATO**: 45 sono rientrati in categorie già esistenti (erano casi male etichettati, non casi senza categoria adatta), **72 sono stati taggati "Erogazione diretta"**.
- **45 casi restano NON_CLASSIFICATO** (11,1% del corpus, contro il 39,8% di partenza) — non forzati in nessuna categoria perché il testo disponibile non permette una classificazione sicura nemmeno con la nuova categoria.
- **Bonus non richiesto esplicitamente, ma trovato durante il lavoro e corretto per coerenza**: nello stesso script (`pbc_tagger.py`) c'era un errore di battitura in un'espressione di riconoscimento testuale che cercava "contenuti/contenuto accessibili" ma, per un refuso, non l'avrebbe mai trovata. Corretto (`content\w* accessibil|document\w* accessibil` al posto del pattern rotto). Segnalo questa modifica perché non era tra le 8 richieste esplicite, ma l'ho ritenuta una correzione di coerenza a basso rischio (un semplice bug di un'espressione di ricerca testuale, che non tocca nessun dato).
- Rigenerato tutto il knowledge graph pubblico (`knowledge_layer/`, `graph_data.json`, `knowledge_graph.html`) e l'Osservatorio (`observatory_data.json`, `osservatorio_ai_terzo_settore.html`) per riflettere questa riclassificazione — verificato che il nodo "Erogazione diretta" compare ora correttamente in entrambi con 72 collegamenti.

---

## Punto 7 — Nota pubblica sul criterio "anticipated impact" (a)

**Cosa significava**: circa un terzo del corpus (128/407, vedi Punto 2) sono casi selezionati da un programma di finanziamento ma non ancora operativi — un criterio di inclusione legittimo e già documentato internamente (`registro_metodologico.md`, Ciclo 186), ma non spiegato nel `README.md`, il primo punto di contatto per chi scopre il progetto.

- Aggiunto un nuovo paragrafo in `README.md`, dopo la sezione "Come è costruito il corpus", che spiega: cos'è un caso "selezionato ma non ancora operativo", perché è incluso, quanti sono (~31% del corpus) e dove trovare il criterio metodologico completo (`registro_metodologico.md`).
- Verifica: `grep -n "Casi selezionati da un programma" README.md` → riga 30.

---

## Punto 8 — Ammorbidire "407 verificati" (a)

**Cosa significava**: sia il `README.md` sia la bozza `post_linkedin.md` usavano la parola "verificati" per tutti i 407 casi, mentre in realtà la verificabilità varia da caso a caso (vedi Punto 4) e circa un terzo non è ancora operativo (vedi Punto 7) — un lettore poteva leggere "407 verificati" come "407 casi tutti allo stesso, alto livello di certezza", cosa non accurata.

- **`README.md`**, riga 3 — da: *"...407 casi verificati manualmente, uno per uno, con fonte primaria citata per ciascuno."* a: *"...407 casi documentati e ricercati uno per uno, ciascuno con fonte primaria citata e livello di verificabilità dichiarato esplicitamente (non tutti i casi sono ugualmente verificabili né già operativi — vedi 'Come è costruito il corpus' più sotto e `registro_metodologico.md`)."*
- **`post_linkedin.md`**, riga 5 (Versione 1) e riga 28 (Versione 2) — stessa logica: "407 implementazioni verificate" / "407 casi verificati" → "407 casi documentati", con un rimando esplicito alla verificabilità dichiarata caso per caso.
- Verificato con lettura diretta delle righe modificate in entrambi i file.

---

## File "specchio" del corpus (.json e .xlsx) — azione aggiuntiva, non tra gli 8 punti

Le modifiche dei Punti 2-6 sono state fatte sul file `corpus_working_407rec_2026-09-16.csv` (9 colonne nuove: 57→66). I file `corpus_working_407rec_2026-09-16.json` e `.xlsx`, che dovrebbero essere copie equivalenti dello stesso corpus in altri due formati, non venivano rigenerati automaticamente da nessuno script del progetto — sarebbero rimasti "indietro" rispetto al `.csv`, con il rischio che chi scarica il `.json` o l'`.xlsx` dal repository veda dati vecchi.

Ho quindi rigenerato entrambi direttamente dal `.csv` corretto (407 record, 66 colonne in tutti e tre i formati, verificato). I file precedenti sono salvati come backup in `_backup_prefase1_2026-09-16/mirror_json_xlsx_stale/`, per sicurezza.

---

## Cosa resta aperto (da decidere con te, non ancora toccato)

1. **Claim "varia dal 5% al 15%"** in `osservatorio_ai_terzo_settore.html` (riga 96), riferito alla quota di casi "non classificabili" per dimensione. Numeri reali oggi, verificati sui dati:
   - Funzione organizzativa: 11,1% → **dentro il range**, ora accurato grazie al Punto 6.
   - Supervisione umana: 0,2% → dentro il range (sotto il minimo, quindi ancora più solido).
   - Criticità: 16,2% → leggermente **sopra** il 15% dichiarato.
   - Beneficio: 27,5% → **ben sopra** il 15% dichiarato, non toccato da nessuna delle decisioni prese finora.

   Non ho modificato questa frase perché non era esplicitamente tra le opzioni scelte (il Punto 8 riguardava solo "407 verificati" in README e post_linkedin). Se vuoi, posso: (a) aggiornare la frase con il range reale, (b) lasciarla ma aggiungere un rimando a `tassonomia_interpretativa.md` per il dettaglio dimensione-per-dimensione, o (c) lasciarla invariata.

2. **Ripubblicazione**: tutti i file sono pronti e verificati localmente, ma — come previsto dal protocollo del progetto — la ripubblicazione dell'Osservatorio su Lovable e il push del repository su GitHub restano passi manuali, separati, che decidi tu quando fare.

3. **`post_linkedin.md`**: valuta se, con i numeri e le formulazioni ora aggiornate nel dataset (Punto 6 in particolare), i due paragrafi "finding" del post (quelli su supervisione umana e "doppio uso") vanno ancora bene così, dato che non li ho toccati.

---

## Come verificare tu stesso, in sintesi

- Apri `README.md`, righe 3 e 30: dovresti vedere il nuovo testo del Punto 7 e 8.
- Apri `post_linkedin.md`, righe 5 e 28: stesso ammorbidimento del Punto 8.
- Apri `osservatorio_ai_terzo_settore.html` o `knowledge_graph.html` nel browser: cerca un caso con funzione "Erogazione diretta" (es. prova a cercare "screening" o "triage" nel motore di ricerca della pagina) — dovrebbe comparire come categoria a sé, non più "non classificato".
- Apri `corpus_working_407rec_2026-09-16.csv` (es. in Excel/Numbers): dovresti vedere 66 colonne, con le 9 nuove in fondo (`Stato_categoria`, `Anno_implementazione_effettiva`, ecc.).
- Questo stesso file, `report_finale_fase1_2026-09-16.md`, resta nella cartella del progetto come riferimento permanente di cosa è cambiato e perché.
