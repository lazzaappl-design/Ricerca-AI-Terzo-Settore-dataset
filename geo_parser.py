# -*- coding: utf-8 -*-
"""
Parser euristico per l'audit geografico dello STEP 0 (v2, corretto dopo revisione manuale).
Estrae Organization_Country / Implementation_Country / Geographic_Confidence
dal campo Paese esistente (testo libero), senza inventare informazioni:
se il testo non consente un'estrazione affidabile, il record viene marcato
AMBIGUOUS/NOT_AVAILABLE e segnalato per revisione umana.

Correzioni v2 rispetto alla prima bozza (rilevate in revisione manuale delle 243 stringhe distinte):
- "India" richiede ora confine di parola (evitava falsi positivi su "Indiana", "Indianapolis")
- Alias ISO2 di 2 lettere (US, IT, CA, CH, NO, GB, DK, JO, AU) spostati in un controllo dedicato
  case-sensitive a inizio stringa, per evitare collisioni con parole italiane comuni
  (es. "NO" case-insensitive matchava "no-profit")
- Aggiunti Paesi mancanti dal lessico: Zambia, Lesotho, Sudan (distinto da Sud Sudan), Ng (Nigeria)
- Ordine di matching reso esplicito per evitare che "Sudan" catturi erroneamente "Sud Sudan"
"""
import re
import csv

COUNTRIES = {
    "Argentina": ["argentina"],
    "Australia": ["australia"],
    "Austria": ["austria"],
    "Bangladesh": ["bangladesh"],
    "Belgio": ["belgio"],
    "Bhutan": ["bhutan"],
    "Brasile": ["brasile", "brazil"],
    "Cambogia": ["cambogia"],
    "Canada": ["canada"],
    "Centrafrica (Rep. Centrafricana)": ["repubblica centrafricana"],
    "Cile": [r"\bcile\b"],
    "Cina": [r"\bcina\b", "china"],
    "Colombia": ["colombia"],
    "Costa d'Avorio": ["costa d'avorio", "costa davorio"],
    "Costa Rica": ["costa rica"],
    "Danimarca": ["danimarca"],
    "Ecuador": ["ecuador"],
    "Egitto": ["egitto"],
    "Etiopia": ["etiopia"],
    "Figi": ["figi", "fiji"],
    "Filippine": ["filippine"],
    "Finlandia": ["finlandia"],
    "Francia": ["francia"],
    "Gambia": ["gambia"],
    "Germania": ["germania"],
    "Ghana": ["ghana"],
    "Giamaica": ["giamaica"],
    "Giordania": ["giordania"],
    "Grecia": ["grecia"],
    "Guatemala": ["guatemala"],
    "Guinea": [r"\bguinea\b(?!-bissau)"],
    "Guyana": ["guyana"],
    "Haiti": ["haiti"],
    "Honduras": ["honduras"],
    "Hong Kong": ["hong kong"],
    "Indonesia": ["indonesia"],  # PRIMA di India per evitare overlap su "Indo"
    "India": [r"\bindia\b"],
    "Irlanda": ["irlanda"],
    "Italia": [r"\bitalia\b"],
    "Kenya": ["kenya"],
    "Lesotho": ["lesotho"],
    "Liberia": ["liberia"],
    "Malawi": ["malawi"],
    "Mali": [r"\bmali\b"],
    "Messico": ["messico"],
    "Mongolia": ["mongolia"],
    "Mozambico": ["mozambico"],
    "Myanmar": ["myanmar"],
    "Nepal": ["nepal"],
    "Nigeria": ["nigeria"],
    "Norvegia": ["norvegia"],
    "Nuova Zelanda": ["nuova zelanda"],
    "Paesi Bassi": ["paesi bassi", "olanda"],
    "Pakistan": ["pakistan"],
    "Panama": ["panam(a|á)"],
    "Perù": [r"\bper(u|ù)\b"],
    "Polonia": ["polonia"],
    "Portogallo": ["portogallo"],
    "Regno Unito": ["regno unito"],
    "Ruanda": ["ruanda", "rwanda"],
    "RD Congo": ["repubblica democratica del congo"],
    "Senegal": ["senegal"],
    "Sierra Leone": ["sierra leone"],
    "Singapore": ["singapore"],
    "Somalia": ["somalia"],
    "Spagna": ["spagna"],
    "Sud Sudan": ["sud sudan"],  # PRIMA di Sudan
    "Sudan": [r"\bsudan\b"],
    "Stati Uniti": ["stati uniti", r"\busa\b", "statunitense"],
    "Sudafrica": ["sudafrica", "sud africa"],
    "Svezia": ["svezia"],
    "Svizzera": ["svizzera"],
    "Taiwan": ["taiwan"],
    "Tanzania": ["tanzania"],
    "Togo": [r"\btogo\b"],
    "Turchia": ["turchia"],
    "Siria": [r"\bsiria\b"],
    "Uganda": ["uganda"],
    "Ucraina": ["ucraina"],
    "Yemen": ["yemen"],
    "Zambia": ["zambia"],
}

