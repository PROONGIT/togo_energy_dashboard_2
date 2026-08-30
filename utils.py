import pandas as pd
import json
import streamlit as st

DATA = "data/"

# ---------- Palette institutionnelle (drapeau togolais) ----------
TOGO_GREEN = "#006A4E"
TOGO_GREEN_DARK = "#004D38"
TOGO_YELLOW = "#FFCE00"
TOGO_RED = "#D21034"
TOGO_WHITE = "#FFFFFF"
TOGO_GREY = "#4A4A4A"

REGION_COLORS = {
    "Maritime": "#8BC98B",
    "Plateaux": "#4DAF4A",
    "Centrale": "#238B45",
    "Kara": "#006D2C",
    "Savanes": "#00441B",
}

VILLES_ORDRE = ["Lomé", "Tabligbo", "Atakpamé", "Kouma konda", "Sotouboua",
                "Sokodé", "Kara", "Niamtougou", "Dapaong", "Mango"]

# Palette qualitative fortement contrastée (Okabe-Ito étendue) - une couleur par ville,
# volontairement non-graduelle pour éviter toute confusion entre villes voisines
VILLE_COLORS = {
    "Lomé": "#0072B2",
    "Tabligbo": "#D55E00",
    "Atakpamé": "#009E73",
    "Kouma konda": "#CC79A7",
    "Sotouboua": "#B8860B",
    "Sokodé": "#56B4E9",
    "Kara": "#E69F00",
    "Niamtougou": "#8B008B",
    "Dapaong": "#111111",
    "Mango": "#D21034",
}

# Coordonnées approximatives des 10 villes (Sud -> Nord), pour superposition sur la carte des forêts
VILLE_COORDS = {
    "Lomé": (6.1319, 1.2228),
    "Tabligbo": (6.5892, 1.5069),
    "Atakpamé": (7.5225, 1.1226),
    "Kouma konda": (6.9500, 0.6200),
    "Sotouboua": (8.5667, 0.9833),
    "Sokodé": (8.9833, 1.1333),
    "Kara": (9.5511, 1.1861),
    "Niamtougou": (9.7667, 1.1000),
    "Dapaong": (10.8639, 0.2078),
    "Mango": (10.3667, 0.4720),
}


@st.cache_data
def load_wb():
    return pd.read_csv(DATA + "wb_indicators.csv")


@st.cache_data
def load_ges_2018():
    return pd.read_csv(DATA + "ges_secteur_2018.csv")


@st.cache_data
def load_temperatures():
    df = pd.read_csv(DATA + "temperatures.csv", parse_dates=["date"])
    df["ville"] = pd.Categorical(df["ville"], categories=VILLES_ORDRE, ordered=True)
    return df


@st.cache_data
def load_renewables_combustible():
    return pd.read_csv(DATA + "renewables_combustible.csv")


@st.cache_data
def load_co2_power_long():
    return pd.read_csv(DATA + "co2_power_long.csv")


@st.cache_data
def load_forets_table():
    return pd.read_csv(DATA + "forets_table.csv")


@st.cache_data
def load_forets_geojson():
    with open(DATA + "forets.geojson") as f:
        return json.load(f)


# ---------- Composants UI "relief" (style plateforme gouvernementale) ----------

def inject_css():
    st.markdown(f"""
    <style>
    .top-flag-bar {{
        height: 6px; width: 100%; border-radius: 4px; margin-bottom: 1rem;
        background: linear-gradient(90deg, {TOGO_GREEN} 0%, {TOGO_GREEN} 33%,
                    {TOGO_YELLOW} 33%, {TOGO_YELLOW} 66%, {TOGO_RED} 66%, {TOGO_RED} 100%);
    }}
    .big-title {{ font-size: 2rem; font-weight: 800; margin-bottom:0; color: {TOGO_GREEN_DARK}; }}
    .subtitle {{ color: #5b6b66; font-size: 1.05rem; margin-top:0.2rem; }}

    .kpi-card {{
        background: {TOGO_WHITE};
        border-radius: 12px;
        padding: 0.9rem 1rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.10);
        border-top: 5px solid var(--kpi-accent, {TOGO_GREEN});
        height: 100%;
    }}
    .kpi-label {{ font-size: 0.82rem; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.02em;}}
    .kpi-value {{ font-size: 1.7rem; font-weight: 800; color: #1f2937; margin-top: 2px;}}
    .kpi-help {{ font-size: 0.78rem; color: #8a8a8a; margin-top: 2px;}}

    .constat-box {{
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin: 0.6rem 0 1rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        border-left: 6px solid var(--c-accent, {TOGO_GREEN});
        background: var(--c-bg, #F0FAF6);
    }}
    .constat-title {{ font-weight: 700; margin-bottom: 0.2rem; color: #1f2937; }}
    .constat-text {{ color: #374151; font-size: 0.95rem; line-height: 1.45; }}

    .section-tag {{
        display:inline-block; background:{TOGO_GREEN}; color:white; font-weight:700;
        font-size:0.78rem; padding: 3px 10px; border-radius: 20px; margin-bottom: 0.5rem;
        letter-spacing: 0.03em; text-transform: uppercase;
    }}
    .analysis-caption {{
        background: #F7F7F5; border-radius: 8px; padding: 0.7rem 1rem; margin-top: 0.3rem;
        border-left: 4px solid {TOGO_GREEN}; font-size: 0.92rem; color: #374151; line-height: 1.5;
    }}
    .reco-card {{
        background: white; border-radius: 12px; padding: 1.1rem 1.2rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.10); border-top: 6px solid var(--r-accent, {TOGO_GREEN});
        height: 100%;
    }}
    .reco-title {{ font-weight: 800; font-size: 1.05rem; margin-bottom: 0.4rem; color: #1f2937; }}
    div[data-testid="stMetricValue"] {{ font-size: 1.5rem; }}
    </style>
    """, unsafe_allow_html=True)


def kpi_card(col, label, value, accent=TOGO_GREEN, help_text=None):
    help_html = f'<div class="kpi-help">{help_text}</div>' if help_text else ""
    col.markdown(f"""
    <div class="kpi-card" style="--kpi-accent: {accent};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {help_html}
    </div>
    """, unsafe_allow_html=True)


def constat_box(title, text, kind="neutral"):
    """kind: 'positif' (vert), 'alerte' (jaune), 'critique' (rouge), 'neutral' (vert clair)"""
    styles = {
        "positif": (TOGO_GREEN, "#EAF7F1"),
        "alerte": (TOGO_YELLOW, "#FFF9E5"),
        "critique": (TOGO_RED, "#FDEBEC"),
        "neutral": (TOGO_GREEN, "#F0FAF6"),
    }
    accent, bg = styles.get(kind, styles["neutral"])
    st.markdown(f"""
    <div class="constat-box" style="--c-accent: {accent}; --c-bg: {bg};">
        <div class="constat-title">{title}</div>
        <div class="constat-text">{text}</div>
    </div>
    """, unsafe_allow_html=True)


def section_tag(text):
    st.markdown(f'<span class="section-tag">{text}</span>', unsafe_allow_html=True)


def analysis_caption(text):
    st.markdown(f'<div class="analysis-caption">{text}</div>', unsafe_allow_html=True)
