// =====================================================================
// Import knowledge_layer -> Neo4j
// Ricerca AI Terzo Settore — v2, schema in italiano, generato 2026-08-24
// (sostituisce la versione 2026-08-20 in inglese: node label, relationship
// type e property key ora in italiano; i VALORI erano già in italiano)
//
// ATTENZIONE — se hai già caricato la versione precedente (inglese):
// questa NON è una modifica additiva. Prima di eseguire questo script,
// svuota il database esistente con:
//   MATCH (n) DETACH DELETE n;
// (poi ricrea i CONSTRAINT ed esegui l'import da zero — più semplice e
// sicuro di rinominare label/relazioni una per una su un grafo già popolato).
//
// Prima di eseguire: copiare tutti i file di knowledge_layer/nodes/ e
// knowledge_layer/relationships/relationships.csv nella cartella import/ di Neo4j
// (Neo4j Desktop: pulsante '...' sul DB -> Open folder -> Import — sostituire
// i vecchi file inglesi con questi nuovi file italiani, stessi nomi diversi).
// Eseguire in ordine: 0) PULIZIA (se necessario), 1) CONSTRAINTS, 2) NODI, 3) RELAZIONI.
// Nessuna dipendenza da APOC: solo Cypher standard.
// =====================================================================

// --------------------- 0) PULIZIA DATABASE ESISTENTE (eseguire solo se il DB contiene già lo schema inglese) ---------------------
// MATCH (n) DETACH DELETE n;
// DROP CONSTRAINT implementation_id_unique IF EXISTS;
// DROP CONSTRAINT organization_id_unique IF EXISTS;
// DROP CONSTRAINT country_id_unique IF EXISTS;
// DROP CONSTRAINT aimodel_id_unique IF EXISTS;
// DROP CONSTRAINT software_id_unique IF EXISTS;
// DROP CONSTRAINT organizationcategory_id_unique IF EXISTS;
// DROP CONSTRAINT aitechnique_id_unique IF EXISTS;
// DROP CONSTRAINT vendor_id_unique IF EXISTS;
// DROP CONSTRAINT organizationalfunction_id_unique IF EXISTS;
// DROP CONSTRAINT missionsector_id_unique IF EXISTS;
// DROP CONSTRAINT benefit_id_unique IF EXISTS;
// DROP CONSTRAINT criticity_id_unique IF EXISTS;
// DROP CONSTRAINT program_id_unique IF EXISTS;
// DROP CONSTRAINT source_id_unique IF EXISTS;

// --------------------- 1) CONSTRAINTS (id univoco per label) ---------------------
CREATE CONSTRAINT implementazione_id_unique IF NOT EXISTS FOR (n:Implementazione) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT organizzazione_id_unique IF NOT EXISTS FOR (n:Organizzazione) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT paese_id_unique IF NOT EXISTS FOR (n:Paese) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT modelloia_id_unique IF NOT EXISTS FOR (n:ModelloIA) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT software_id_unique IF NOT EXISTS FOR (n:Software) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT categoriaorganizzativa_id_unique IF NOT EXISTS FOR (n:CategoriaOrganizzativa) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT tecnicaia_id_unique IF NOT EXISTS FOR (n:TecnicaIA) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT fornitore_id_unique IF NOT EXISTS FOR (n:Fornitore) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT funzioneorganizzativa_id_unique IF NOT EXISTS FOR (n:FunzioneOrganizzativa) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT settoremissione_id_unique IF NOT EXISTS FOR (n:SettoreMissione) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT beneficio_id_unique IF NOT EXISTS FOR (n:Beneficio) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT criticita_id_unique IF NOT EXISTS FOR (n:Criticita) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT programma_id_unique IF NOT EXISTS FOR (n:Programma) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT fonte_id_unique IF NOT EXISTS FOR (n:Fonte) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT tipobeneficiario_id_unique IF NOT EXISTS FOR (n:TipoBeneficiario) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT tiposupervisioneumana_id_unique IF NOT EXISTS FOR (n:TipoSupervisioneUmana) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT collaboratore_id_unique IF NOT EXISTS FOR (n:Collaboratore) REQUIRE n.id IS UNIQUE;

// --------------------- 2) CARICAMENTO NODI ---------------------
// Implementazione <- implementazioni.csv
LOAD CSV WITH HEADERS FROM 'file:///implementazioni.csv' AS row
MERGE (n:Implementazione {id: row.id})
SET n.nome = row.nome, n.Anno = row.Anno, n.Stato = row.Stato, n.Problema = row.Problema, n.Obiettivo = row.Obiettivo, n.Sottoprocesso = row.Sottoprocesso, n.Workflow_dettagliato = row.Workflow_dettagliato, n.Input = row.Input, n.Output = row.Output, n.Ruolo_umano = row.Ruolo_umano, n.Livello_integrazione = row.Livello_integrazione, n.KPI = row.KPI, n.Tempo_risparmiato = row.Tempo_risparmiato, n.ROI = row.ROI, n.Livello_prova = row.Livello_prova, n.Grado_completezza = row.Grado_completezza, n.Grado_verificabilita = row.Grado_verificabilita, n.Livello_confidenza = row.Livello_confidenza, n.Osservazioni = row.Osservazioni, n.Fonte_qualificata = row.Fonte_qualificata, n.Fallimenti = row.Fallimenti;