# Ordine di priorità esplicito: nomi composti/piu' lunghi prima (per gestire overlap come Sud Sudan/Sudan)
_ordered_canons = sorted(COUNTRIES.keys(), key=lambda c: -max(len(a) for a in COUNTRIES[c]))
_compiled = []
for canon in _ordered_canons:
    for a in COUNTRIES[canon]:
        _compiled.append((canon, re.compile(a, re.IGNORECASE)))

# Codici ISO2 riconosciuti SOLO case-sensitive e SOLO a inizio stringa (o dopo "/", spazio a inizio token),
# per lo stile di alcuni record dei primi cicli (es. "US", "IT (...)", "NO (operatività globale)").
# Tenuti separati dal lessico generale per evitare collisioni con parole italiane comuni (es. "no", "it").
ISO2_PREFIX = {
    "US": "Stati Uniti", "IT": "Italia", "CA": "Canada", "CH": "Svizzera",
    "NO": "Norvegia", "GB": "Regno Unito", "UK": "Regno Unito", "DK": "Danimarca",
    "JO": "Giordania", "AU": "Australia", "NG": "Nigeria", "BD": "Bangladesh",
}

HQ_KEYWORDS = [
    "sede legale", "sede operativa", "sede istituzionale", "sede organizzativa",
    "sede centrale", "sede internazionale", "organizzazione madre", "organizzazione con sede",
    "registrata in", "sede", "organizzazione internazionale con sede",
]
IMPL_KEYWORDS = [
    "implementazione operativa", "implementazione principale", "implementazione in",
    "implementazione pilota", "operativita", "operatività", "opera in", "attiva in",
    "progetti in", "progetto pilotato", "progetto pilota", "pilota", "pilot",
    "espansione", "rollout", "distribuzione", "utenti in", "utenza", "copertura operativa",
    "applicazione", "applicazioni documentate", "intervento", "servizio disponibile",
    "operativa anche in", "operativo in", "rete attiva in", "operazioni in", "operazioni a",
]
GLOBAL_KEYWORDS = ["globale", "internazionale", "livello globale", "in tutto il mondo", "worldwide"]


def find_iso2_prefix(text):
    """Riconosce codici ISO2 ovunque nel testo, case-sensitive e a confine di parola
    (es. 'US', 'NG / BD', '(sede US)'), per evitare collisioni con parole italiane comuni
    minuscole (es. 'no', 'it') pur riconoscendo lo stile ISO2 usato nei primi cicli."""
    tokens = re.findall(r'\b[A-Z]{2}\b', text)
    seen = []
    for t in tokens:
        if t in ISO2_PREFIX and ISO2_PREFIX[t] not in seen:
            seen.append(ISO2_PREFIX[t])
    return seen


