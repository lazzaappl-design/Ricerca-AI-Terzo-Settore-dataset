# Decisioni Fase 0 — Ricerca AI Terzo Settore

Registro delle decisioni metodologiche della Fase 0 (pulizia dati), con data, motivazione e stato di applicazione.
Documento di lavoro: viene aggiornato solo su approvazione esplicita di Alessandro.
Riferimenti: `diagnosi_fase0.md` (numeri di base), `report_finale_fase1_2026-09-16.md` (resoconto prima/dopo delle correzioni già applicate).

Regola: i numeri di `diagnosi_fase0.md` prevalgono sulle stime precedenti alla diagnosi.

---

## PARTE 1 — Decisioni già approvate e già applicate ai file

Tutte approvate da Alessandro il 2026-09-16 con il messaggio: "1. a, b, c; 2 a; 3 a; 4a; 5a; 6 in tutti i casi in cui si tratta di erogazione diretta scrivi erogazione diretta; 7a; 8a".
Corrispondenza con le lettere del piano 0b indicata per ciascuna voce.

### D1 — Pipeline: nome del corpus, percorsi rotti, automazione dell'Osservatorio
**(non presente nelle lettere 0b; emersa dalla diagnosi, sezione 1)**
- **Data**: 2026-09-16
- **Decisione**: (a) rinominare `corpus_working_389rec_2026-08-20.*` in `corpus_working_407rec_2026-09-16.*` e aggiornare tutti i riferimenti; (b) sostituire i percorsi assoluti di sessione in `beneficiary_tagger.py` e `human_oversight_tagger.py` con percorsi relativi; (c) creare un meccanismo di rigenerazione automatica dell'Osservatorio.
- **Motivazione**: il nome del file dichiarava 389 record su un corpus di 407 (fonte di errore per chiunque lo legga); i percorsi assoluti avrebbero fatto fallire due script fuori dalla sessione cloud in cui erano stati scritti; l'HTML dell'Osservatorio veniva aggiornato per copia-incolla manuale, quindi poteva restare indietro rispetto ai dati senza che nessuno se ne accorgesse (ed era effettivamente successo).
- **Applicato**: sì. Nuovi file `osservatorio_template.html` e `build_observatory_export.py`; `protocollo_ricerca_settimanale.md` (riga 107) e `README.md` aggiornati.

### D2 — Mappatura di Stato → lettera (b) del piano 0b
- **Data**: 2026-09-16
- **Decisione**: aggiungere la colonna `Stato_categoria` con 6 valori standard, calcolata dal testo libero originale, senza modificare il campo `Stato` di origine.
- **Motivazione**: 310 valori testuali distinti su 407 record rendevano impossibile qualsiasi aggregazione affidabile sullo stato di avanzamento.
- **Risultato verificato (corpus e knowledge layer allineati)**: 225 Operativo / 128 Annunciato-selezionato non ancora operativo / 44 In sviluppo-pilota generico / 4 Concluso / 3 Ambiguo-da rivedere / 3 Abbandonato.
- **Limite dichiarato**: 3 casi non classificabili con sicurezza sono marcati "Ambiguo/da rivedere" invece di essere forzati.
- **Applicato**: sì.

### D3 — Separazione anno di implementazione / data di annuncio → lettera (c)
- **Data**: 2026-09-16
- **Decisione**: separare in tre colonne nuove (`Anno_implementazione_effettiva`, `Anno_annuncio_o_selezione`, `Anno_fondazione_organizzazione`), lasciando invariato `Anno_implementazione`; marcare in `Anno_da_verificare` i casi in cui il testo non permette di isolare l'anno con sicurezza.
- **Motivazione**: 258/407 (63,4%) del campo Anno non era un anno singolo pulito; in parte dei casi il numero era la data di un annuncio, non di un'implementazione.
- **Limite dichiarato**: 78/407 (19,2%) restano marcati "da verificare". Campo interno, non esposto nelle pagine pubbliche.
- **Applicato**: sì.

### D4 — Uniformazione confidenza e verificabilità → lettera (d)
- **Data**: 2026-09-16
- **Decisione**: aggiungere `Livello_confidenza_normalizzato` e `Grado_verificabilita_normalizzato` su scale fisse a 5 valori, più `Grado_verificabilita_nota` per i casi che richiedono un chiarimento; campi originali invariati.
- **Motivazione**: 10 valori letterali per la confidenza e 67 per la verificabilità, riducibili a 5-6 categorie reali: differenze di maiuscole e ordine delle parole, non di sostanza.
- **Applicato**: sì.

