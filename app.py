import streamlit as st
import pandas as pd
import plotly.express as px
from collections import defaultdict

st.set_page_config(page_title="KI-Reifegrad Mittelstand", layout="wide")

# -------------------------
# Fragenkatalog
# -------------------------

QUESTIONS = [
    # Unternehmensweit – Strategie
    {
        "id": "S1",
        "scope": "Unternehmensweit",
        "dimension": "Strategie",
        "role": "M",
        "text": "Es existiert eine schriftlich fixierte KI-Strategie, die mit der Unternehmensstrategie verknüpft ist."
    },
    {
        "id": "S2",
        "scope": "Unternehmensweit",
        "dimension": "Strategie",
        "role": "M",
        "text": "Es gibt eine priorisierte KI-Use-Case-Roadmap mit klaren Zielen (Qualität, Kosten, Zeit, Risiko)."
    },
    {
        "id": "S3",
        "scope": "Unternehmensweit",
        "dimension": "Strategie",
        "role": "M/F",
        "text": "Entscheidungen über KI-Investitionen folgen einem definierten Kriterienkatalog (Business Case, Risiko, Datenverfügbarkeit)."
    },
    {
        "id": "S4",
        "scope": "Unternehmensweit",
        "dimension": "Strategie",
        "role": "F",
        "text": "Fachbereiche (Entwicklung, Einkauf, Service) sind systematisch in die Identifikation und Priorisierung von KI-Use-Cases eingebunden."
    },
    {
        "id": "S5",
        "scope": "Unternehmensweit",
        "dimension": "Strategie",
        "role": "IT",
        "text": "KI-Strategie ist mit der IT-/Digitalisierungsstrategie abgestimmt (Architektur, Infrastruktur, Security)."
    },

    # Unternehmensweit – Kompetenz & Kultur
    {
        "id": "K1",
        "scope": "Unternehmensweit",
        "dimension": "Kompetenz & Kultur",
        "role": "M",
        "text": "Es gibt ein Qualifizierungsprogramm zu KI für Führungskräfte und Schlüsselfunktionen."
    },
    {
        "id": "K2",
        "scope": "Unternehmensweit",
        "dimension": "Kompetenz & Kultur",
        "role": "F",
        "text": "In den Fachbereichen existieren KI-Champions / Multiplikatoren als Ansprechpartner."
    },
    {
        "id": "K3",
        "scope": "Unternehmensweit",
        "dimension": "Kompetenz & Kultur",
        "role": "F",
        "text": "Mitarbeitende kennen konkrete KI-Anwendungsfälle im eigenen Bereich und verstehen deren Nutzen."
    },
    {
        "id": "K4",
        "scope": "Unternehmensweit",
        "dimension": "Kompetenz & Kultur",
        "role": "IT",
        "text": "Interne oder externe Experten für Datenanalyse, Data Engineering und MLOps stehen zur Verfügung."
    },
    {
        "id": "K5",
        "scope": "Unternehmensweit",
        "dimension": "Kompetenz & Kultur",
        "role": "M/F",
        "text": "Erfahrungen aus KI-Projekten werden strukturiert geteilt (Communities, Brown-Bag-Sessions, Lessons Learned)."
    },

    # Unternehmensweit – Governance & Daten
    {
        "id": "G1",
        "scope": "Unternehmensweit",
        "dimension": "Governance & Daten",
        "role": "M",
        "text": "Rollen und Verantwortlichkeiten für KI-Governance sind definiert (z.B. KI-Board, Data Owner, Data Steward)."
    },
    {
        "id": "G2",
        "scope": "Unternehmensweit",
        "dimension": "Governance & Daten",
        "role": "M/IT",
        "text": "Es existieren Richtlinien für den Einsatz von KI (Datenschutz, IT-Sicherheit, Compliance, ethische Leitlinien)."
    },
    {
        "id": "G3",
        "scope": "Unternehmensweit",
        "dimension": "Governance & Daten",
        "role": "IT",
        "text": "Datenmanagement ist strukturiert (Datenkatalog, Stammdatenkonzepte, Datenqualitätsregeln)."
    },
    {
        "id": "G4",
        "scope": "Unternehmensweit",
        "dimension": "Governance & Daten",
        "role": "IT/F",
        "text": "Daten aus Entwicklung, Einkauf und Service sind identifizierbar, zugreifbar und technisch nutzbar."
    },
    {
        "id": "G5",
        "scope": "Unternehmensweit",
        "dimension": "Governance & Daten",
        "role": "M/F",
        "text": "Für KI-Modelle gibt es Freigabeprozesse, Monitoring und Regeln zur Nachvollziehbarkeit von Entscheidungen."
    },

    # Unternehmensweit – Technologie & Anwendungen
    {
        "id": "T1",
        "scope": "Unternehmensweit",
        "dimension": "Technologie & Anwendungen",
        "role": "IT",
        "text": "Es existiert eine standardisierte Plattform-/Toolchain für Datenanalyse und KI."
    },
    {
        "id": "T2",
        "scope": "Unternehmensweit",
        "dimension": "Technologie & Anwendungen",
        "role": "IT/F",
        "text": "Fachsysteme (PLM, ERP, MES, Service-Tools) sind mit der Daten-/KI-Plattform integriert."
    },
    {
        "id": "T3",
        "scope": "Unternehmensweit",
        "dimension": "Technologie & Anwendungen",
        "role": "F",
        "text": "Fachbereiche nutzen bereits produktive KI-Anwendungen im Tagesgeschäft."
    },
    {
        "id": "T4",
        "scope": "Unternehmensweit",
        "dimension": "Technologie & Anwendungen",
        "role": "M",
        "text": "Technische KI-Innovationen werden systematisch gescreent und bewertet (Pilotierung, PoCs)."
    },
    {
        "id": "T5",
        "scope": "Unternehmensweit",
        "dimension": "Technologie & Anwendungen",
        "role": "IT",
        "text": "Betrieb und Support von KI-Anwendungen sind organisatorisch geregelt."
    },

    # Entwicklung – Management
    {
        "id": "E_M1",
        "scope": "Entwicklung",
        "dimension": "Management",
        "role": "M",
        "text": "Für die Produktentwicklung existieren klar definierte KI-Zielbilder (z.B. Testreduktion, schnellere Variantenbewertung)."
    },
    {
        "id": "E_M2",
        "scope": "Entwicklung",
        "dimension": "Management",
        "role": "M",
        "text": "KPIs zum KI-Nutzen in der Entwicklung werden verwendet (Testumfang, Durchlaufzeiten, Fehlerquote)."
    },
    {
        "id": "E_M3",
        "scope": "Entwicklung",
        "dimension": "Management",
        "role": "M",
        "text": "Es gibt ein Portfolio priorisierter KI-Use-Cases entlang des V-Modells."
    },

    # Entwicklung – Fachbereich
    {
        "id": "E_F1",
        "scope": "Entwicklung",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Konstruktions-, Versuch-, Feld- und Qualitätsdaten sind für Analysen gemeinsam nutzbar."
    },
    {
        "id": "E_F2",
        "scope": "Entwicklung",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "DoE, Optimierungsmethoden und KI-Modelle werden in der Auslegung systematisch eingesetzt."
    },
    {
        "id": "E_F3",
        "scope": "Entwicklung",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Testlasten und Testprogramme werden datenbasiert optimiert (Versuchspläne, Testfallreduktion, ML-gestützte Auswahl)."
    },
    {
        "id": "E_F4",
        "scope": "Entwicklung",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Anforderungsmanagement und Systems Engineering nutzen KI-Unterstützung (Analyse von Spezifikationen, Traceability)."
    },
    {
        "id": "E_F5",
        "scope": "Entwicklung",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Lessons Learned aus Projekten sind strukturiert erfasst und werden mittels KI ausgewertet."
    },

    # Entwicklung – IT
    {
        "id": "E_IT1",
        "scope": "Entwicklung",
        "dimension": "IT",
        "role": "IT",
        "text": "Entwicklungswerkzeuge (PLM, ALM, Testmanagement, Simulation) sind an eine zentrale Daten-/KI-Plattform angebunden."
    },
    {
        "id": "E_IT2",
        "scope": "Entwicklung",
        "dimension": "IT",
        "role": "IT",
        "text": "Es gibt standardisierte Datenpipelines für Entwicklungsdaten inkl. Versionierung von Daten und Modellen."
    },
    {
        "id": "E_IT3",
        "scope": "Entwicklung",
        "dimension": "IT",
        "role": "IT",
        "text": "KI-Modelle für Entwicklung können automatisiert deployt und betrieben werden."
    },

    # Einkauf – Management
    {
        "id": "P_M1",
        "scope": "Einkauf",
        "dimension": "Management",
        "role": "M",
        "text": "Für den Einkauf existieren strategische Ziele für den Einsatz von KI (Einsparpotenziale, Risikoreduktion)."
    },
    {
        "id": "P_M2",
        "scope": "Einkauf",
        "dimension": "Management",
        "role": "M",
        "text": "Es gibt Kennzahlen zur Bewertung des KI-Beitrags im Einkauf (Savings, Lieferperformance, Risikoindex)."
    },

    # Einkauf – Fachbereich
    {
        "id": "P_F1",
        "scope": "Einkauf",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Lieferantendaten und Materialstammdaten sind konsistent und zentral verfügbar."
    },
    {
        "id": "P_F2",
        "scope": "Einkauf",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Preisentwicklungen und Kostenstrukturen werden datengetrieben analysiert, inkl. externer Marktdaten."
    },
    {
        "id": "P_F3",
        "scope": "Einkauf",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "KI-gestützte Bewertungen unterstützen die Lieferantenauswahl und -segmentierung."
    },
    {
        "id": "P_F4",
        "scope": "Einkauf",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Bestellmengen und Dispositionsparameter werden auf Basis datenbasierter Prognosen optimiert."
    },
    {
        "id": "P_F5",
        "scope": "Einkauf",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Abweichungen (Lieferverzug, Qualitätsmängel) werden analytisch ausgewertet."
    },

    # Einkauf – IT
    {
        "id": "P_IT1",
        "scope": "Einkauf",
        "dimension": "IT",
        "role": "IT",
        "text": "ERP-, SRM- und Logistiksysteme sind in eine Datenplattform integriert."
    },
    {
        "id": "P_IT2",
        "scope": "Einkauf",
        "dimension": "IT",
        "role": "IT",
        "text": "Externe Datenquellen (Markt-/Risikodaten) können technisch eingebunden werden."
    },
    {
        "id": "P_IT3",
        "scope": "Einkauf",
        "dimension": "IT",
        "role": "IT",
        "text": "KI-Services (Prognosen, Scoring) können in operative Einkäufertätigkeiten integriert werden."
    },

    # Service – Management
    {
        "id": "Srv_M1",
        "scope": "Service",
        "dimension": "Management",
        "role": "M",
        "text": "Für Service und After-Sales existieren klare Zielbilder für den KI-Einsatz (Predictive Maintenance, Remote Diagnose)."
    },
    {
        "id": "Srv_M2",
        "scope": "Service",
        "dimension": "Management",
        "role": "M",
        "text": "Servicekennzahlen (First-Fix-Rate, Stillstandszeiten, Kundenzufriedenheit) werden mit Blick auf KI-Einfluss ausgewertet."
    },

    # Service – Fachbereich
    {
        "id": "Srv_F1",
        "scope": "Service",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Servicefälle, Fehlermeldungen, Reparaturberichte und Teiletausch sind strukturiert erfasst und auswertbar."
    },
    {
        "id": "Srv_F2",
        "scope": "Service",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Es existieren Analyse- oder KI-Anwendungen zur Mustererkennung in Felddaten."
    },
    {
        "id": "Srv_F3",
        "scope": "Service",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Servicetechniker greifen auf eine zentrale Wissensbasis mit KI-Unterstützung bei der Suche zu."
    },
    {
        "id": "Srv_F4",
        "scope": "Service",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Für ausgewählte Produkte gibt es datenbasierte Konzepte zur vorausschauenden Wartung."
    },
    {
        "id": "Srv_F5",
        "scope": "Service",
        "dimension": "Fachbereich",
        "role": "F",
        "text": "Kundenschnittstellen nutzen KI (Routing, Vorqualifizierung von Tickets, FAQ-Automatisierung)."
    },

    # Service – IT
    {
        "id": "Srv_IT1",
        "scope": "Service",
        "dimension": "IT",
        "role": "IT",
        "text": "Feld- und Servicedaten sind technisch zusammenführbar und auf einer Datenplattform verfügbar."
    },
    {
        "id": "Srv_IT2",
        "scope": "Service",
        "dimension": "IT",
        "role": "IT",
        "text": "Es gibt Mechanismen zum sicheren Zugriff auf Maschinendaten beim Kunden."
    },
    {
        "id": "Srv_IT3",
        "scope": "Service",
        "dimension": "IT",
        "role": "IT",
        "text": "KI-Modelle für Serviceprozesse können in die Serviceprozesse integriert werden."
    },
]