// Organizzazione <- organizzazioni.csv
LOAD CSV WITH HEADERS FROM 'file:///organizzazioni.csv' AS row
MERGE (n:Organizzazione {id: row.id})
SET n.nome = row.nome, n.Tipo_organizzazione = row.Tipo_organizzazione, n.Status_legale = row.Status_legale, n.Dimensione = row.Dimensione, n.Dimensione_dettaglio = row.Dimensione_dettaglio, n.N_dipendenti = row.N_dipendenti, n.Fatturato = row.Fatturato;

// Paese <- paesi.csv
LOAD CSV WITH HEADERS FROM 'file:///paesi.csv' AS row
MERGE (n:Paese {id: row.id})
SET n.nome = row.nome;

// ModelloIA <- modelli_ia.csv
LOAD CSV WITH HEADERS FROM 'file:///modelli_ia.csv' AS row
MERGE (n:ModelloIA {id: row.id})
SET n.nome = row.nome;

// Software <- software.csv
LOAD CSV WITH HEADERS FROM 'file:///software.csv' AS row
MERGE (n:Software {id: row.id})
SET n.nome = row.nome;

// CategoriaOrganizzativa <- categorie_organizzative.csv
LOAD CSV WITH HEADERS FROM 'file:///categorie_organizzative.csv' AS row
MERGE (n:CategoriaOrganizzativa {id: row.id})
SET n.nome = row.nome;

// TecnicaIA <- tecniche_ia.csv
LOAD CSV WITH HEADERS FROM 'file:///tecniche_ia.csv' AS row
MERGE (n:TecnicaIA {id: row.id})
SET n.nome = row.nome;

// Fornitore <- fornitori.csv
LOAD CSV WITH HEADERS FROM 'file:///fornitori.csv' AS row
MERGE (n:Fornitore {id: row.id})
SET n.nome = row.nome;

// FunzioneOrganizzativa <- funzioni_organizzative.csv
LOAD CSV WITH HEADERS FROM 'file:///funzioni_organizzative.csv' AS row
MERGE (n:FunzioneOrganizzativa {id: row.id})
SET n.nome = row.nome;

// SettoreMissione <- settori_missione.csv
LOAD CSV WITH HEADERS FROM 'file:///settori_missione.csv' AS row
MERGE (n:SettoreMissione {id: row.id})
SET n.nome = row.nome;

// Beneficio <- benefici.csv
LOAD CSV WITH HEADERS FROM 'file:///benefici.csv' AS row
MERGE (n:Beneficio {id: row.id})
SET n.nome = row.nome;

// Criticita <- criticita.csv
LOAD CSV WITH HEADERS FROM 'file:///criticita.csv' AS row
MERGE (n:Criticita {id: row.id})
SET n.nome = row.nome;

// Programma <- programmi.csv
LOAD CSV WITH HEADERS FROM 'file:///programmi.csv' AS row
MERGE (n:Programma {id: row.id})
SET n.nome = row.nome;

// Fonte <- fonti.csv
LOAD CSV WITH HEADERS FROM 'file:///fonti.csv' AS row
MERGE (n:Fonte {id: row.id})
SET n.nome = row.nome;

// TipoBeneficiario <- tipi_beneficiario.csv (NUOVO 2026-08-24)
LOAD CSV WITH HEADERS FROM 'file:///tipi_beneficiario.csv' AS row
MERGE (n:TipoBeneficiario {id: row.id})
SET n.nome = row.nome;

// TipoSupervisioneUmana <- tipi_supervisione_umana.csv (NUOVO 2026-08-24, v4)
LOAD CSV WITH HEADERS FROM 'file:///tipi_supervisione_umana.csv' AS row
MERGE (n:TipoSupervisioneUmana {id: row.id})
SET n.nome = row.nome;

// Collaboratore <- collaboratori.csv (NUOVO 2026-08-24, v4)
LOAD CSV WITH HEADERS FROM 'file:///collaboratori.csv' AS row
MERGE (n:Collaboratore {id: row.id})
SET n.nome = row.nome;

// --------------------- 3) CARICAMENTO RELAZIONI ---------------------
// Un'unica relationships.csv, filtrata per Relationship_Type (nessun APOC richiesto)
// Le colonne del CSV restano in inglese (Implementation_ID/Confidence/Evidence_Field/
// Evidence_Value: file interno di elaborazione, mai visualizzato in Neo4j); le
// PROPRIETA' scritte sulle relazioni con SET sono in italiano.