### D5 — KPI che non sono risultati → lettera (e)
- **Data**: 2026-09-16
- **Decisione**: aggiungere la colonna `KPI_tipo`, compilata solo dove il KPI dichiarato è un obiettivo o una selezione, non un risultato misurato.
- **Motivazione**: un lettore non attento può leggere come risultato conseguito un numero che la fonte dichiara come obiettivo futuro.
- **Risultato**: 65/407 marcati. **Scostamento dichiarato**: la diagnosi ne stimava 67; la differenza di 2 nasce da un affinamento delle parole chiave fatto in fase di implementazione per ridurre falsi positivi (rimossi "non ancora" e "in fase di sviluppo", troppo generici). I 2 casi di confine non sono stati ancora rivisti manualmente.
- **Applicato**: sì.

### D6 — Casi senza funzione organizzativa → lettera (f)
- **Data**: 2026-09-16
- **Decisione**: aggiungere una 19ª categoria "Erogazione diretta" al vocabolario e riclassificare i casi non classificati che descrivono un servizio erogato direttamente a un beneficiario finale.
- **Motivazione**: la diagnosi ha verificato che 0 dei 162 casi NON_CLASSIFICATO aveva il campo sorgente vuoto: non mancavano i dati, mancava una categoria. Le 18 categorie esistenti erano pensate per funzioni di back-office e non coprivano le attività di prima linea (triage, screening, accoglienza, risposta alle emergenze).
- **Risultato**: 162 → 45 NON_CLASSIFICATO (39,8% → 11,1%). 72 casi taggati "Erogazione diretta", 45 rientrati in categorie già esistenti.
- **Limite dichiarato**: 45 casi restano non classificati, non forzati.
- **Correzione collaterale**: corretto in `pbc_tagger.py` un errore di espressione di ricerca che impediva di riconoscere "contenuti/documenti accessibili".
- **Applicato**: sì.

### D7 — Nota pubblica sul criterio "anticipated impact" → lettera (a), parte relativa alla trasparenza
- **Data**: 2026-09-16
- **Decisione**: aggiungere al `README.md` un paragrafo che spiega il criterio di inclusione dei casi selezionati in un programma di finanziamento ma non ancora operativi, la loro quota (~31%) e il rimando al `registro_metodologico.md`.
- **Motivazione**: il criterio era documentato internamente (Ciclo 186, 2026-08-06) ma non nel primo punto di contatto pubblico, dove generava una tensione apparente con il criterio di esclusione delle "dichiarazioni di intenti".
- **Applicato**: sì (README.md, riga 30).
- **NOTA**: questa decisione riguarda solo la *dichiarazione* del criterio. La scelta di perimetro (includere / separare / escludere dal perimetro principale) è ancora aperta: vedi sezione "Decisioni aperte", voce A.

### D8 — "Implementazioni verificate" → "casi documentati" → lettera (g)
- **Data**: 2026-09-16
- **Decisione**: sostituire le formulazioni "407 implementazioni verificate" / "407 casi verificati" con "407 casi documentati", aggiungendo il rimando al livello di verificabilità dichiarato caso per caso.
- **Motivazione**: "verificato" suggeriva un livello di certezza uniforme che i dati non sostengono (la verificabilità varia per caso e ~42% non è operativo).
- **Applicato**: sì (README.md riga 3; post_linkedin.md righe 5 e 28).

### D9 — Perimetro dei casi selezionati ma non operativi → lettera (a), parte relativa al perimetro
- **Data**: 2026-09-16
- **Decisione**: opzione A — includere i casi non operativi nel corpus e nel perimetro principale, dichiarandolo. Nessuna stratificazione obbligatoria dei numeri pubblici per stato, nessuna esclusione dal perimetro.
- **Motivazione di contesto**: la visibilità dello stato di ciascun caso è comunque garantita a livello di singolo record dal filtro per stato e dall'indicatore di solidità della prova già previsti nel catalogo "Trova esperienze simili" (piano, fase 2a). La dichiarazione del criterio è già nel README (D7).
- **Numeri di riferimento**: 225 operativi / 128 annunciati-selezionati non operativi / 44 in sviluppo-pilota / 10 altro. Casi non operativi: 172/407 (42,3%). Di questi, 19 non documentano alcun contenuto oltre la selezione al bando.
- **Rischio accettato consapevolmente**: un lettore che si ferma al numero di testa ("407 casi documentati") può percepirlo come più solido di quanto la composizione del corpus sostenga. Mitigazione affidata al livello di dettaglio della pagina, non al titolo.
- **Applicato**: nessuna modifica ai dati necessaria (conferma dello stato attuale).

---