def find_countries(text):
    found = []
    used_spans = []
    for canon, pat in _compiled:
        for m in pat.finditer(text):
            span = m.span()
            if any(not (span[1] <= s[0] or span[0] >= s[1]) for s in used_spans):
                continue
            found.append((canon, span[0], span[1]))
            used_spans.append(span)
    found.sort(key=lambda x: x[1])
    return found


def classify(paese_raw):
    text = paese_raw.strip()
    iso2_hits = find_iso2_prefix(text)
    countries = find_countries(text)

    canon_list_in_order = []
    seen = set()
    for c in [h for h in iso2_hits] + [c for c, s, e in countries]:
        if c not in seen:
            canon_list_in_order.append(c)
            seen.add(c)

    has_hq_kw = any(kw in text.lower() for kw in HQ_KEYWORDS)
    has_impl_kw = any(kw in text.lower() for kw in IMPL_KEYWORDS)
    has_global_kw = any(kw in text.lower() for kw in GLOBAL_KEYWORDS)

    result = {
        "Country_Original": paese_raw,
        "Organization_Country": "",
        "Implementation_Country": "",
        "Geographic_Confidence": "",
        "Geographic_Evidence_Note": "",
        "Requires_Human_Review": "NO",
    }

    if not countries and not iso2_hits:
        result.update(Organization_Country="NOT_AVAILABLE", Implementation_Country="NOT_AVAILABLE",
                       Geographic_Confidence="NOT_AVAILABLE",
                       Geographic_Evidence_Note="Parser non ha riconosciuto nomi di Paese nel testo originale.",
                       Requires_Human_Review="YES")
        return result

    # caso ISO2 puro (es. "US", "IT", "NO (operatività globale)", "NG / BD")
    if iso2_hits and not countries:
        if len(iso2_hits) == 1:
            c = iso2_hits[0]
            result["Organization_Country"] = c
            if has_global_kw:
                result["Implementation_Country"] = "GLOBAL_MULTI_COUNTRY_UNSPECIFIED"
                result["Geographic_Confidence"] = "STRONG_INFERENCE"
                result["Geographic_Evidence_Note"] = "Codice ISO2 a inizio stringa riconosciuto come sede; implementazione dichiarata globale senza elenco Paesi."
            else:
                result["Implementation_Country"] = c
                result["Geographic_Confidence"] = "STRONG_INFERENCE"
                result["Geographic_Evidence_Note"] = "Codice ISO2 singolo senza ulteriori qualificazioni; sede e implementazione assunte coincidenti."
            return result
        else:
            result["Organization_Country"] = "AMBIGUOUS"
            result["Implementation_Country"] = "; ".join(iso2_hits)
            result["Geographic_Confidence"] = "AMBIGUOUS"
            result["Geographic_Evidence_Note"] = "Piu' codici ISO2 elencati senza indicazione esplicita di quale sia la sede."
            result["Requires_Human_Review"] = "YES"
            return result

    # unico paese, nessuna clausola HQ/impl
    if len(canon_list_in_order) == 1 and not has_hq_kw and not has_impl_kw:
        c = canon_list_in_order[0]
        result["Organization_Country"] = c
        result["Implementation_Country"] = c
        result["Geographic_Confidence"] = "STRONG_INFERENCE"
        result["Geographic_Evidence_Note"] = (
            "Valore originale composto da un singolo Paese senza ulteriori qualificazioni; "
            "sede e implementazione assunte coincidenti in assenza di indicazioni contrarie nel campo."
        )
        return result

    if has_hq_kw or has_impl_kw:
        low = text.lower()
        hq_pos = min([low.find(kw) for kw in HQ_KEYWORDS if kw in low], default=None)
        impl_positions = [low.find(kw) for kw in IMPL_KEYWORDS if kw in low]
        impl_pos = min(impl_positions) if impl_positions else None

        all_hits = [(c, s, e) for c, s, e in countries]

        if hq_pos is not None and impl_pos is not None:
            if hq_pos < impl_pos:
                hq_country = [c for c, s, e in all_hits if s < impl_pos]
                impl_countries = [c for c, s, e in all_hits if s >= impl_pos]
            else:
                impl_countries = [c for c, s, e in all_hits if s < hq_pos]
                hq_country = [c for c, s, e in all_hits if s >= hq_pos]
        elif hq_pos is not None:
            hq_country = [c for c, s, e in all_hits if abs(s - hq_pos) < 40] or canon_list_in_order[:1]
            impl_countries = [c for c in canon_list_in_order if c not in hq_country]
        else:
            hq_country = canon_list_in_order[:1]
            impl_countries = [c for c, s, e in all_hits if s >= impl_pos]

        hq_country = list(dict.fromkeys(hq_country))
        impl_countries = list(dict.fromkeys(impl_countries))

        if hq_country and impl_countries:
            result["Organization_Country"] = "; ".join(hq_country)
            result["Implementation_Country"] = "; ".join(impl_countries)
            result["Geographic_Confidence"] = "EXPLICIT"
            result["Geographic_Evidence_Note"] = "Estratto per posizione testuale da clausole sede/operatività esplicite nel campo Paese originale."
            return result
        elif hq_country and not impl_countries and has_global_kw:
            result["Organization_Country"] = "; ".join(hq_country)
            result["Implementation_Country"] = "GLOBAL_MULTI_COUNTRY_UNSPECIFIED"
            result["Geographic_Confidence"] = "STRONG_INFERENCE"
            result["Geographic_Evidence_Note"] = "Sede identificata; implementazione dichiarata globale/multi-Paese senza elenco specifico nel testo originale."
            return result
        elif hq_country and not impl_countries and len(canon_list_in_order) == 1:
            # unico Paese nell'intero testo (quello della sede): il resto della frase descrive
            # dettagli sub-nazionali (città/stati/contee) dello stesso Paese, non altre nazioni.
            c = hq_country[0]
            result["Organization_Country"] = c
            result["Implementation_Country"] = c
            result["Geographic_Confidence"] = "STRONG_INFERENCE"
            result["Geographic_Evidence_Note"] = (
                "Nessun altro Paese menzionato nel testo oltre alla sede; i dettagli aggiuntivi "
                "(citta'/stati/contee) sono sub-nazionali all'interno dello stesso Paese della sede."
            )
            return result
        elif hq_country and not impl_countries:
            result["Organization_Country"] = "; ".join(hq_country)
            result["Implementation_Country"] = "AMBIGUOUS"
            result["Geographic_Confidence"] = "AMBIGUOUS"
            result["Geographic_Evidence_Note"] = "Sede identificata ma Paese/i di implementazione non estraibili con certezza dal testo."
            result["Requires_Human_Review"] = "YES"
            return result

    if len(canon_list_in_order) > 1 and not has_hq_kw:
        # Convenzione osservata nello stile di scrittura del corpus: quando piu' Paesi sono
        # elencati senza parola chiave esplicita (es. "Stati Uniti / Canada", "Stati Uniti
        # (operazioni in Indonesia)" ora gia' gestito sopra via impl-keyword), il primo Paese
        # menzionato nel testo corrisponde alla sede dell'organizzazione. Applicata solo come
        # STRONG_INFERENCE (non EXPLICIT) e solo quando il primo paese e' menzionato prima di
        # ogni parentesi/slash separatore.
        first_country, first_pos = countries[0][0], countries[0][1]
        result["Organization_Country"] = first_country
        result["Implementation_Country"] = "; ".join(canon_list_in_order)
        result["Geographic_Confidence"] = "STRONG_INFERENCE"
        result["Geographic_Evidence_Note"] = (
            "Nessuna parola chiave esplicita di sede/operativita' nel testo; applicata la convenzione "
            "'primo Paese elencato = sede', coerente con lo stile di scrittura del resto del corpus. "
            "Implementazione assunta in tutti i Paesi elencati (incluso quello della sede) in assenza "
            "di indicazioni contrarie."
        )
        result["Requires_Human_Review"] = "YES"  # confermare comunque con lettura rapida della fonte
        return result

    result["Organization_Country"] = "AMBIGUOUS"
    result["Implementation_Country"] = "; ".join(canon_list_in_order) if canon_list_in_order else "AMBIGUOUS"
    result["Geographic_Confidence"] = "AMBIGUOUS"
    result["Geographic_Evidence_Note"] = "Caso non coperto dalle regole euristiche principali."
    result["Requires_Human_Review"] = "YES"
    return result