// Organizzazione -[:HA_IMPLEMENTAZIONE]-> Implementazione
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'HA_IMPLEMENTAZIONE'
MATCH (s:Organizzazione {id: row.Source_Node_ID})
MATCH (t:Implementazione {id: row.Target_Node_ID})
MERGE (s)-[r:HA_IMPLEMENTAZIONE]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Organizzazione -[:HA_SEDE_IN]-> Paese
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'HA_SEDE_IN'
MATCH (s:Organizzazione {id: row.Source_Node_ID})
MATCH (t:Paese {id: row.Target_Node_ID})
MERGE (s)-[r:HA_SEDE_IN]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:IMPLEMENTATO_IN]-> Paese
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'IMPLEMENTATO_IN'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:Paese {id: row.Target_Node_ID})
MERGE (s)-[r:IMPLEMENTATO_IN]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Organizzazione -[:HA_TIPO]-> CategoriaOrganizzativa
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'HA_TIPO'
MATCH (s:Organizzazione {id: row.Source_Node_ID})
MATCH (t:CategoriaOrganizzativa {id: row.Target_Node_ID})
MERGE (s)-[r:HA_TIPO]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:USA_MODELLO]-> ModelloIA
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'USA_MODELLO'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:ModelloIA {id: row.Target_Node_ID})
MERGE (s)-[r:USA_MODELLO]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:USA_SOFTWARE]-> Software
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'USA_SOFTWARE'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:Software {id: row.Target_Node_ID})
MERGE (s)-[r:USA_SOFTWARE]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:USA_TECNICA]-> TecnicaIA
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'USA_TECNICA'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:TecnicaIA {id: row.Target_Node_ID})
MERGE (s)-[r:USA_TECNICA]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:USA_FORNITORE]-> Fornitore
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'USA_FORNITORE'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:Fornitore {id: row.Target_Node_ID})
MERGE (s)-[r:USA_FORNITORE]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:HA_FUNZIONE]-> FunzioneOrganizzativa
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'HA_FUNZIONE'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:FunzioneOrganizzativa {id: row.Target_Node_ID})
MERGE (s)-[r:HA_FUNZIONE]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:INDIRIZZA_SETTORE]-> SettoreMissione
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'INDIRIZZA_SETTORE'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:SettoreMissione {id: row.Target_Node_ID})
MERGE (s)-[r:INDIRIZZA_SETTORE]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:RIPORTA_BENEFICIO]-> Beneficio
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'RIPORTA_BENEFICIO'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:Beneficio {id: row.Target_Node_ID})
MERGE (s)-[r:RIPORTA_BENEFICIO]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:RIPORTA_CRITICITA]-> Criticita
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'RIPORTA_CRITICITA'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:Criticita {id: row.Target_Node_ID})
MERGE (s)-[r:RIPORTA_CRITICITA]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:DOCUMENTATO_DA]-> Fonte
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'DOCUMENTATO_DA'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:Fonte {id: row.Target_Node_ID})
MERGE (s)-[r:DOCUMENTATO_DA]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:FA_PARTE_DI]-> Programma
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'FA_PARTE_DI'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:Programma {id: row.Target_Node_ID})
MERGE (s)-[r:FA_PARTE_DI]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:HA_BENEFICIARIO]-> TipoBeneficiario (NUOVO 2026-08-24)
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'HA_BENEFICIARIO'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:TipoBeneficiario {id: row.Target_Node_ID})
MERGE (s)-[r:HA_BENEFICIARIO]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:COINVOLGE_UMANO]-> TipoSupervisioneUmana (NUOVO 2026-08-24, v4)
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'COINVOLGE_UMANO'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:TipoSupervisioneUmana {id: row.Target_Node_ID})
MERGE (s)-[r:COINVOLGE_UMANO]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// Implementazione -[:REALIZZATO_CON]-> Collaboratore (NUOVO 2026-08-24, v4)
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
WITH row WHERE row.Relationship_Type = 'REALIZZATO_CON'
MATCH (s:Implementazione {id: row.Source_Node_ID})
MATCH (t:Collaboratore {id: row.Target_Node_ID})
MERGE (s)-[r:REALIZZATO_CON]->(t)
SET r.ID_Caso = row.Implementation_ID, r.Affidabilita = row.Confidence, r.Campo_evidenza = row.Evidence_Field, r.Valore_evidenza = row.Evidence_Value;

// --------------------- 4) VERIFICA RAPIDA POST-IMPORT ---------------------
// MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY n DESC;
// MATCH ()-[r]->() RETURN type(r) AS relazione, count(*) AS n ORDER BY n DESC;
// Attesi: 1.275 nodi totali, 6.083 relazioni dopo deduplica MERGE (6.098 righe generate, 15 duplicate su HA_SEDE_IN).