### D10 — Casi senza Beneficio e senza Criticità classificati → non presente nelle lettere 0b, emersa il 2026-09-16
- **Data**: 2026-09-16
- **Decisione**: opzione 1, "variante prudente". Correggere le regole di riconoscimento di `pbc_tagger.py` solo dove sono concettualmente corrette:
  1. Criticità — riconoscere i sinonimi realmente usati nel corpus per i limiti di fonte ("fornitore tecnologico" oltre a "vendor", "mancano fonti indipendenti" oltre a "mancano valutazioni indipendenti", "comunicato stampa ufficiale" oltre a "del/istituzionale");
  2. Criticità — nuova categoria "Dato non ancora misurato/proiezione dichiarata ('anticipated impact')";
  3. Beneficio — nuova categoria "Beneficio futuro dichiarato (obiettivo non ancora misurato)", agganciata alla sola formula "obiettivo dichiarato" usata dal progetto;
  4. Beneficio — riconoscere un aggettivo interposto tra numero e sostantivo nel pattern di scala ("122 nuovi utenti", oggi non riconosciuto).
- **Esplicitamente ESCLUSO dalla decisione**: l'allargamento del pattern monetario ("5 milioni di dollari"), che avrebbe portato "Impatto economico/finanziario quantificato" da 86 a 124 casi contando come impatto economico prodotto dall'IA degli importi di bandi *ricevuti*. Stesso errore concettuale del tag "vincita di un grant" scartato in precedenza.
- **Motivazione**: i casi NON_CLASSIFICATO non sono casi privi di informazione (verificato: 0 su 112 con campo sorgente vuoto) ma casi in cui il vocabolario del classificatore è cieco a formulazioni che il corpus usa correntemente. Dichiararli "non classificabili" sarebbe un'affermazione sullo strumento, non sulle fonti, e non veritiera.
- **Effetto atteso, misurato in test (nessun file ancora modificato)**:
  - Beneficio NON_CLASSIFICATO: 114 → 62 (15,2%); nuova categoria "Beneficio futuro dichiarato" = 75; "Impatto economico" invariato a 86.
  - Criticità NON_CLASSIFICATO: 68 → 47 (11,5%); "Limiti della fonte" 21 → 58; "Nessuna criticità documentata" invariato a 295.
- **Risultato di ricerca esplicitamente preservato**: i 282 casi (69,3%) che non documentano alcuna criticità restano classificati come tali e non sono toccati. Sono un esito della ricerca, non un difetto.
- **Applicato**: NO. In attesa della fase 0c, come da regola "nessuna modifica finché tutte le decisioni della fase 0b non sono approvate".

---

### D11 — Affermazioni numeriche scritte a mano nella pagina dell'Osservatorio → voce C
- **Data**: 2026-09-16
- **Decisione**: opzione 1 — correzione manuale una tantum delle frasi, effettuata in `osservatorio_template.html` (mai nella pagina generata), con i numeri verificati al momento della correzione. Nessuna generazione automatica delle frasi.
- **Frasi interessate (5, tutte nel testo fisso della pagina)**:
  1. riga 96 — "non classificabili: dal 5% al 15% a seconda della dimensione". Falsa su entrambi i lati: 5 dimensioni su 8 sono a 0%, nessuna al 5%; Beneficio 27,5% oggi, 15,2% dopo D10.
  2. riga 89 — "Stati Uniti: 40,5% delle occorrenze-paese". Ricalcolo odierno: 51,8% (su 898 occorrenze, relazioni IMPLEMENTATO_IN + HA_SEDE_IN). Da riverificare con la definizione originale di "occorrenza-paese" prima di riscrivere.
  3. riga 90 — "78,1% dei record è ONG generica". Ricalcolo: 77,7%, ma su 386 organizzazioni, non su 407 record: va corretto anche il denominatore citato.
  4. riga 98 — "N_dipendenti e Fatturato disponibili per 5% e 1%". Non ancora verificata.
  5. riga 75 — "raccolti, verificati e strutturati": residuo non applicato della decisione (g)/D8, da chiudere nella stessa passata.
- **Motivazione della scelta**: contenere il lavoro tecnico e arrivare prima alla pubblicazione.
- **Rischio accettato consapevolmente**: queste frasi non vengono ricalcolate dalla pipeline, quindi tornano a invecchiare al primo ciclo settimanale che modifica i dati, senza che nulla lo segnali. È lo stesso meccanismo che ha prodotto l'errore odierno del "5-15%".
- **Mitigazione proposta, da confermare in fase 0c**: aggiungere a `protocollo_ricerca_settimanale.md` un punto di controllo esplicito — a ogni congelamento di una versione pubblica, riverificare a mano le cinque frasi numeriche. Costo nullo, trasforma una deriva silenziosa in una voce di checklist.
- **Applicato**: NO. Rinviato alla fase 0c.

---

