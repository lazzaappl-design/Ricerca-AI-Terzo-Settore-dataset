# Tassonomia interpretativa dell'adozione IA nel Terzo Settore

Questo documento nasce da un limite esplicito dell'osservatorio pubblicato finora: mostrava conteggi (quante volte compare una tecnica, quanti casi in un settore) ma non un'interpretazione — non diceva cosa quei numeri significano insieme, né riorganizzava le dimensioni già costruite (beneficiario, livello di integrazione, supervisione umana) in un modello coerente. Qui si parte dai dati per far emergere pattern reali, non per imporne uno a priori: dove i numeri non mostrano un pattern netto, lo si dichiara.

Base: i 407 casi di `corpus_working_389rec_2026-08-20.csv` (nome file storico, mantenuto per continuità — il corpus è cresciuto oltre i 389 record originari), incrociando `Tipo_beneficiario_Tags`, `Livello_integrazione`, `Supervisione_umana_Tags`, `Dimensione` (organizzazione), geografia e tipo organizzativo. *(Aggiornato il 2026-09-15: tutti i numeri di questo documento sono stati ricalcolati da zero sul corpus a 407 record dopo la fusione di due rami di ricerca paralleli — vedi `registro_metodologico.md`, sezione "Scoperta di due rami paralleli". I pattern descritti si confermano sostanzialmente stabili rispetto alla prima versione a 389 casi, il che è di per sé un'indicazione preliminare di robustezza, non ancora una prova di generalizzabilità.)*

## 0. Limiti di copertura, dichiarati prima di ogni interpretazione

Qualunque pattern descritto sotto va letto tenendo conto di questi squilibri strutturali del campione:

- **Concentrazione geografica**: gli Stati Uniti da soli coprono il 40,5% delle occorrenze-paese (208 su 514 occorrenze totali, contando i casi multi-paese separatamente, su 79 paesi distinti rappresentati); 36 paesi hanno una sola occorrenza documentata. Qualunque differenza regionale osservata nel corpus rischia di riflettere la disponibilità di fonti in lingua inglese più che una reale differenza di adozione.
- **Concentrazione organizzativa**: il 78,1% dei record (318/407) è classificato genericamente come "ONG/organizzazione non governativa"; le cooperative sociali sono 3, le imprese sociali 2, le organizzazioni di ricerca no-profit 1. Confrontare "tipi di organizzazione" ha quindi senso solo in modo molto approssimativo.
- **Numerosità**: 407 casi, raccolti da fonti pubbliche esistenti (non un censimento). I pattern descritti sotto sono associazioni osservate nel campione disponibile, non stime di prevalenza nella popolazione reale delle organizzazioni del Terzo Settore.

Questi limiti non invalidano i pattern che seguono, ma ne restringono la portata: sono letture di *questo* corpus, da trattare come ipotesi di lavoro da verificare mano a mano che il corpus cresce (il ciclo di ricerca settimanale, vedi `protocollo_ricerca_settimanale.md`, serve anche a questo), non come conclusioni definitive sul settore.

## 1. Una tassonomia a partire da "chi beneficia", non dal livello tecnico

Il primo tentativo naturale di tassonomia sarebbe stato un modello lineare di maturità (dal pilota all'automazione piena). I dati non lo sostengono: **il livello di integrazione tecnica e il tipo di beneficiario sono sostanzialmente indipendenti** — la quota di casi orientati alla missione resta tra il 69% (Livello 1, solo 13 casi, campione piccolo) e l'86% a ogni livello di integrazione successivo (Finding 1, §3). Non esiste quindi una progressione "più tecnicamente maturo = più vicino alla missione" né il contrario.

La tassonomia che segue si basa invece sulla combinazione effettiva di chi beneficia, che il campo `Tipo_beneficiario_Tags` già cattura come tag multipli (un caso può avere più beneficiari contemporaneamente). Le combinazioni osservate nel corpus si raggruppano in 4 tipi con numerosità sufficiente per essere trattati come categorie reali:

| Tipo | N | % | Descrizione |
|---|---|---|---|
| **Missione pura** | 166 | 40,8% | Il sistema serve esclusivamente i beneficiari finali (rifugiati, pazienti, comunità...) — nessun beneficio interno o verso terzi documentato. |
| **Ibrido missione-interno** | 138 | 33,9% | Il sistema serve sia i beneficiari finali sia l'organizzazione stessa (es. uno strumento che aiuta gli operatori a essere più efficaci *e* riduce il loro carico di lavoro). |
| **Efficientamento interno puro** | 54 | 13,3% | Il sistema serve solo l'organizzazione (backoffice, produttività interna, riduzione costi) — nessun beneficio diretto dichiarato per i destinatari della missione. |
| **Coinvolge terzi/PA** | 49 | 12,0% | Il sistema coinvolge enti terzi, pubblica amministrazione o partner istituzionali (da solo o in combinazione con missione/interno) — la quota più eterogenea. |

**Finding 2 — l'adozione "a doppio uso" è la norma quasi quanto quella pura**: il tipo ibrido missione-interno (33,9%) resta quasi grande quanto il tipo missione pura (40,8%). Questo smentisce l'idea che l'adozione IA nel settore si divida nettamente tra "per i beneficiari" e "per noi stessi": nella maggioranza dei casi documentati con beneficio interno (148 su 204, il 72,5%), quel beneficio interno si accompagna a un beneficio per la missione, non lo sostituisce. L'"efficientamento interno puro" (13,3%) è una minoranza reale ma non marginale — e merita di essere segnalata separatamente in ogni comunicazione pubblica del corpus, perché è la categoria più esposta al rischio di essere presentata come "IA per la missione" quando non lo è.

## 2. Un secondo asse: la supervisione umana non diminuisce con la maturità tecnica

**Finding 3 (controintuitivo)**: se si assume che "più il sistema è integrato/maturo, meno serve il controllo umano", i dati mostrano l'opposto. Il numero medio di meccanismi di supervisione umana dichiarati per caso (quanti dei 5 tipi di `Supervisione_umana_Tags` sono presenti insieme) *cresce* con il livello di integrazione:

| Livello di integrazione | N casi | Media meccanismi di supervisione |
|---|---|---|
| Livello 1 (sperimentazione) | 13 | 1,23 |
| Livello 1-2 | 73 | 1,55 |
| Livello 2 (uso strutturato) | 153 | 1,50 |
| Livello 2-3 | 18 | 1,56 |
| Livello 3 (integrazione workflow) | 123 | 1,65 |
| Livello 4 (processo automatizzato) | 27 | 1,74 |

In particolare, la quota di casi in cui un umano "mantiene l'esecuzione/relazione diretta" sale dal 46% al Livello 1 al 74% al Livello 4, e la validazione umana pre-uso resta nello stesso ordine di grandezza o cresce (39% → 48%). Solo la "supervisione per eccezioni/escalation" cala nettamente ai livelli più alti (dal 45% del Livello 1-2 al 7% del Livello 4) — suggerendo che ai livelli di maggiore automazione il controllo umano non sparisce ma si sposta da un intervento *reattivo* (si interviene solo quando qualcosa va storto) a un coinvolgimento *strutturale* (l'umano resta parte del processo per definizione, non solo come rete di sicurezza).

**Lettura**: nel corpus, "più automatizzato" nel Terzo Settore tende a significare "automazione assistita a più livelli", non "sostituzione del giudizio umano". È una lettura compatibile con l'osservazione indipendente che il 58,7% di tutti i casi del corpus mantiene comunque l'esecuzione/relazione diretta umana come meccanismo di supervisione — qui si aggiunge che questa quota è più alta, non più bassa, proprio ai livelli di integrazione più avanzati.

## 3. Un sottogruppo da segnalare: supervisione minima

92 casi su 407 (22,6%) hanno un solo meccanismo di supervisione dichiarato, ed è "esecuzione/relazione diretta" — cioè il grado di coinvolgimento umano documentato più basso possibile nel vocabolario adottato. Questo sottogruppo non è distribuito casualmente: è concentrato ai Livelli 2-3 (71 casi su 92, il 77,2% del sottogruppo). Non implica che questi casi siano problematici — nella maggior parte dei casi la fonte non descrive semplicemente meccanismi ulteriori, non ne esclude l'esistenza — ma è la lista naturale da cui partire per un controllo di criticità futuro (in relazione al campo `Criticita_Tags` già presente nel corpus), qualora si voglia approfondire dove il controllo umano documentato è più debole.

## 4. Riepilogo dei 4 findings

1. **Livello di integrazione tecnica e beneficiario non sono correlati** — vanno trattati come due assi indipendenti, non come stadi di una stessa progressione.
2. **L'adozione "a doppio uso" (missione + interno) resta quasi grande quanto quella orientata solo alla missione** (33,9% vs 40,8%) — la dicotomia netta "per i beneficiari" vs "per l'organizzazione" semplifica eccessivamente la realtà del corpus.
3. **La supervisione umana non diminuisce con la maturità tecnica: cambia natura**, da reattiva (intervento su eccezione) a strutturale (presenza costante nell'esecuzione o nella validazione).
4. **Quasi un quarto dei casi (22,6%) dichiara un solo meccanismo di supervisione**, concentrato ai livelli intermedi di integrazione — un sottogruppo utile per future verifiche di criticità, non un'anomalia di per sé.

Tutti e 4 vanno letti alla luce dei limiti di copertura dichiarati al §0: sono pattern di *questo* corpus, non stime definitive sul settore. Il fatto che si confermino, con scostamenti minimi, dopo la crescita del corpus da 389 a 407 casi (+18 record, di cui 14 provenienti da un ramo di ricerca indipendente con metodologia leggermente diversa ma criteri di inclusione comparabili) è un primo segnale di stabilità dei pattern, non ancora una prova di generalizzabilità al settore nel suo complesso.