# -------------------------
# Skala 0–5 (Texte)
# -------------------------

SCALE_DEFS = {
    0: {
        "kurz": "nicht vorhanden",
        "detail": "Keinerlei Struktur, Zuständigkeit oder Aktivitäten im KI-Kontext."
    },
    1: {
        "kurz": "sehr rudimentär",
        "detail": "Einzelne, personengeprägte Aktivitäten ohne Struktur, ohne stabile Datenbasis, ohne klare Ziele."
    },
    2: {
        "kurz": "grundlegend vorhanden",
        "detail": "Erste Verantwortlichkeiten und Pilotprozesse, nutzbare Datenquellen, Erfolgsmessung punktuell vorhanden."
    },
    3: {
        "kurz": "etabliert in Teilbereichen",
        "detail": "Klare Rollen und Prozesse, wiederverwendbare Daten- und Tool-Basis, messbare Ergebnisse in mehreren Bereichen."
    },
    4: {
        "kurz": "weitgehend integriert",
        "detail": "KI ist in Kernprozesse und Systeme eingebettet, unternehmensweit verfügbar und wird aktiv über Business-KPIs gesteuert."
    },
    5: {
        "kurz": "voll etabliert",
        "detail": "KI ist selbstverständlicher Bestandteil von Strategie, Prozessen und Systemen mit nachweisbarem, dauerhaftem Business-Impact."
    },
}