### D12 — Riproducibilità delle correzioni nella pipeline → voce D
- **Data**: 2026-09-16
- **Decisione**: opzione 2 — salvare nel progetto gli script che hanno prodotto le correzioni e inserirli nella sequenza documentata della pipeline, così che i casi dei cicli settimanali nascano già con tutte le colonne derivate.
- **Motivazione**: la logica di D2, D3, D4, D5 e D6 esisteva solo in due file nell'area temporanea del computer, che viene svuotata alla chiusura della sessione. Conseguenze: i casi nuovi sarebbero arrivati con celle vuote senza errori visibili; e soprattutto `Stato_categoria` era una colonna della quale nessuno, nemmeno l'autore della ricerca, poteva ricostruire la derivazione — un problema di provenienza del dato in un progetto che si regge sulla trasparenza metodologica.
- **Eseguito il 2026-09-16**:
  1. `arricchisci_corpus.py` → salvato nel progetto come **`normalizza_corpus.py`**, con intestazione che documenta le 9 colonne prodotte, la decisione di riferimento per ciascuna e quando va eseguito.
  2. `riclassifica_funzione.py` → salvato come **`riclassifica_funzione_organizzativa.py`**, con la stessa documentazione.
  3. **Difetto trovato e corretto durante la verifica**: `normalizza_corpus.py` non era idempotente — rieseguito su un corpus già normalizzato portava le colonne da 66 a **75**, duplicando le 9 colonne derivate invece di aggiornarle. Al primo ciclo settimanale avrebbe corrotto il corpus senza produrre nessun errore visibile. Corretto (le colonne già presenti vengono aggiornate, non riaggiunte).
  4. **Verifica di idempotenza superata**: rieseguendo entrambi gli script su una copia del corpus attuale si ottiene un file **identico byte per byte** all'originale. Questo dimostra anche che lo stato attuale del corpus è esattamente riproducibile a partire da questi due script: le colonne derivate hanno ora una provenienza verificabile.
- **Ancora da fare in fase 0c**: inserimento della sequenza completa in `protocollo_ricerca_settimanale.md` e citazione dei due script nel `README.md`.
- **Nota di metodo**: la verifica è stata eseguita su una copia in area temporanea; il corpus del progetto non è stato toccato.

---

## PARTE 2 — Obblighi di processo non ancora assolti

Queste non sono decisioni da prendere, sono passaggi previsti dalle regole di lavoro e non ancora eseguiti. Vanno chiusi prima della fase 0d.

1. **Nuova sezione in `registro_metodologico.md`** che documenta le correzioni D1-D8. L'ultima sezione del registro è ancora "Scoperta di due rami paralleli (2026-09-11/15)": le correzioni di oggi non sono nel registro.
2. ~~**Riproducibilità delle correzioni**~~ — **RISOLTA il 2026-09-16, vedi D12** (resta il solo inserimento nel protocollo settimanale). Testo originale del problema: Le colonne di D2, D3, D4, D5 e la riclassificazione di D6 sono state prodotte da due script temporanei (`arricchisci_corpus.py`, `riclassifica_funzione.py`) scritti nell'area di lavoro temporanea del computer e **non salvati nel progetto**. Conseguenza concreta: i nuovi casi dei cicli settimanali **non nascerebbero già corretti** — non avrebbero `Stato_categoria`, `KPI_tipo`, gli anni separati né le etichette normalizzate. Questo contrasta con la regola "le correzioni si fanno alla fonte, poi si riesegue la pipeline". Va deciso come sanare (vedi voce D tra le decisioni aperte).
3. **Controllo manuale su ~10 casi a campione** da parte di Alessandro (previsto dalla fase 0c): non ancora fatto.
4. **Aggiornamento di `protocollo_ricerca_settimanale.md`** limitato finora al solo passo di rigenerazione dell'Osservatorio; manca la parte sui nuovi campi derivati.
5. **Congelamento di una versione "dati aggiornati al [data]"** per la pubblicazione (fase 0d): non ancora fatto.
6. **Riferimento obsoleto** dentro `diagnosi_fase0.md`: il riepilogo cita ancora `corpus_working_389rec_2026-08-20.csv` come file in uso, nome superato da D1. Da correggere con una nota, senza riscrivere la diagnosi.

---

## PARTE 3 — Decisioni aperte, in ordine di presentazione

- ~~A. Perimetro dei casi selezionati ma non operativi~~ — **DECISA il 2026-09-16, opzione A: vedi D9.**
- ~~B. Casi senza Beneficio e senza Criticità classificati~~ — **DECISA il 2026-09-16, opzione 1 (variante prudente): vedi D10.**
- ~~C. Claim pubblico "dal 5% al 15%"~~ — **DECISA il 2026-09-16, opzione 1 (correzione manuale nel template): vedi D11.**
- ~~D. Riproducibilità delle correzioni nella pipeline~~ — **DECISA il 2026-09-16, opzione 2: vedi D12.**
- **E. Meta tag Open Graph** per l'anteprima LinkedIn: non presenti. Appartiene alla fase 2b, registrata qui per non perderla.

---

*Ultimo aggiornamento: 2026-09-16*