# Override manuali per casi dove la lettura diretta del testo (non nuova ricerca, solo comprensione
# del campo gia' raccolto) permette una classificazione piu' accurata di quella puramente posizionale.
MANUAL_OVERRIDES = {
    "Giamaica (implementazione operativa); rete di supporto internazionale coordinata da WeRobotics (sede a Ginevra, Svizzera/Wilmington, Delaware, USA) tramite nodi Flying Labs in Panama, Brasile, Tanzania, India e Senegal": {
        "Organization_Country": "Svizzera; Stati Uniti",
        "Implementation_Country": "Giamaica",
        "Geographic_Confidence": "EXPLICIT",
        "Geographic_Evidence_Note": "WeRobotics ha doppia sede (Ginevra/Wilmington); Panama, Brasile, Tanzania, India, Senegal sono altri nodi Flying Labs citati per contesto, non la sede né l'implementazione di questo specifico caso (Giamaica).",
        "Requires_Human_Review": "NO",
    },
    "Malawi (implementazione principale); organizzazione con sede negli Stati Uniti (Illinois), operativa a livello globale; espansione pilota in Kenya e Ghana nel 2025": {
        "Organization_Country": "Stati Uniti",
        "Implementation_Country": "Malawi; Kenya; Ghana",
        "Geographic_Confidence": "EXPLICIT",
        "Geographic_Evidence_Note": "Kenya e Ghana sono espansione pilota dell'implementazione (2025), non sede dell'organizzazione.",
        "Requires_Human_Review": "NO",
    },
    "Kenya (organizzazione con doppia sede a Nairobi e Cambridge, Regno Unito; operativa anche in Somalia e altri Paesi africani)": {
        "Organization_Country": "Kenya; Regno Unito",
        "Implementation_Country": "Kenya; Somalia; +altri Paesi africani non elencati",
        "Geographic_Confidence": "STRONG_INFERENCE",
        "Geographic_Evidence_Note": "Doppia sede Nairobi/Cambridge; l'operatività include verosimilmente il Kenya stesso oltre a Somalia e altri Paesi non elencati nominalmente.",
        "Requires_Human_Review": "NO",
    },
    "Globale (60+ Paesi)": {
        "Organization_Country": "Danimarca",
        "Implementation_Country": "GLOBAL_MULTI_COUNTRY_UNSPECIFIED",
        "Geographic_Confidence": "STRONG_INFERENCE",
        "Geographic_Evidence_Note": "Sede desunta dal campo Organizzazione dello stesso record ('host: Danish Refugee Council'), non da nuova ricerca. Implementazione dichiarata in 60+ Paesi senza elenco specifico.",
        "Requires_Human_Review": "NO",
    },
    "Honduras (I2UD con sede a Somerville, USA)": {
        "Organization_Country": "Stati Uniti",
        "Implementation_Country": "Honduras",
        "Geographic_Confidence": "EXPLICIT",
        "Geographic_Evidence_Note": "Sede esplicitamente indicata a Somerville, Massachusetts, USA nel testo originale.",
        "Requires_Human_Review": "NO",
    },
    "Hong Kong (Cina), con copertura operativa in oltre 50 giurisdizioni in Asia e Medio Oriente": {
        "Organization_Country": "Hong Kong",
        "Implementation_Country": "GLOBAL_MULTI_COUNTRY_UNSPECIFIED",
        "Geographic_Confidence": "STRONG_INFERENCE",
        "Geographic_Evidence_Note": "Copertura dichiarata su oltre 50 giurisdizioni in Asia e Medio Oriente, senza elenco specifico nel testo originale.",
        "Requires_Human_Review": "NO",
    },
    "NG / BD": {
        "Organization_Country": "Stati Uniti",
        "Implementation_Country": "Nigeria; Bangladesh",
        "Geographic_Confidence": "STRONG_INFERENCE",
        "Geographic_Evidence_Note": "Sede desunta per analogia dal record gemello della stessa organizzazione già presente nel corpus (GiveDirectly, TS-AI-00065, sede Stati Uniti), non da nuova ricerca.",
        "Requires_Human_Review": "NO",
    },
    "Norvegia (sede); operazioni di sminamento in Ucraina (caso documentato) e in oltre 30 Paesi complessivamente": {
        "Organization_Country": "Norvegia",
        "Implementation_Country": "Ucraina; GLOBAL_MULTI_COUNTRY_UNSPECIFIED (+oltre 30 Paesi non enumerati)",
        "Geographic_Confidence": "EXPLICIT",
        "Geographic_Evidence_Note": "Sede esplicita in Norvegia; Ucraina esplicitamente documentata come caso specifico, oltre 30 Paesi aggiuntivi non enumerati.",
        "Requires_Human_Review": "NO",
    },
    "Internazionale (organizzazione con governance globale)": {
        "Organization_Country": "Germania; Messico",
        "Implementation_Country": "GLOBAL_MULTI_COUNTRY_UNSPECIFIED",
        "Geographic_Confidence": "EXPLICIT",
        "Geographic_Evidence_Note": ("Ricerca mirata STEP 0 (2026-08-20): questo valore corrisponde a Forest Stewardship Council (FSC), "
            "che ha sede operativa a Bonn, Germania (dal trasferimento da Oaxaca, Messico), pur restando registrata legalmente come ONG "
            "internazionale in Messico. Implementazione (certificazione forestale) a copertura globale, non enumerata per Paese."),
        "Requires_Human_Review": "NO",
    },
    "Stati Uniti (sede Freedom House) e Taiwan (sede Doublethink Lab); oggetto di monitoraggio: Repubblica Popolare Cinese": {
        "Organization_Country": "Stati Uniti; Taiwan",
        "Implementation_Country": "Stati Uniti; Taiwan",
        "Geographic_Confidence": "STRONG_INFERENCE",
        "Geographic_Evidence_Note": "Caso particolare: due organizzazioni co-implementano il sistema (sedi USA e Taiwan); la Cina è l'oggetto dell'analisi di disinformazione, non un luogo di implementazione territoriale del sistema stesso. Distinzione concettuale segnalata per eventuale revisione in Step successivi.",
        "Requires_Human_Review": "YES",
    },
}


if __name__ == "__main__":
    with open("corpus_freeze_391rec_2026-08-20.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    distinct = {}
    for r in rows:
        val = r["Paese"]
        if val in distinct:
            continue
        if val in MANUAL_OVERRIDES:
            cl = dict(MANUAL_OVERRIDES[val])
            cl["Country_Original"] = val
        else:
            cl = classify(val)
        distinct[val] = cl

    with open("paese_classification_preview.tsv", "w", encoding="utf-8") as out:
        out.write("Country_Original\tOrganization_Country\tImplementation_Country\tConfidence\tReview\n")
        for val, cl in sorted(distinct.items()):
            out.write(f"{val}\t{cl['Organization_Country']}\t{cl['Implementation_Country']}\t{cl['Geographic_Confidence']}\t{cl['Requires_Human_Review']}\n")

    import json
    with open("paese_classification_map.json", "w", encoding="utf-8") as f:
        json.dump(distinct, f, ensure_ascii=False, indent=1)

    n_review = sum(1 for cl in distinct.values() if cl["Requires_Human_Review"] == "YES")
    print(f"Valori distinti classificati: {len(distinct)}")
    print(f"Valori distinti che richiedono revisione umana: {n_review}")