# -------------------------
# Hilfsfunktionen
# -------------------------

def role_matches(filter_role, q_role):
    if filter_role == "Alle":
        return True
    if filter_role == "Management":
        key = "M"
    elif filter_role == "Fachbereich":
        key = "F"
    elif filter_role == "IT":
        key = "IT"
    else:
        return True
    return key in q_role

def compute_dimension_scores(scope, answers):
    scores = defaultdict(list)
    for q in QUESTIONS:
        if q["scope"] == scope:
            qid = q["id"]
            if qid in answers:
                scores[q["dimension"]].append(answers[qid])
    dim_scores = {}
    for dim, vals in scores.items():
        if len(vals) > 0:
            dim_scores[dim] = sum(vals) / len(vals)
    return dim_scores

def compute_overall_score(dim_scores, dim_weights):
    num = 0.0
    den = 0.0
    for dim, score in dim_scores.items():
        w = dim_weights.get(dim, 1.0)
        num += score * w
        den += w
    if den == 0:
        return None
    return num / den

def plot_radar(dim_scores, title):
    if not dim_scores:
        st.write("Keine Daten für die Spidergraphik verfügbar.")
        return
    df = pd.DataFrame({
        "Dimension": list(dim_scores.keys()),
        "Score": list(dim_scores.values())
    })
    fig = px.line_polar(
        df,
        r="Score",
        theta="Dimension",
        line_close=True,
        range_r=[0, 5]
    )
    fig.update_traces(fill="toself")
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Hilfsfunktionen Kennzahlen
# -------------------------

def score_percent(value, bands):
    if value is None:
        return 0
    v = max(0.0, float(value))
    if v <= bands[0]:
        return 0
    elif v <= bands[1]:
        return 1
    elif v <= bands[2]:
        return 2
    elif v <= bands[3]:
        return 3
    elif v <= bands[4]:
        return 4
    else:
        return 5

def score_count(value, bands):
    if value is None:
        return 0
    v = max(0.0, float(value))
    if v <= bands[0]:
        return 0
    elif v <= bands[1]:
        return 1
    elif v <= bands[2]:
        return 2
    elif v <= bands[3]:
        return 3
    elif v <= bands[4]:
        return 4
    else:
        return 5

def score_select(level, mapping):
    return mapping.get(level, 0)

# -------------------------
# UI-Komponenten
# -------------------------

def render_question_section():
    # Scope & Rolle aus Session holen (oder Default)
    scope = st.session_state.get("scope", "Unternehmensweit")
    role_filter = st.session_state.get("role_filter", "Alle")

    filtered_questions = [
        q for q in QUESTIONS
        if q["scope"] == scope and role_matches(role_filter, q["role"])
    ]

    answers = {}
    current_group = None

    if not filtered_questions:
        st.write("Keine Fragen für diese Kombination aus Bereich und Rolle definiert.")
    else:
        for q in filtered_questions:
            group_label = f"{q['dimension']} – Rolle: {q['role']}"
            if group_label != current_group:
                st.markdown(f"### {group_label}")
                current_group = group_label

            st.markdown(
                f"""
                <div style="font-size:18px; font-weight:500; line-height:1.3; margin-top:0.4rem; margin-bottom:0.2rem;">
                    {q['text']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_slider, _ = st.columns([1, 3])
            with col_slider:
                val = st.slider(
                    label="Bewertung (0–5)",
                    min_value=0,
                    max_value=5,
                    value=0,
                    step=1,
                    key=q["id"]
                )
                answers[q["id"]] = val

                st.caption(
                    f"{val} – {SCALE_DEFS[val]['kurz']}: {SCALE_DEFS[val]['detail']}"
                )

    return answers

def render_metrics_section():
    st.subheader("Kennzahlen & Use-Case-Durchdringung")

    st.markdown("**1. Investitionsvolumen für KI/Digitalisierung**")
    col1, col2 = st.columns(2)
    with col1:
        invest_ki_abs = st.number_input(
            "Jährliches Investitionsvolumen KI/Digitalisierung (in Mio. €)",
            min_value=0.0,
            step=0.1,
            format="%.1f",
            key="invest_ki_abs"
        )
    with col2:
        invest_ki_share = st.number_input(
            "Anteil KI-/Digital-Investitionen an Gesamtinvestitionen (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            key="invest_ki_share"
        )
    score_invest = score_percent(
        invest_ki_share,
        bands=[0, 1, 5, 10, 20]
    )

    st.markdown("---")
    st.markdown("**2. Use-Case-Portfolio (Idee → Pilot → Produktiv)**")
    col_u1, col_u2, col_u3 = st.columns(3)
    with col_u1:
        n_usecases_idea = st.number_input(
            "Anzahl identifizierte/bewertete Use Cases",
            min_value=0,
            step=1,
            key="n_usecases_idea"
        )
    with col_u2:
        n_usecases_pilot = st.number_input(
            "Anzahl laufende Piloten/PoCs",
            min_value=0,
            step=1,
            key="n_usecases_pilot"
        )
    with col_u3:
        n_usecases_prod = st.number_input(
            "Anzahl produktive Use Cases im Tagesgeschäft",
            min_value=0,
            step=1,
            key="n_usecases_prod"
        )

    total_usecases = n_usecases_idea + n_usecases_pilot + n_usecases_prod
    score_usecases_total = score_count(
        total_usecases,
        bands=[0, 3, 7, 15, 30]
    )
    score_usecases_prod = score_count(
        n_usecases_prod,
        bands=[0, 1, 3, 7, 15]
    )
    score_usecases = round((score_usecases_total + score_usecases_prod) / 2, 1)

    st.markdown("---")
    st.markdown("**3. Durchdringung der Kernprozesse**")
    share_core_processes = st.slider(
        "Anteil der Kernprozesse mit mindestens einem produktiven KI-/Digital-Use-Case (%)",
        min_value=0,
        max_value=100,
        step=5,
        value=0,
        key="share_core_processes"
    )
    score_core = score_percent(
        share_core_processes,
        bands=[0, 5, 20, 40, 60]
    )

    st.markdown("---")
    st.markdown("**4. Umsatzanteil digitaler/KI-basierter Services**")
    share_digital_revenue = st.slider(
        "Anteil des Umsatzes aus digitalen/KI-basierten Services (%)",
        min_value=0,
        max_value=100,
        step=5,
        value=0,
        key="share_digital_revenue"
    )
    score_revenue = score_percent(
        share_digital_revenue,
        bands=[0, 1, 5, 15, 30]
    )

    st.markdown("---")
    st.markdown("**5. FTE in Data/AI/Digital-Rollen und Qualifizierung**")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fte_data_ai = st.number_input(
            "Anzahl FTE in Data/AI/Digital-Rollen",
            min_value=0,
            step=1,
            key="fte_data_ai"
        )
    with col_f2:
        share_trained_staff = st.slider(
            "Anteil der Belegschaft mit relevanten KI-/Daten-Trainings pro Jahr (%)",
            min_value=0,
            max_value=100,
            step=5,
            value=0,
            key="share_trained_staff"
        )

    score_fte = score_count(
        fte_data_ai,
        bands=[0, 5, 20, 50, 100]
    )
    score_training = score_percent(
        share_trained_staff,
        bands=[0, 5, 20, 40, 60]
    )
    score_skills = round((score_fte + score_training) / 2, 1)

    st.markdown("---")
    st.markdown("**6. KPI-System und Business Cases für KI/Digital**")
    level_kpi = st.selectbox(
        "Reifegrad KPI-/Business-Case-Steuerung für KI-/Digital-Initiativen",
        options=[
            "Kein KPI-/BC-System",
            "Einzelne Piloten mit grober Wirkungsschätzung",
            "Systematische Business Cases bei größeren Projekten",
            "Standardisiertes KPI-/BC-Framework für alle KI-/Digital-Projekte",
            "Integriertes, datengetriebenes Performance-Management (laufendes Monitoring)"
        ],
        key="level_kpi"
    )
    score_kpi = score_select(
        level_kpi,
        mapping={
            "Kein KPI-/BC-System": 0,
            "Einzelne Piloten mit grober Wirkungsschätzung": 2,
            "Systematische Business Cases bei größeren Projekten": 3,
            "Standardisiertes KPI-/BC-Framework für alle KI-/Digital-Projekte": 4,
            "Integriertes, datengetriebenes Performance-Management (laufendes Monitoring)": 5,
        }
    )

    st.markdown("---")
    st.markdown("**7. Strategie, Governance und Ownership für KI/Digital**")
    level_strategy = st.selectbox(
        "Reifegrad Digital-/KI-Strategie und Governance",
        options=[
            "Keine explizite Digital-/KI-Strategie",
            "Grundsatzpapier, aber keine klare Roadmap",
            "Definierte Strategie mit initialer Roadmap und Verantwortlichkeiten",
            "Etabliertes Digital-/KI-Target Operating Model mit klarer Governance",
            "Kontinuierlich adaptierte, datengetriebene Digital-/KI-Strategie (OKR, Reviews, M&A-Integration)"
        ],
        key="level_strategy"
    )
    score_strategy = score_select(
        level_strategy,
        mapping={
            "Keine explizite Digital-/KI-Strategie": 0,
            "Grundsatzpapier, aber keine klare Roadmap": 2,
            "Definierte Strategie mit initialer Roadmap und Verantwortlichkeiten": 3,
            "Etabliertes Digital-/KI-Target Operating Model mit klarer Governance": 4,
            "Kontinuierlich adaptierte, datengetriebene Digital-/KI-Strategie (OKR, Reviews, M&A-Integration)": 5,
        }
    )

    subscores = [
        score_invest,
        score_usecases,
        score_core,
        score_revenue,
        score_skills,
        score_kpi,
        score_strategy,
    ]
    metrics_score = round(sum(subscores) / len(subscores), 2)

    st.markdown("---")
    st.info(f"Teil-Score Kennzahlen & Use Cases: {metrics_score} / 5")

    with st.expander("Detail-Scores dieser Sektion"):
        st.write({
            "Investitionen KI/Digital": score_invest,
            "Use-Case-Portfolio": score_usecases,
            "Kernprozess-Durchdringung": score_core,
            "Digital-/KI-Umsatzanteil": score_revenue,
            "Skills & Trainings": score_skills,
            "KPI- & Business-Case-System": score_kpi,
            "Strategie & Governance": score_strategy,
        })

    return metrics_score

# -------------------------
# Sidebar
# -------------------------

st.sidebar.title("Einstellungen")

company = st.sidebar.text_input("Firma / Kunde", value="")
project = st.sidebar.text_input("Projekt / Assessment", value="")
assessor = st.sidebar.text_input("Bearbeiter", value="")

scope = st.sidebar.selectbox(
    "Bereich",
    ["Unternehmensweit", "Entwicklung", "Einkauf", "Service"],
    key="scope"
)

role_filter = st.sidebar.selectbox(
    "Rollenfilter",
    ["Alle", "Management", "Fachbereich", "IT"],
    key="role_filter"
)

all_dimensions = sorted({q["dimension"] for q in QUESTIONS})
dim_weights = {}

st.sidebar.subheader("Gewichtung Dimensionen")
for dim in all_dimensions:
    default = 1.0
    if dim == "Governance & Daten":
        default = 1.5
    dim_weights[dim] = st.sidebar.number_input(
        f"Gewicht {dim}",
        min_value=0.0,
        max_value=5.0,
        value=default,
        step=0.1
    )

# -------------------------
# Hauptbereich mit Tabs
# -------------------------

st.title("KI-Reifegrad-Assessment – Mittelstand")

with st.expander("Erläuterung der Skala 0–5"):
    for lvl in range(0, 6):
        st.markdown(
            f"**{lvl} – {SCALE_DEFS[lvl]['kurz']}**  \n"
            f"{SCALE_DEFS[lvl]['detail']}"
        )

meta_info = []
if company:
    meta_info.append(f"Firma: {company}")
if project:
    meta_info.append(f"Projekt: {project}")
if assessor:
    meta_info.append(f"Bearbeiter: {assessor}")

meta_info.append(f"Bereich: {scope}")
meta_info.append(f"Rolle: {role_filter}")
st.markdown(" – ".join(meta_info))

tab_fragen, tab_kennzahlen, tab_auswertung = st.tabs(
    ["Fragenkatalog", "Kennzahlen & Use Cases", "Auswertung"]
)

with tab_fragen:
    answers = render_question_section()

with tab_kennzahlen:
    metrics_score = render_metrics_section()

with tab_auswertung:
    st.header("Auswertung")

    dim_scores = compute_dimension_scores(scope, answers)
    overall_score_questions = compute_overall_score(dim_scores, dim_weights)

    combined_score = None
    if overall_score_questions is not None:
        combined_score = (overall_score_questions + metrics_score) / 2

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Scores je Dimension (Fragenkatalog)")
        if dim_scores:
            df_scores = pd.DataFrame(
                [{"Dimension": d, "Score": round(s, 2)} for d, s in dim_scores.items()]
            )
            st.dataframe(df_scores, use_container_width=True)
        else:
            st.write("Keine Daten verfügbar.")

        st.subheader("Gesamt-Reifegrad Fragenkatalog")
        if overall_score_questions is not None:
            st.metric("Gesamt-Score Fragen", f"{overall_score_questions:.2f} / 5.00")
        else:
            st.write("Gesamt-Score nicht berechenbar.")

        st.subheader("Teil-Score Kennzahlen & Use Cases")
        st.metric("Kennzahlen-Score", f"{metrics_score:.2f} / 5.00")

        if combined_score is not None:
            st.subheader("Gesamt-Reifegrad kombiniert")
            st.metric("Kombinierter Score", f"{combined_score:.2f} / 5.00")

    with col2:
        st.subheader("Spidergraphik (Fragenkatalog)")
        plot_radar(dim_scores, f"Reifegrad – {scope} ({role_filter})")
