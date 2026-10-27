import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. FILE & DATASET CONFIGURATION
# ==============================================================================
APP_DIR = Path(__file__).resolve().parent
CSV_FILENAME = "Plastic Waste Around the World.csv"
CSV_PATH = APP_DIR / CSV_FILENAME

EXPECTED_COLUMNS = [
    "Country",
    "Total_Plastic_Waste_MT",
    "Main_Sources",
    "Recycling_Rate",
    "Per_Capita_Waste_KG",
    "Coastal_Waste_Risk",
]

NUMERIC_COLUMNS = [
    "Total_Plastic_Waste_MT",
    "Recycling_Rate",
    "Per_Capita_Waste_KG",
]

# Risk category visual styling and ordering
RISK_ORDER = ["Low", "Medium", "High", "Very_High"]

# Dribbble Revenue App Theme Palettes
THEMES = {
    "dark": {
        "app_bg": "#0B0F19",
        "card_bg": "rgba(17, 24, 39, 0.75)",
        "card_border": "rgba(255, 255, 255, 0.08)",
        "card_hover_border": "rgba(99, 102, 241, 0.35)",
        "header_bg": "linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(30, 27, 75, 0.85) 50%, rgba(15, 23, 42, 0.95) 100%)",
        "text_main": "#F8FAFC",
        "text_muted": "#94A3B8",
        "text_faint": "#64748B",
        "grid_color": "rgba(255, 255, 255, 0.05)",
        "border_color": "rgba(255, 255, 255, 0.08)",
        "accent_purple": "#8B5CF6",
        "accent_indigo": "#6366F1",
        "accent_emerald": "#10B981",
        "accent_cyan": "#06B6D4",
        "accent_amber": "#F59E0B",
        "accent_rose": "#F43F5E",
        "sidebar_bg": "#0D1322",
        "sidebar_border": "rgba(255, 255, 255, 0.06)",
        "stat_pill_bg": "rgba(99, 102, 241, 0.12)",
        "stat_pill_text": "#A5B4FC",
        "badge_border": "rgba(99, 102, 241, 0.3)",
        "tooltip_bg": "#0F172A",
    },
    "light": {
        "app_bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "card_border": "#E2E8F0",
        "card_hover_border": "rgba(99, 102, 241, 0.4)",
        "header_bg": "linear-gradient(135deg, #0F172A 0%, #1E1B4B 60%, #1E293B 100%)",
        "text_main": "#0F172A",
        "text_muted": "#475569",
        "text_faint": "#94A3B8",
        "grid_color": "rgba(0, 0, 0, 0.05)",
        "border_color": "#E2E8F0",
        "accent_purple": "#7C3AED",
        "accent_indigo": "#4F46E5",
        "accent_emerald": "#059669",
        "accent_cyan": "#0891B2",
        "accent_amber": "#D97706",
        "accent_rose": "#E11D48",
        "sidebar_bg": "#FFFFFF",
        "sidebar_border": "#E2E8F0",
        "stat_pill_bg": "rgba(99, 102, 241, 0.08)",
        "stat_pill_text": "#4F46E5",
        "badge_border": "rgba(99, 102, 241, 0.25)",
        "tooltip_bg": "#0F172A",
    },
}

RISK_COLORS = {
    "Low": "#10B981",        # Emerald
    "Medium": "#06B6D4",     # Neon Cyan
    "High": "#F59E0B",       # Vivid Amber
    "Very_High": "#F43F5E",  # Rose Coral
}

# ==============================================================================
# 2. STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Revenue.OS // Eco-Waste & Valuation Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 3. DRIBBBLE REVENUE APP CSS INJECTION
# ==============================================================================
def apply_dribbble_theme(theme_mode: str = "dark") -> None:
    """Injects high-finish Dribbble 'Revenue App' UI styling."""
    t = THEMES[theme_mode]

    is_dark = theme_mode == "dark"
    app_bg = t["app_bg"]
    card_bg = t["card_bg"]
    card_border = t["card_border"]
    text_main = t["text_main"]
    text_muted = t["text_muted"]
    stat_pill_bg = t["stat_pill_bg"]
    stat_pill_text = t["stat_pill_text"]
    badge_border = t["badge_border"]

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

        :root {{
            --font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --app-bg: {app_bg};
            --card-bg: {card_bg};
            --card-border: {card_border};
            --text-main: {text_main};
            --text-muted: {text_muted};
            --indigo: #6366F1;
            --purple: #8B5CF6;
            --emerald: #10B981;
            --cyan: #06B6D4;
            --rose: #F43F5E;
            --amber: #F59E0B;
        }}

        /* Global Canvas */
        html, body, [class*="css"], .stApp {{
            font-family: var(--font-family) !important;
            background-color: var(--app-bg) !important;
            color: var(--text-main) !important;
        }}

        .stApp {{
            background-color: var(--app-bg) !important;
            {'background-image: radial-gradient(circle at 10% 0%, rgba(99, 102, 241, 0.12) 0%, transparent 40%), radial-gradient(circle at 90% 100%, rgba(16, 185, 129, 0.08) 0%, transparent 40%);' if is_dark else 'background-image: radial-gradient(circle at 10% 0%, rgba(99, 102, 241, 0.04) 0%, transparent 40%), radial-gradient(circle at 90% 100%, rgba(6, 182, 212, 0.03) 0%, transparent 40%);'}
            background-attachment: fixed;
        }}

        .block-container {{
            max-width: 1560px !important;
            padding-top: 1rem !important;
            padding-bottom: 4rem !important;
            padding-left: clamp(1rem, 2.5vw, 2.5rem) !important;
            padding-right: clamp(1rem, 2.5vw, 2.5rem) !important;
        }}

        /* Top Dribbble App Header Bar */
        .revenue-app-header {{
            background: {t["header_bg"]};
            border-radius: 20px;
            padding: 1.6rem 2.2rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 20px 40px -15px {'rgba(0, 0, 0, 0.5)' if is_dark else 'rgba(15, 23, 42, 0.12)'};
            border: 1px solid {t["card_border"]};
            display: flex;
            flex-direction: column;
            gap: 0.8rem;
            position: relative;
            overflow: hidden;
        }}

        .revenue-app-header::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 320px;
            height: 100%;
            background: radial-gradient(circle at 80% 20%, rgba(99, 102, 241, 0.25) 0%, transparent 70%);
            pointer-events: none;
        }}

        .nav-meta-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 0.8rem;
        }}

        .nav-meta-left {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            flex-wrap: wrap;
        }}

        .brand-badge {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%);
            color: #C7D2FE;
            border: 1px solid rgba(165, 180, 252, 0.35);
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            padding: 0.3rem 0.75rem;
            border-radius: 9999px;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-family: var(--font-mono);
        }}

        .live-dot {{
            width: 7px;
            height: 7px;
            background-color: #10B981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10B981;
            display: inline-block;
            animation: pulse-green 2s infinite;
        }}

        @keyframes pulse-green {{
            0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
            70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
            100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
        }}

        .nav-meta-right {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.75rem;
            color: #94A3B8;
        }}

        .pill-chip {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #E2E8F0;
            padding: 0.25rem 0.65rem;
            border-radius: 8px;
            font-size: 0.72rem;
            font-weight: 600;
        }}

        .header-main-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .header-title-box {{
            flex: 1;
            min-width: 280px;
        }}

        .app-title {{
            color: #FFFFFF !important;
            font-size: clamp(1.4rem, 2.4vw, 2.2rem) !important;
            font-weight: 800 !important;
            letter-spacing: -0.035em !important;
            margin: 0 !important;
            line-height: 1.15 !important;
        }}

        .app-title-gradient {{
            background: linear-gradient(135deg, #FFFFFF 30%, #A5B4FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .app-subtitle {{
            color: #94A3B8 !important;
            font-size: clamp(0.82rem, 1vw, 0.92rem) !important;
            margin: 0.35rem 0 0 0 !important;
            line-height: 1.45 !important;
            font-weight: 400 !important;
        }}

        /* Hero Revenue Metric Cards (Dribbble Style) */
        .revenue-kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(215px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}

        .rev-card {{
            background: {card_bg};
            border-radius: 18px;
            padding: 1.25rem 1.15rem;
            border: 1px solid {card_border};
            box-shadow: 0 10px 25px -5px {'rgba(0, 0, 0, 0.3)' if is_dark else 'rgba(15, 23, 42, 0.04)'};
            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .rev-card:hover {{
            transform: translateY(-3px);
            border-color: {t["card_hover_border"]};
            box-shadow: 0 18px 35px -8px {'rgba(99, 102, 241, 0.25)' if is_dark else 'rgba(99, 102, 241, 0.12)'};
        }}

        .rev-card-glow-indigo::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #6366F1, #8B5CF6);
        }}

        .rev-card-glow-emerald::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #10B981, #059669);
        }}

        .rev-card-glow-cyan::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #06B6D4, #3B82F6);
        }}

        .rev-card-glow-amber::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #F59E0B, #EA580C);
        }}

        .rev-card-glow-rose::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #F43F5E, #E11D48);
        }}

        .rev-card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.6rem;
        }}

        .rev-card-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {text_muted};
        }}

        .rev-card-icon-badge {{
            width: 32px;
            height: 32px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem;
            background: {'rgba(255, 255, 255, 0.05)' if is_dark else '#F1F5F9'};
            border: 1px solid {'rgba(255, 255, 255, 0.08)' if is_dark else '#E2E8F0'};
        }}

        .rev-card-val {{
            font-size: clamp(1.45rem, 2.1vw, 1.95rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            color: {text_main};
            line-height: 1.15;
            margin-bottom: 0.45rem;
            font-feature-settings: "tnum";
            font-variant-numeric: tabular-nums;
        }}

        .rev-card-unit {{
            font-size: 0.82rem;
            font-weight: 600;
            color: {text_muted};
        }}

        .rev-card-trend-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-top: 0.2rem;
        }}

        .trend-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.2rem 0.55rem;
            border-radius: 9999px;
            font-family: var(--font-mono);
        }}

        .trend-pill.positive {{
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .trend-pill.neutral {{
            background: rgba(99, 102, 241, 0.15);
            color: #A5B4FC;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }}

        .trend-pill.alert {{
            background: rgba(244, 63, 94, 0.15);
            color: #FB7185;
            border: 1px solid rgba(244, 63, 94, 0.3);
        }}

        .trend-pill.warning {{
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        .rev-card-caption {{
            font-size: 0.72rem;
            color: {text_muted};
            font-weight: 500;
        }}

        /* Dribbble Section Headers */
        .dribbble-section-title {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 1.8rem;
            margin-bottom: 0.85rem;
            padding-bottom: 0.4rem;
            border-bottom: 1px solid {t["border_color"]};
        }}

        .dribbble-section-title h3 {{
            margin: 0;
            font-size: 1.15rem;
            font-weight: 800;
            color: {text_main};
            letter-spacing: -0.025em;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section-tag {{
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {text_muted};
            background: {'rgba(255, 255, 255, 0.05)' if is_dark else '#F1F5F9'};
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
        }}

        /* Plotly Chart Card Styling */
        div[data-testid="stPlotlyChart"] {{
            border: 1px solid {card_border};
            border-radius: 18px;
            background: {card_bg};
            padding: 0.6rem 0.6rem 0.3rem 0.6rem;
            box-shadow: 0 10px 25px -5px {'rgba(0, 0, 0, 0.3)' if is_dark else 'rgba(15, 23, 42, 0.04)'};
            margin-bottom: 1.2rem;
            transition: border-color 0.2s ease;
        }}

        div[data-testid="stPlotlyChart"]:hover {{
            border-color: {t["card_hover_border"]};
        }}

        /* Automated Insights (Dribbble Micro-cards) */
        .insight-pill-card {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 14px;
            padding: 1rem 1.1rem;
            box-shadow: 0 8px 20px -5px {'rgba(0, 0, 0, 0.25)' if is_dark else 'rgba(15, 23, 42, 0.03)'};
            margin-bottom: 0.8rem;
            position: relative;
            overflow: hidden;
            border-left: 4px solid #6366F1;
        }}

        .insight-pill-card.emerald {{ border-left-color: #10B981; }}
        .insight-pill-card.amber {{ border-left-color: #F59E0B; }}
        .insight-pill-card.cyan {{ border-left-color: #06B6D4; }}
        .insight-pill-card.rose {{ border-left-color: #F43F5E; }}

        .insight-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.25rem;
        }}

        .insight-tag {{
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {text_muted};
        }}

        .insight-main {{
            font-size: 0.88rem;
            font-weight: 700;
            color: {text_main};
            line-height: 1.35;
        }}

        .insight-subtext {{
            font-size: 0.72rem;
            color: {text_muted};
            margin-top: 0.2rem;
        }}

        /* Country Profile Hero Card */
        .profile-hero {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 20px;
            padding: 1.4rem;
            box-shadow: 0 12px 30px -8px {'rgba(0, 0, 0, 0.4)' if is_dark else 'rgba(15, 23, 42, 0.05)'};
            margin-bottom: 1.4rem;
        }}

        .profile-badge-pill {{
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }}

        .profile-badge-pill.Low {{
            background: rgba(16, 185, 129, 0.2);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }}
        .profile-badge-pill.Medium {{
            background: rgba(6, 182, 212, 0.2);
            color: #67E8F9;
            border: 1px solid rgba(6, 182, 212, 0.35);
        }}
        .profile-badge-pill.High {{
            background: rgba(245, 158, 11, 0.2);
            color: #FCD34D;
            border: 1px solid rgba(245, 158, 11, 0.35);
        }}
        .profile-badge-pill.Very_High {{
            background: rgba(244, 63, 94, 0.2);
            color: #FDA4AF;
            border: 1px solid rgba(244, 63, 94, 0.35);
        }}

        /* Data Ledger Note */
        .ledger-banner {{
            background: {'rgba(15, 23, 42, 0.6)' if is_dark else '#F1F5F9'};
            border: 1px solid {card_border};
            border-left: 4px solid #6366F1;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            font-size: 0.78rem;
            color: {text_muted};
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        /* Buttons & Tab Controls */
        div[data-testid="stDownloadButton"] button {{
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 0.82rem !important;
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            padding: 0.5rem 1.1rem !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
            transition: all 0.2s ease !important;
        }}

        div[data-testid="stDownloadButton"] button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5) !important;
        }}

        div[data-testid="stButton"] button {{
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            transition: all 0.15s ease !important;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: {t["sidebar_bg"]} !important;
            border-right: 1px solid {t["sidebar_border"]} !important;
        }}

        /* Tabs Styling (Dribbble Segmented Style) */
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background: {'rgba(15, 23, 42, 0.6)' if is_dark else '#F1F5F9'};
            padding: 0.35rem 0.45rem;
            border-radius: 14px;
            border: 1px solid {card_border};
            margin-bottom: 1.2rem;
        }}

        div[data-testid="stTabs"] [data-baseweb="tab"] {{
            border-radius: 10px !important;
            font-size: 0.82rem !important;
            font-weight: 700 !important;
            padding: 0.45rem 1rem !important;
            color: {text_muted} !important;
            background: transparent !important;
            border: none !important;
            transition: all 0.15s ease;
        }}

        div[data-testid="stTabs"] [aria-selected="true"] {{
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35) !important;
        }}

        /* Footer */
        .revenue-footer {{
            margin-top: 3.5rem;
            padding: 1.5rem 0;
            border-top: 1px solid {t["border_color"]};
            text-align: center;
            color: {text_muted};
            font-size: 0.78rem;
        }}

        .revenue-footer-brand {{
            font-weight: 800;
            letter-spacing: -0.02em;
            color: {text_main};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 4. DATA LOADING, VALIDATION & INTEGRITY CHECKS
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_dataset(csv_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the authentic country CSV dataset from disk.
    Strict column verification, whitespace stripping, and safe numeric parsing.
    NEVER generates synthetic records.
    """
    if not csv_path.is_file():
        return pd.DataFrame(), {
            "status": "missing_file",
            "path": str(csv_path),
            "error": f"Dataset file not found at: {csv_path}",
        }

    try:
        raw_df = pd.read_csv(csv_path)
    except Exception as exc:
        return pd.DataFrame(), {
            "status": "read_error",
            "path": str(csv_path),
            "error": f"Failed to parse CSV file: {exc}",
        }

    # Normalize column names
    raw_columns = [str(col).strip() for col in raw_df.columns]
    raw_df.columns = raw_columns

    col_map = {}
    lower_map = {col.lower(): col for col in EXPECTED_COLUMNS}
    for col in raw_columns:
        if col.lower() in lower_map:
            col_map[col] = lower_map[col.lower()]

    df = raw_df.rename(columns=col_map).copy()

    # Verify required columns
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        return pd.DataFrame(), {
            "status": "missing_columns",
            "missing": missing_cols,
            "found": list(raw_df.columns),
            "error": f"Dataset is missing required columns: {', '.join(missing_cols)}",
        }

    df = df[EXPECTED_COLUMNS].copy()

    # Clean text columns
    df["Country"] = df["Country"].astype(str).str.strip()
    df["Main_Sources"] = df["Main_Sources"].astype(str).str.strip()
    df["Coastal_Waste_Risk"] = df["Coastal_Waste_Risk"].astype(str).str.strip()

    # Safely convert numeric columns
    numeric_issues = {}
    for col in NUMERIC_COLUMNS:
        original_non_na = df[col].notna().sum()
        df[col] = pd.to_numeric(df[col], errors="coerce")
        parsed_non_na = df[col].notna().sum()
        coerced_count = int(original_non_na - parsed_non_na)
        if coerced_count > 0:
            numeric_issues[col] = coerced_count

    # Calculate Circular Economy Metrics (Monetization & Valuation)
    # Recycled MT = Total_Plastic_Waste_MT * (Recycling_Rate / 100)
    # Recycled Material Value: Avg global price for recovered secondary polymers ~ $850 / MT
    # Unmanaged Waste Leakage Cost: ~$1,200 / MT
    df["Recycled_Waste_MT"] = df["Total_Plastic_Waste_MT"] * (df["Recycling_Rate"] / 100.0)
    df["Material_Valuation_USD_M"] = df["Recycled_Waste_MT"] * 850.0  # In Millions USD (since MT is in Millions)

    meta = {
        "status": "success",
        "total_records": len(df),
        "unique_countries": df["Country"].nunique(),
        "numeric_issues": numeric_issues,
        "path": str(csv_path),
    }
    return df, meta


# ==============================================================================
# 5. DRIBBBLE PLOTLY THEME ENGINE
# ==============================================================================
def apply_dribbble_chart_theme(
    fig: go.Figure,
    theme_mode: str = "dark",
    height: int = 380,
    title: Optional[str] = None,
    show_legend: bool = True,
) -> go.Figure:
    """Applies a bespoke Dribbble dark/light modern UI styling to Plotly charts."""
    t = THEMES[theme_mode]
    is_dark = theme_mode == "dark"

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=55 if title else 25, b=25),
        font=dict(
            family="Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
            color=t["text_main"],
            size=11,
        ),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=13.5, color=t["text_main"], family="Plus Jakarta Sans"),
            x=0.015,
            xanchor="left",
        ) if title else None,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10.5, color=t["text_muted"]),
            bgcolor="rgba(0,0,0,0)",
        ) if show_legend else dict(visible=False),
        hoverlabel=dict(
            bgcolor="#0F172A" if is_dark else "#1E293B",
            bordercolor="#6366F1",
            font=dict(
                family="Plus Jakarta Sans, sans-serif",
                color="#FFFFFF",
                size=12,
            ),
        ),
        hovermode="closest",
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=t["grid_color"],
        zerolinecolor=t["grid_color"],
        linecolor=t["border_color"],
        tickfont=dict(size=10, color=t["text_muted"]),
        title_font=dict(size=11, color=t["text_main"]),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=t["grid_color"],
        zerolinecolor=t["grid_color"],
        linecolor=t["border_color"],
        tickfont=dict(size=10, color=t["text_muted"]),
        title_font=dict(size=11, color=t["text_main"]),
    )

    return fig


# ==============================================================================
# 6. DRIBBBLE SIDEBAR FILTERS & CONTROLS
# ==============================================================================
def render_sidebar(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
    """Renders the sleek Dribbble parameter control panel and returns filtered data and theme."""
    st.sidebar.markdown(
        """
        <div style="padding-bottom: 0.8rem; margin-bottom: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span style="font-size:1.15rem;">⚡</span>
                <span style="font-size:1.05rem; font-weight:800; letter-spacing:-0.02em;">Revenue.OS Control</span>
            </div>
            <div style="font-size:0.72rem; color:#94A3B8; margin-top:0.2rem;">Fintech & Eco-Analytics Parameters</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Theme Switcher (Dribbble Dark Mode vs Clean Fintech Light)
    theme_choice = st.sidebar.radio(
        "UI Aesthetic Mode",
        ["Dribbble Dark (Obsidian)", "Clean Fintech (Light)"],
        index=0,
        key="theme_radio",
        label_visibility="visible",
    )
    theme_mode = "dark" if "Dark" in theme_choice else "light"

    st.sidebar.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Reset Filters Button
    if st.sidebar.button("↺ Reset All Parameters", use_container_width=True, type="secondary"):
        for key in [
            "f_country_search",
            "f_countries_select",
            "f_coastal_risk",
            "f_main_sources",
            "f_recycling_slider",
            "f_waste_slider",
        ]:
            st.session_state.pop(key, None)
        st.rerun()

    st.sidebar.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # 1. Country Name Search (Text Input)
    search_query = st.sidebar.text_input(
        "🔍 Country Search (⌘K)",
        placeholder="Search nation...",
        key="f_country_search",
        help="Filters countries whose names contain the entered keyword.",
    ).strip()

    # 2. Country Multiselect
    all_countries = sorted(df["Country"].unique().tolist())
    selected_countries = st.sidebar.multiselect(
        "🌐 Specific Nations",
        options=all_countries,
        default=[],
        key="f_countries_select",
        help="Select specific countries to isolate in the ledger.",
    )

    # 3. Coastal Waste Risk Category
    risk_options = [r for r in RISK_ORDER if r in df["Coastal_Waste_Risk"].unique()]
    other_risks = sorted(list(set(df["Coastal_Waste_Risk"].unique()) - set(risk_options)))
    risk_options.extend(other_risks)

    selected_risks = st.sidebar.multiselect(
        "🌊 Coastal Leakage Risk",
        options=risk_options,
        default=[],
        key="f_coastal_risk",
        help="Filter by coastal plastic leakage vulnerability.",
    )

    # 4. Main Plastic Waste Source Category
    source_options = sorted(df["Main_Sources"].dropna().unique().tolist())
    selected_sources = st.sidebar.multiselect(
        "🏭 Material Source Sector",
        options=source_options,
        default=[],
        key="f_main_sources",
        help="Filter by primary recorded industrial/packaging stream.",
    )

    # 5. Recycling Rate Slider Range
    rec_min = float(df["Recycling_Rate"].min())
    rec_max = float(df["Recycling_Rate"].max())
    selected_rec_range = st.sidebar.slider(
        "♻️ Recycling Efficiency (%)",
        min_value=rec_min,
        max_value=rec_max,
        value=(rec_min, rec_max),
        step=0.1,
        format="%.1f%%",
        key="f_recycling_slider",
    )

    # 6. Total Plastic Waste Slider Range
    waste_min = float(df["Total_Plastic_Waste_MT"].min())
    waste_max = float(df["Total_Plastic_Waste_MT"].max())
    selected_waste_range = st.sidebar.slider(
        "📦 Waste Volume Range (MT)",
        min_value=waste_min,
        max_value=waste_max,
        value=(waste_min, waste_max),
        step=0.01,
        format="%.2f MT",
        key="f_waste_slider",
    )

    # Filter logic
    filtered = df.copy()

    if search_query:
        filtered = filtered[filtered["Country"].str.contains(search_query, case=False, na=False)]

    if selected_countries:
        filtered = filtered[filtered["Country"].isin(selected_countries)]

    if selected_risks:
        filtered = filtered[filtered["Coastal_Waste_Risk"].isin(selected_risks)]

    if selected_sources:
        filtered = filtered[filtered["Main_Sources"].isin(selected_sources)]

    filtered = filtered[
        filtered["Recycling_Rate"].between(selected_rec_range[0], selected_rec_range[1], inclusive="both")
    ]

    filtered = filtered[
        filtered["Total_Plastic_Waste_MT"].between(selected_waste_range[0], selected_waste_range[1], inclusive="both")
    ]

    filter_info = {
        "search_query": search_query,
        "selected_countries": selected_countries,
        "selected_risks": selected_risks,
        "selected_sources": selected_sources,
        "rec_range": selected_rec_range,
        "waste_range": selected_waste_range,
        "total_records": len(df),
        "matching_records": len(filtered),
    }

    # Sidebar KPI Pill
    match_pct = (len(filtered) / len(df) * 100) if len(df) > 0 else 0
    st.sidebar.markdown(
        f"""
        <div style="margin-top:1.2rem; padding:0.85rem; background:rgba(99, 102, 241, 0.08); border-radius:12px; border:1px solid rgba(99, 102, 241, 0.25);">
            <div style="font-size:0.68rem; font-weight:700; text-transform:uppercase; color:#A5B4FC; letter-spacing:0.08em; font-family:'JetBrains Mono', monospace;">Feed Status</div>
            <div style="font-size:1.15rem; font-weight:800; color:{'#FFFFFF' if theme_mode == 'dark' else '#0F172A'}; margin-top:0.2rem;">
                {len(filtered):,} <span style="font-size:0.8rem; font-weight:500; color:#94A3B8;">/ {len(df):,} nations</span>
            </div>
            <div style="font-size:0.72rem; color:#10B981; font-weight:700; margin-top:0.2rem;">
                ● {match_pct:.1f}% Global Coverage Active
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return filtered, filter_info, theme_mode


# ==============================================================================
# 7. DRIBBBLE REVENUE APP HERO STAT CARDS
# ==============================================================================
def render_revenue_kpi_cards(df: pd.DataFrame, total_global_countries: int, benchmark_df: pd.DataFrame) -> None:
    """Renders 5 Dribbble-style SaaS Revenue KPI metric cards."""
    if df.empty:
        total_waste = 0.0
        avg_recycling = 0.0
        avg_per_capita = 0.0
        high_risk_count = 0
        country_count = 0
        total_market_value = 0.0
    else:
        total_waste = float(df["Total_Plastic_Waste_MT"].sum())
        avg_recycling = float(df["Recycling_Rate"].mean())
        avg_per_capita = float(df["Per_Capita_Waste_KG"].mean())
        high_risk_count = int(df["Coastal_Waste_Risk"].isin(["High", "Very_High"]).sum())
        country_count = int(df["Country"].nunique())
        total_market_value = float(df["Material_Valuation_USD_M"].sum())

    bm_waste = float(benchmark_df["Total_Plastic_Waste_MT"].sum())
    bm_rec = float(benchmark_df["Recycling_Rate"].mean())
    bm_per_cap = float(benchmark_df["Per_Capita_Waste_KG"].mean())

    waste_share_pct = (total_waste / bm_waste * 100) if bm_waste > 0 else 0
    rec_delta = avg_recycling - bm_rec
    per_cap_delta = ((avg_per_capita - bm_per_cap) / bm_per_cap * 100) if bm_per_cap > 0 else 0
    risk_pct = (high_risk_count / country_count * 100) if country_count > 0 else 0

    kpi_cols = st.columns(5)

    # 1. Total Plastic Waste Volume
    with kpi_cols[0]:
        st.markdown(
            f"""
            <div class="rev-card rev-card-glow-indigo">
                <div class="rev-card-top">
                    <span class="rev-card-label">Waste Generation</span>
                    <div class="rev-card-icon-badge">📦</div>
                </div>
                <div class="rev-card-val">{total_waste:,.2f} <span class="rev-card-unit">MT</span></div>
                <div class="rev-card-trend-row">
                    <span class="trend-pill neutral">{waste_share_pct:.1f}% Global Share</span>
                    <span class="rev-card-caption">National reported</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Average Recycling Efficiency
    with kpi_cols[1]:
        rec_pill_cls = "positive" if rec_delta >= 0 else "alert"
        rec_sign = "+" if rec_delta >= 0 else ""
        st.markdown(
            f"""
            <div class="rev-card rev-card-glow-emerald">
                <div class="rev-card-top">
                    <span class="rev-card-label">Recycling Margin</span>
                    <div class="rev-card-icon-badge">♻️</div>
                </div>
                <div class="rev-card-val">{avg_recycling:.2f}<span class="rev-card-unit">%</span></div>
                <div class="rev-card-trend-row">
                    <span class="trend-pill {rec_pill_cls}">{rec_sign}{rec_delta:.1f}% vs BM</span>
                    <span class="rev-card-caption">Mean efficiency</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Circular Economy Material Valuation ($M USD)
    with kpi_cols[2]:
        st.markdown(
            f"""
            <div class="rev-card rev-card-glow-cyan">
                <div class="rev-card-top">
                    <span class="rev-card-label">Circular Valuation</span>
                    <div class="rev-card-icon-badge">💎</div>
                </div>
                <div class="rev-card-val">${total_market_value:,.1f} <span class="rev-card-unit">M</span></div>
                <div class="rev-card-trend-row">
                    <span class="trend-pill positive">Recoverable Asset</span>
                    <span class="rev-card-caption">@ $850/MT polymer</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Critical Coastal Leakage Risk
    with kpi_cols[3]:
        risk_pill_cls = "alert" if risk_pct > 30 else "warning"
        st.markdown(
            f"""
            <div class="rev-card rev-card-glow-rose">
                <div class="rev-card-top">
                    <span class="rev-card-label">Coastal Risk Exposure</span>
                    <div class="rev-card-icon-badge">🚨</div>
                </div>
                <div class="rev-card-val">{high_risk_count:,} <span class="rev-card-unit">({risk_pct:.0f}%)</span></div>
                <div class="rev-card-trend-row">
                    <span class="trend-pill {risk_pill_cls}">High & Critical</span>
                    <span class="rev-card-caption">Vulnerable nations</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5. Per-Capita Waste Index
    with kpi_cols[4]:
        st.markdown(
            f"""
            <div class="rev-card rev-card-glow-amber">
                <div class="rev-card-top">
                    <span class="rev-card-label">Per-Capita Index</span>
                    <div class="rev-card-icon-badge">👤</div>
                </div>
                <div class="rev-card-val">{avg_per_capita:,.1f} <span class="rev-card-unit">kg/person</span></div>
                <div class="rev-card-trend-row">
                    <span class="trend-pill neutral">{country_count}/{total_global_countries} Nations</span>
                    <span class="rev-card-caption">Unweighted mean</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# 8. AUTOMATED INSIGHTS GENERATOR (DRIBBBLE SMART CARDS)
# ==============================================================================
def render_dribbble_insights(df: pd.DataFrame, benchmark_df: pd.DataFrame) -> None:
    """Computes dynamic, data-driven analytical takeaways in sleek Dribbble cards."""
    if df.empty:
        return

    # 1. Largest Waste Producer
    top_waste_row = df.loc[df["Total_Plastic_Waste_MT"].idxmax()]
    total_waste_sum = df["Total_Plastic_Waste_MT"].sum()
    top_waste_share = (top_waste_row["Total_Plastic_Waste_MT"] / total_waste_sum * 100) if total_waste_sum > 0 else 0

    # 2. Highest Recycling Country
    top_rec_row = df.loc[df["Recycling_Rate"].idxmax()]

    # 3. Highest Per-Capita Waste
    top_per_cap_row = df.loc[df["Per_Capita_Waste_KG"].idxmax()]

    # 4. Most Common Waste Source
    source_counts = df["Main_Sources"].value_counts()
    dominant_source = source_counts.index[0] if not source_counts.empty else "N/A"
    dominant_source_count = source_counts.iloc[0] if not source_counts.empty else 0
    dominant_source_share = (dominant_source_count / len(df) * 100) if len(df) > 0 else 0

    cols = st.columns(4)

    with cols[0]:
        st.markdown(
            f"""
            <div class="insight-pill-card">
                <div class="insight-header">
                    <span class="insight-tag">Volume Anchor</span>
                    <span>📈</span>
                </div>
                <div class="insight-main">{top_waste_row['Country']} • {top_waste_row['Total_Plastic_Waste_MT']:,.2f} MT</div>
                <div class="insight-subtext">Drives {top_waste_share:.1f}% of current filtered waste footprint.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[1]:
        st.markdown(
            f"""
            <div class="insight-pill-card emerald">
                <div class="insight-header">
                    <span class="insight-tag">Efficiency Benchmark</span>
                    <span>🏆</span>
                </div>
                <div class="insight-main">{top_rec_row['Country']} • {top_rec_row['Recycling_Rate']:.1f}% Recycled</div>
                <div class="insight-subtext">Global benchmark average is {benchmark_df['Recycling_Rate'].mean():.1f}%.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[2]:
        st.markdown(
            f"""
            <div class="insight-pill-card amber">
                <div class="insight-header">
                    <span class="insight-tag">Peak Generation Density</span>
                    <span>⚡</span>
                </div>
                <div class="insight-main">{top_per_cap_row['Country']} • {top_per_cap_row['Per_Capita_Waste_KG']:,.1f} kg</div>
                <div class="insight-subtext">Global average is {benchmark_df['Per_Capita_Waste_KG'].mean():.1f} kg/person.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[3]:
        st.markdown(
            f"""
            <div class="insight-pill-card cyan">
                <div class="insight-header">
                    <span class="insight-tag">Dominant Stream</span>
                    <span>🏭</span>
                </div>
                <div class="insight-main">{dominant_source.replace('_', ' ')}</div>
                <div class="insight-subtext">Primary stream across {dominant_source_count} nations ({dominant_source_share:.1f}%).</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# 9. THE 7 CORE INTERACTIVE PLOTLY CHARTS (DRIBBBLE STYLED)
# ==============================================================================

# ------------------------------------------------------------------------------
# Chart 1: Top 10 countries by total plastic waste — horizontal bar chart
# ------------------------------------------------------------------------------
def render_top_waste_chart(df: pd.DataFrame, theme_mode: str) -> None:
    """Chart 1: Top 10 countries by total plastic waste — vibrant horizontal bar chart."""
    if df.empty:
        st.info("No data available for Top Waste chart with current parameters.")
        return

    top10 = df.nlargest(min(10, len(df)), "Total_Plastic_Waste_MT").copy()
    top10 = top10.sort_values("Total_Plastic_Waste_MT", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=top10["Total_Plastic_Waste_MT"],
            y=top10["Country"],
            orientation="h",
            marker=dict(
                color=top10["Total_Plastic_Waste_MT"],
                colorscale=[[0, "#4338CA"], [0.5, "#6366F1"], [1, "#8B5CF6"]],
                line=dict(color="#A5B4FC", width=1),
            ),
            text=[f"{val:,.2f} MT" for val in top10["Total_Plastic_Waste_MT"]],
            textposition="outside",
            customdata=top10[
                ["Total_Plastic_Waste_MT", "Recycling_Rate", "Per_Capita_Waste_KG", "Coastal_Waste_Risk", "Main_Sources"]
            ].to_numpy(),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Total Plastic Waste: <b>%{customdata[0]:,.2f} MT</b><br>"
                "Recycling Efficiency: %{customdata[1]:.1f}%<br>"
                "Per-Capita Generation: %{customdata[2]:,.1f} kg/person<br>"
                "Coastal Risk: %{customdata[3]}<br>"
                "Primary Stream: %{customdata[4]}<extra></extra>"
            ),
        )
    )

    fig.update_xaxes(title_text="Total Plastic Waste (MT)", rangemode="tozero")
    fig.update_yaxes(title_text="")
    apply_dribbble_chart_theme(
        fig,
        theme_mode=theme_mode,
        height=390,
        title="Top 10 Global Generators by Total Plastic Waste (MT)",
        show_legend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="chart_top_waste")


# ------------------------------------------------------------------------------
# Chart 2: Recycling rates by country — sorted bar chart
# ------------------------------------------------------------------------------
def render_recycling_rates_chart(df: pd.DataFrame, theme_mode: str) -> None:
    """Chart 2: Recycling rates by country — sorted horizontal bar chart."""
    if df.empty:
        st.info("No data available for Recycling Rates chart.")
        return

    c1, c2 = st.columns([1.5, 1])
    with c1:
        sort_mode = st.radio(
            "Sort Direction",
            ["Highest Recycling First", "Lowest Recycling First"],
            horizontal=True,
            key="rec_sort_mode",
            label_visibility="collapsed",
        )
    with c2:
        view_limit = st.selectbox(
            "Scope",
            [15, 25, 50, "All Filtered Nations"],
            index=0,
            key="rec_view_limit",
            label_visibility="collapsed",
        )

    if isinstance(view_limit, int):
        if sort_mode == "Highest Recycling First":
            rec_data = df.nlargest(min(view_limit, len(df)), "Recycling_Rate").sort_values("Recycling_Rate", ascending=True)
        else:
            rec_data = df.nsmallest(min(view_limit, len(df)), "Recycling_Rate").sort_values("Recycling_Rate", ascending=False)
    else:
        rec_data = df.sort_values("Recycling_Rate", ascending=True if sort_mode == "Highest Recycling First" else False)

    fig = go.Figure(
        go.Bar(
            x=rec_data["Recycling_Rate"],
            y=rec_data["Country"],
            orientation="h",
            marker=dict(
                color=rec_data["Recycling_Rate"],
                colorscale=[[0, "#047857"], [0.5, "#10B981"], [1, "#34D399"]],
                line=dict(color="#6EE7B7", width=1),
            ),
            text=[f"{val:.1f}%" for val in rec_data["Recycling_Rate"]],
            textposition="outside",
            customdata=rec_data[
                ["Recycling_Rate", "Total_Plastic_Waste_MT", "Per_Capita_Waste_KG", "Coastal_Waste_Risk", "Main_Sources"]
            ].to_numpy(),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Recycling Margin: <b>%{customdata[0]:.1f}%</b><br>"
                "Total Plastic Waste: %{customdata[1]:,.2f} MT<br>"
                "Per-Capita Waste: %{customdata[2]:,.1f} kg/person<br>"
                "Coastal Risk: %{customdata[3]}<br>"
                "Primary Stream: %{customdata[4]}<extra></extra>"
            ),
        )
    )

    fig.update_xaxes(title_text="Recycling Rate (%)", range=[0, min(100, max(rec_data["Recycling_Rate"].max() * 1.15, 15))])
    fig.update_yaxes(title_text="")
    chart_h = max(390, min(800, len(rec_data) * 22 + 90))
    apply_dribbble_chart_theme(
        fig,
        theme_mode=theme_mode,
        height=chart_h,
        title="Recycling Performance & Circular Recovery Efficiency (%)",
        show_legend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="chart_recycling_rates")


# ------------------------------------------------------------------------------
# Chart 3: Per-capita plastic waste — horizontal bar chart
# ------------------------------------------------------------------------------
def render_per_capita_chart(df: pd.DataFrame, theme_mode: str) -> None:
    """Chart 3: Per-capita plastic waste — horizontal bar chart."""
    if df.empty:
        st.info("No data available for Per-Capita chart.")
        return

    top_per_capita = df.nlargest(min(10, len(df)), "Per_Capita_Waste_KG").copy()
    top_per_capita = top_per_capita.sort_values("Per_Capita_Waste_KG", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=top_per_capita["Per_Capita_Waste_KG"],
            y=top_per_capita["Country"],
            orientation="h",
            marker=dict(
                color=top_per_capita["Per_Capita_Waste_KG"],
                colorscale=[[0, "#C2410C"], [0.5, "#F97316"], [1, "#FDBA74"]],
                line=dict(color="#FED7AA", width=1),
            ),
            text=[f"{val:,.1f} kg" for val in top_per_capita["Per_Capita_Waste_KG"]],
            textposition="outside",
            customdata=top_per_capita[
                ["Per_Capita_Waste_KG", "Total_Plastic_Waste_MT", "Recycling_Rate", "Coastal_Waste_Risk", "Main_Sources"]
            ].to_numpy(),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Per-Capita Waste: <b>%{customdata[0]:,.1f} kg/person</b><br>"
                "Total Plastic Waste: %{customdata[1]:,.2f} MT<br>"
                "Recycling Margin: %{customdata[2]:.1f}%<br>"
                "Coastal Risk: %{customdata[3]}<br>"
                "Primary Stream: %{customdata[4]}<extra></extra>"
            ),
        )
    )

    fig.update_xaxes(title_text="Per-Capita Plastic Waste (kg/person)", rangemode="tozero")
    fig.update_yaxes(title_text="")
    apply_dribbble_chart_theme(
        fig,
        theme_mode=theme_mode,
        height=390,
        title="Top 10 Per-Capita Waste Footprints (kg/person)",
        show_legend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="chart_per_capita")


# ------------------------------------------------------------------------------
# Chart 4: Coastal waste risk distribution — donut chart
# ------------------------------------------------------------------------------
def render_coastal_risk_donut(df: pd.DataFrame, theme_mode: str) -> None:
    """Chart 4: Coastal waste risk distribution — Dribbble thick-cut donut chart."""
    if df.empty:
        st.info("No data available for Coastal Risk Donut.")
        return

    risk_counts = df["Coastal_Waste_Risk"].value_counts().reset_index()
    risk_counts.columns = ["Coastal_Waste_Risk", "Country_Count"]

    ordered_risks = [r for r in RISK_ORDER if r in risk_counts["Coastal_Waste_Risk"].tolist()]
    for r in risk_counts["Coastal_Waste_Risk"].tolist():
        if r not in ordered_risks:
            ordered_risks.append(r)

    risk_counts["order_idx"] = risk_counts["Coastal_Waste_Risk"].apply(
        lambda x: ordered_risks.index(x) if x in ordered_risks else 99
    )
    risk_counts = risk_counts.sort_values("order_idx").drop(columns=["order_idx"])
    risk_counts["Share_Pct"] = (risk_counts["Country_Count"] / risk_counts["Country_Count"].sum() * 100).round(1)

    # Collect sample countries for tooltips
    sample_countries = {}
    for risk in risk_counts["Coastal_Waste_Risk"]:
        c_list = df[df["Coastal_Waste_Risk"] == risk]["Country"].head(6).tolist()
        suffix = ", ..." if len(df[df["Coastal_Waste_Risk"] == risk]) > 6 else ""
        sample_countries[risk] = ", ".join(c_list) + suffix

    risk_counts["Sample_Countries"] = risk_counts["Coastal_Waste_Risk"].map(sample_countries)
    colors = [RISK_COLORS.get(r, "#94A3B8") for r in risk_counts["Coastal_Waste_Risk"]]

    is_dark = theme_mode == "dark"

    fig = go.Figure(
        go.Pie(
            labels=risk_counts["Coastal_Waste_Risk"],
            values=risk_counts["Country_Count"],
            hole=0.64,
            marker=dict(colors=colors, line=dict(color="#0B0F19" if is_dark else "#FFFFFF", width=3)),
            textinfo="label+percent",
            textfont=dict(size=11, color="#FFFFFF" if is_dark else "#0F172A", family="Plus Jakarta Sans"),
            sort=False,
            customdata=risk_counts[["Share_Pct", "Sample_Countries"]].to_numpy(),
            hovertemplate=(
                "<b>%{label} Risk</b><br>"
                "Country Count: <b>%{value}</b><br>"
                "Share: <b>%{customdata[0]}%</b><br>"
                "Nations: %{customdata[1]}<extra></extra>"
            ),
        )
    )

    # Center callout
    fig.update_layout(
        annotations=[
            dict(
                text=f"<b style='font-size:22px;'>{len(df)}</b><br><span style='font-size:10px; color:#94A3B8;'>NATIONS</span>",
                x=0.5,
                y=0.5,
                font=dict(size=16, family="Plus Jakarta Sans", color="#FFFFFF" if is_dark else "#0F172A"),
                showarrow=False,
            )
        ]
    )

    apply_dribbble_chart_theme(
        fig,
        theme_mode=theme_mode,
        height=370,
        title="Coastal Waste Leakage Risk Breakdown",
        show_legend=True,
    )
    st.plotly_chart(fig, use_container_width=True, key="chart_coastal_risk")


# ------------------------------------------------------------------------------
# Chart 5: Main plastic waste sources — bar chart
# ------------------------------------------------------------------------------
def render_main_sources_chart(df: pd.DataFrame, theme_mode: str) -> None:
    """Chart 5: Main plastic waste sources — bar chart counting country records."""
    if df.empty:
        st.info("No data available for Waste Sources chart.")
        return

    source_counts = df["Main_Sources"].value_counts().reset_index()
    source_counts.columns = ["Main_Sources", "Country_Count"]
    source_counts = source_counts.sort_values("Country_Count", ascending=True)
    source_counts["Display_Label"] = source_counts["Main_Sources"].str.replace("_", " ")
    source_counts["Share_Pct"] = (source_counts["Country_Count"] / len(df) * 100).round(1)

    fig = go.Figure(
        go.Bar(
            x=source_counts["Country_Count"],
            y=source_counts["Display_Label"],
            orientation="h",
            marker=dict(
                color=source_counts["Country_Count"],
                colorscale=[[0, "#0E7490"], [0.5, "#06B6D4"], [1, "#67E8F9"]],
                line=dict(color="#A5F3FC", width=1),
            ),
            text=[f"{val:,}" for val in source_counts["Country_Count"]],
            textposition="outside",
            customdata=source_counts[["Main_Sources", "Share_Pct"]].to_numpy(),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Nations: <b>%{x}</b><br>"
                "Selection Proportion: <b>%{customdata[1]}%</b><extra></extra>"
            ),
        )
    )

    fig.update_xaxes(title_text="Number of Countries", rangemode="tozero")
    fig.update_yaxes(title_text="")
    apply_dribbble_chart_theme(
        fig,
        theme_mode=theme_mode,
        height=370,
        title="Primary Waste Streams by Sector (Country Count)",
        show_legend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="chart_main_sources")


# ------------------------------------------------------------------------------
# Chart 6: Total plastic waste versus recycling rate — scatter plot
# ------------------------------------------------------------------------------
def render_waste_vs_recycling_scatter(df: pd.DataFrame, theme_mode: str) -> None:
    """Chart 6: Total plastic waste versus recycling rate — scatter plot colored by coastal risk."""
    if df.empty:
        st.info("No data available for Waste vs Recycling scatter plot.")
        return

    c1, c2 = st.columns([3, 1])
    with c2:
        use_log_scale = st.checkbox(
            "Log Scale (Waste MT)",
            value=False,
            help="Logarithmic scale for high dynamic range waste visual.",
            key="scatter_log_scale",
        )

    scatter_df = df.copy()

    fig = px.scatter(
        scatter_df,
        x="Total_Plastic_Waste_MT",
        y="Recycling_Rate",
        size="Per_Capita_Waste_KG",
        size_max=32,
        color="Coastal_Waste_Risk",
        color_discrete_map=RISK_COLORS,
        category_orders={"Coastal_Waste_Risk": RISK_ORDER},
        custom_data=["Country", "Total_Plastic_Waste_MT", "Recycling_Rate", "Per_Capita_Waste_KG", "Main_Sources", "Coastal_Waste_Risk"],
    )

    fig.update_traces(
        marker=dict(opacity=0.85, line=dict(width=1.2, color="#FFFFFF")),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Total Plastic Waste: <b>%{customdata[1]:,.2f} MT</b><br>"
            "Recycling Margin: <b>%{customdata[2]:.1f}%</b><br>"
            "Per-Capita Waste: <b>%{customdata[3]:,.1f} kg/person</b><br>"
            "Coastal Risk: <b>%{customdata[5]}</b><br>"
            "Stream: %{customdata[4]}<extra></extra>"
        ),
    )

    fig.update_xaxes(
        title_text="Total Plastic Waste (MT)" + (" [Log Scale]" if use_log_scale else ""),
        type="log" if use_log_scale else "linear",
    )
    fig.update_yaxes(title_text="Recycling Rate (%)", range=[0, min(100, max(scatter_df["Recycling_Rate"].max() * 1.1, 15))])

    apply_dribbble_chart_theme(
        fig,
        theme_mode=theme_mode,
        height=440,
        title="Waste Volume vs Recycling Efficiency (Bubble Size = Per-Capita kg)",
        show_legend=True,
    )
    st.plotly_chart(fig, use_container_width=True, key="chart_scatter")


# ------------------------------------------------------------------------------
# Chart 7: Country comparison — compare selected countries across metrics
# ------------------------------------------------------------------------------
def render_country_comparison(df: pd.DataFrame, benchmark_df: pd.DataFrame, theme_mode: str) -> None:
    """
    Chart 7: Country comparison across total waste, recycling rate, and per-capita waste.
    Separates incompatible units onto independent subplots with dedicated axes.
    """
    st.markdown(
        """
        <div class="dribbble-section-title">
            <h3><span>⚔️</span> Head-to-Head Country Benchmark Matrix</h3>
            <span class="section-tag">Multi-metric comparative</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_avail_countries = sorted(df["Country"].unique().tolist())
    if len(all_avail_countries) < 2:
        st.info("At least two countries must be available in the active dataset to execute comparative analysis.")
        return

    default_selection = [c for c in ["China", "United States", "Germany", "India"] if c in all_avail_countries]
    if len(default_selection) < 2:
        default_selection = all_avail_countries[: min(3, len(all_avail_countries))]

    selected = st.multiselect(
        "Select Benchmark Cohort (2 to 8 Nations)",
        options=all_avail_countries,
        default=default_selection,
        key="comp_multiselect",
        help="Select countries to contrast across volume, recovery, and density.",
    )

    if len(selected) < 2:
        st.warning("Please choose at least 2 countries to populate benchmark comparative charts.")
        return

    comp_df = df[df["Country"].isin(selected)].copy()

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "Total Plastic Waste (MT)",
            "Recycling Margin (%)",
            "Per-Capita Waste (kg/person)",
        ),
        horizontal_spacing=0.09,
    )

    # Subplot 1: Total Waste
    fig.add_trace(
        go.Bar(
            x=comp_df["Country"],
            y=comp_df["Total_Plastic_Waste_MT"],
            name="Total Waste (MT)",
            marker=dict(
                color="#6366F1",
                line=dict(color="#A5B4FC", width=1),
            ),
            text=[f"{v:,.2f}" for v in comp_df["Total_Plastic_Waste_MT"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Total Waste: %{y:,.2f} MT<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # Subplot 2: Recycling Rate
    fig.add_trace(
        go.Bar(
            x=comp_df["Country"],
            y=comp_df["Recycling_Rate"],
            name="Recycling Rate (%)",
            marker=dict(
                color="#10B981",
                line=dict(color="#6EE7B7", width=1),
            ),
            text=[f"{v:.1f}%" for v in comp_df["Recycling_Rate"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Recycling Margin: %{y:.1f}%<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    # Subplot 3: Per-Capita Waste
    fig.add_trace(
        go.Bar(
            x=comp_df["Country"],
            y=comp_df["Per_Capita_Waste_KG"],
            name="Per-Capita (kg)",
            marker=dict(
                color="#F59E0B",
                line=dict(color="#FDE68A", width=1),
            ),
            text=[f"{v:,.1f}" for v in comp_df["Per_Capita_Waste_KG"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Per-Capita: %{y:,.1f} kg/person<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=3,
    )

    fig.update_yaxes(title_text="MT", rangemode="tozero", row=1, col=1)
    fig.update_yaxes(title_text="Percent (%)", rangemode="tozero", row=1, col=2)
    fig.update_yaxes(title_text="kg / person", rangemode="tozero", row=1, col=3)

    apply_dribbble_chart_theme(
        fig,
        theme_mode=theme_mode,
        height=380,
        title="Side-by-Side Performance Across Core Metrics",
        show_legend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="chart_multi_country_comp")

    # Detailed Comparison Table with Benchmark Comparison
    st.markdown("##### 📌 Variance Against Global Baseline Averages")
    bm_waste = benchmark_df["Total_Plastic_Waste_MT"].mean()
    bm_rec = benchmark_df["Recycling_Rate"].mean()
    bm_per_cap = benchmark_df["Per_Capita_Waste_KG"].mean()

    table_rows = []
    for _, row in comp_df.iterrows():
        table_rows.append(
            {
                "Country": row["Country"],
                "Total Waste (MT)": f"{row['Total_Plastic_Waste_MT']:,.2f}",
                "vs Global Baseline (1.72 MT)": f"{((row['Total_Plastic_Waste_MT'] - bm_waste) / bm_waste * 100):+.1f}%",
                "Recycling Margin (%)": f"{row['Recycling_Rate']:.1f}%",
                "vs Global Baseline (13.1%)": f"{(row['Recycling_Rate'] - bm_rec):+.1f} pts",
                "Per-Capita (kg)": f"{row['Per_Capita_Waste_KG']:,.1f}",
                "vs Global Baseline (122.3 kg)": f"{((row['Per_Capita_Waste_KG'] - bm_per_cap) / bm_per_cap * 100):+.1f}%",
                "Valuation ($M)": f"${row['Material_Valuation_USD_M']:,.2f}M",
                "Coastal Risk": row["Coastal_Waste_Risk"],
                "Primary Stream": row["Main_Sources"].replace("_", " "),
            }
        )

    summary_table_df = pd.DataFrame(table_rows)
    st.dataframe(summary_table_df, use_container_width=True, hide_index=True)

    # Download comparison CSV button
    comp_csv = comp_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Download Benchmark Cohort Data (CSV)",
        data=comp_csv,
        file_name="revenue_os_country_benchmark.csv",
        mime="text/csv",
        key="btn_download_comp",
    )


# ==============================================================================
# 10. COUNTRY DETAILS PROFILE PANEL (DRIBBBLE FINTECH DRAWER)
# ==============================================================================
def render_country_details(df: pd.DataFrame, benchmark_df: pd.DataFrame, theme_mode: str) -> None:
    """Renders a deep-dive country profile card styled like a Stripe/Mercury dashboard drawer."""
    st.markdown(
        """
        <div class="dribbble-section-title">
            <h3><span>🔍</span> Deep-Dive Country Dossier & Valuation</h3>
            <span class="section-tag">Entity level profiling</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    country_list = sorted(df["Country"].unique().tolist())
    if not country_list:
        st.info("No country records available.")
        return

    default_idx = 0
    if "United States" in country_list:
        default_idx = country_list.index("United States")
    elif "China" in country_list:
        default_idx = country_list.index("China")

    selected_country = st.selectbox(
        "Choose Entity to Inspect",
        options=country_list,
        index=default_idx,
        key="detail_country_select",
    )

    c_row = df[df["Country"] == selected_country].iloc[0]

    bm_waste_avg = benchmark_df["Total_Plastic_Waste_MT"].mean()
    bm_rec_avg = benchmark_df["Recycling_Rate"].mean()
    bm_per_cap_avg = benchmark_df["Per_Capita_Waste_KG"].mean()

    waste_diff_pct = ((c_row["Total_Plastic_Waste_MT"] - bm_waste_avg) / bm_waste_avg) * 100
    rec_diff_pts = c_row["Recycling_Rate"] - bm_rec_avg
    per_cap_diff_pct = ((c_row["Per_Capita_Waste_KG"] - bm_per_cap_avg) / bm_per_cap_avg) * 100
    risk_cls = c_row["Coastal_Waste_Risk"]

    t = THEMES[theme_mode]
    is_dark = theme_mode == "dark"

    st.markdown(
        f"""
        <div class="profile-hero">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem;">
                <div>
                    <div style="font-size:1.6rem; font-weight:800; color:{t['text_main']}; letter-spacing:-0.03em;">
                        📍 {c_row['Country']}
                    </div>
                    <div style="font-size:0.75rem; color:{t['text_muted']}; margin-top:0.15rem;">
                        National Material Flow & Circular Economy Intelligence
                    </div>
                </div>
                <div style="display:flex; gap:0.5rem; align-items:center;">
                    <span class="profile-badge-pill {risk_cls}">{risk_cls.replace('_', ' ')} Coastal Risk</span>
                    <span style="font-size:0.72rem; background:{'rgba(255,255,255,0.06)' if is_dark else '#F1F5F9'}; border:1px solid {t['card_border']}; padding:0.3rem 0.75rem; border-radius:9999px; font-weight:700; color:{t['text_main']};">
                        Sector: {c_row['Main_Sources'].replace('_', ' ')}
                    </span>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:1rem; margin-top:1.4rem;">
                <div style="background:{'rgba(255,255,255,0.03)' if is_dark else '#F8FAFC'}; border:1px solid {t['card_border']}; border-radius:14px; padding:1.05rem;">
                    <div style="font-size:0.7rem; font-weight:700; color:{t['text_muted']}; text-transform:uppercase; letter-spacing:0.08em;">Total Waste Volume</div>
                    <div style="font-size:1.45rem; font-weight:800; color:{t['text_main']}; margin-top:0.25rem;">{c_row['Total_Plastic_Waste_MT']:,.2f} MT</div>
                    <div style="font-size:0.72rem; color:{'#F43F5E' if waste_diff_pct > 0 else '#10B981'}; font-weight:700; margin-top:0.3rem;">
                        {waste_diff_pct:+.1f}% vs global mean ({bm_waste_avg:.2f} MT)
                    </div>
                </div>

                <div style="background:{'rgba(255,255,255,0.03)' if is_dark else '#F8FAFC'}; border:1px solid {t['card_border']}; border-radius:14px; padding:1.05rem;">
                    <div style="font-size:0.7rem; font-weight:700; color:{t['text_muted']}; text-transform:uppercase; letter-spacing:0.08em;">Recycling Efficiency</div>
                    <div style="font-size:1.45rem; font-weight:800; color:#10B981; margin-top:0.25rem;">{c_row['Recycling_Rate']:.1f}%</div>
                    <div style="font-size:0.72rem; color:{'#10B981' if rec_diff_pts > 0 else '#F43F5E'}; font-weight:700; margin-top:0.3rem;">
                        {rec_diff_pts:+.1f} pts vs global mean ({bm_rec_avg:.1f}%)
                    </div>
                </div>

                <div style="background:{'rgba(255,255,255,0.03)' if is_dark else '#F8FAFC'}; border:1px solid {t['card_border']}; border-radius:14px; padding:1.05rem;">
                    <div style="font-size:0.7rem; font-weight:700; color:{t['text_muted']}; text-transform:uppercase; letter-spacing:0.08em;">Per-Capita Intensity</div>
                    <div style="font-size:1.45rem; font-weight:800; color:#F59E0B; margin-top:0.25rem;">{c_row['Per_Capita_Waste_KG']:,.1f} kg</div>
                    <div style="font-size:0.72rem; color:{'#F43F5E' if per_cap_diff_pct > 0 else '#10B981'}; font-weight:700; margin-top:0.3rem;">
                        {per_cap_diff_pct:+.1f}% vs global mean ({bm_per_cap_avg:.1f} kg)
                    </div>
                </div>

                <div style="background:{'rgba(255,255,255,0.03)' if is_dark else '#F8FAFC'}; border:1px solid {t['card_border']}; border-radius:14px; padding:1.05rem;">
                    <div style="font-size:0.7rem; font-weight:700; color:{t['text_muted']}; text-transform:uppercase; letter-spacing:0.08em;">Circular Asset Value</div>
                    <div style="font-size:1.45rem; font-weight:800; color:#06B6D4; margin-top:0.25rem;">${c_row['Material_Valuation_USD_M']:,.2f} M</div>
                    <div style="font-size:0.72rem; color:{t['text_muted']}; font-weight:600; margin-top:0.3rem;">
                        Recovered polymer market opportunity
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 11. SEARCHABLE DATA TABLE & EXPORT (DRIBBBLE REVENUE LEDGER)
# ==============================================================================
def render_data_ledger(df: pd.DataFrame) -> None:
    """Renders the comprehensive searchable data ledger with CSV export."""
    st.markdown(
        """
        <div class="dribbble-section-title">
            <h3><span>📋</span> Global Financial & Material Waste Ledger</h3>
            <span class="section-tag">Authentic raw records</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2, 1.2, 0.8])
    with c1:
        tbl_query = st.text_input(
            "Filter ledger by country name",
            placeholder="Type country name to search...",
            key="tbl_search_input",
        ).strip()
    with c2:
        sort_col = st.selectbox(
            "Sort Ledger By",
            options=EXPECTED_COLUMNS + ["Material_Valuation_USD_M"],
            index=1,
            key="tbl_sort_col",
        )
    with c3:
        sort_order = st.selectbox(
            "Order",
            ["Descending", "Ascending"],
            index=0,
            key="tbl_sort_order",
        )

    tbl_data = df.copy()
    if tbl_query:
        tbl_data = tbl_data[tbl_data["Country"].str.contains(tbl_query, case=False, na=False)]

    ascending = True if sort_order == "Ascending" else False
    tbl_data = tbl_data.sort_values(by=sort_col, ascending=ascending)

    display_df = tbl_data.copy().rename(
        columns={
            "Country": "Country",
            "Total_Plastic_Waste_MT": "Total Waste (MT)",
            "Main_Sources": "Primary Sector",
            "Recycling_Rate": "Recycling Rate (%)",
            "Per_Capita_Waste_KG": "Per-Capita (kg)",
            "Coastal_Waste_Risk": "Coastal Leakage Risk",
            "Material_Valuation_USD_M": "Circular Valuation ($M USD)",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=380,
    )

    csv_bytes = tbl_data.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Download Filtered Ledger (CSV)",
        data=csv_bytes,
        file_name="revenue_os_plastic_waste_ledger.csv",
        mime="text/csv",
        key="btn_download_filtered",
    )


# ==============================================================================
# 12. MAIN APPLICATION ORCHESTRATION
# ==============================================================================
def main() -> None:
    # Load dataset
    df, meta = load_dataset(CSV_PATH)

    # Render Sidebar and extract filtered data + chosen theme
    filtered_df, filter_info, theme_mode = render_sidebar(df)

    # Apply Dribbble Revenue Theme CSS
    apply_dribbble_theme(theme_mode)

    # Handle missing or invalid dataset safely
    if meta["status"] != "success":
        st.markdown(
            f"""
            <div class="revenue-app-header" style="border-left: 5px solid #F43F5E;">
                <div class="nav-meta-row">
                    <span class="brand-badge" style="color:#FDA4AF; border-color:rgba(244,63,94,0.4);">
                        Dataset Error
                    </span>
                </div>
                <h1 class="app-title">Revenue.OS // Environmental Data Fault</h1>
                <p class="app-subtitle">A problem occurred while locating or reading the CSV file.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.error(f"⚠️ {meta['error']}")
        st.info(f"Expected CSV path: `{CSV_PATH}`")
        st.stop()

    # Dribbble Top Application Header
    st.markdown(
        f"""
        <div class="revenue-app-header">
            <div class="nav-meta-row">
                <div class="nav-meta-left">
                    <span class="brand-badge"><span class="live-dot"></span> REVENUE.OS // CIRCULAR INTELLIGENCE</span>
                    <span class="pill-chip">Workspace: Global Environmental</span>
                    <span class="pill-chip">Ledger: {meta['unique_countries']} Verified Nations</span>
                </div>
                <div class="nav-meta-right">
                    <span class="pill-chip">⚡ Mode: {theme_mode.upper()}</span>
                    <span class="pill-chip">Status: 100% Authentic CSV</span>
                </div>
            </div>
            <div class="header-main-row">
                <div class="header-title-box">
                    <h1 class="app-title"><span class="app-title-gradient">Global Revenue & Waste Intelligence</span></h1>
                    <p class="app-subtitle">
                        Comprehensive fintech-grade analytics on country-level plastic footprints, recycling margins, 
                        per-capita leakage, and circular economy asset valuation.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Ledger Source Status Banner
    st.markdown(
        f"""
        <div class="ledger-banner">
            <span>
                <b>Dataset Feed:</b> <code>{CSV_FILENAME}</code> &nbsp;|&nbsp; 
                Active Scope: <b>{len(filtered_df):,}</b> of <b>{len(df):,}</b> nations ({len(filtered_df)/len(df)*100:.1f}%) 
                matching current parameters.
            </span>
            <span style="font-size:0.72rem; font-family:'JetBrains Mono', monospace; color:#10B981;">
                ● DIRECT CALCULATION ENGINE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Five Hero Revenue Metric Cards Across Top
    render_revenue_kpi_cards(filtered_df, total_global_countries=len(df), benchmark_df=df)

    # Empty filter state safeguard
    if filtered_df.empty:
        st.warning(
            "⚠️ No country records match your active parameter selections. "
            "Please broaden your filter criteria in the left sidebar or click 'Reset All Parameters'."
        )
        return

    # 2. Key Automated Insights (Smart Dribbble Cards)
    st.markdown(
        """
        <div class="dribbble-section-title">
            <h3><span>💡</span> Autonomous Executive Takeaways</h3>
            <span class="section-tag">Computed Signals</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_dribbble_insights(filtered_df, benchmark_df=df)

    # 3. Dribbble Segmented Tabs for Clean SaaS Experience
    tabs = st.tabs([
        "⚡ Revenue & Waste Analytics",
        "📊 Efficiency & Volume Leaderboards",
        "⚔️ Benchmark Cohort Matrix",
        "🔍 Country Dossier",
        "📋 Ledger Explorer",
    ])

    # Tab 1: Core Visualizations
    with tabs[0]:
        st.markdown(
            """
            <div class="dribbble-section-title">
                <h3><span>📈</span> Macro Risk & Material Flow Analysis</h3>
                <span class="section-tag">Interactive visual suite</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        row1_c1, row1_c2 = st.columns([1, 1.25])
        with row1_c1:
            render_coastal_risk_donut(filtered_df, theme_mode)
        with row1_c2:
            render_main_sources_chart(filtered_df, theme_mode)

        render_waste_vs_recycling_scatter(filtered_df, theme_mode)

    # Tab 2: Leaderboards
    with tabs[1]:
        st.markdown(
            """
            <div class="dribbble-section-title">
                <h3><span>🏆</span> Global Generation & Recovery Rankings</h3>
                <span class="section-tag">Leaderboards</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        row3_c1, row3_c2 = st.columns([1, 1])
        with row3_c1:
            render_top_waste_chart(filtered_df, theme_mode)
        with row3_c2:
            render_per_capita_chart(filtered_df, theme_mode)

        render_recycling_rates_chart(filtered_df, theme_mode)

    # Tab 3: Multi-Country Benchmark Comparison
    with tabs[2]:
        render_country_comparison(filtered_df, benchmark_df=df, theme_mode=theme_mode)

    # Tab 4: Country Dossier
    with tabs[3]:
        render_country_details(filtered_df, benchmark_df=df, theme_mode=theme_mode)

    # Tab 5: Ledger Explorer & CSV Export
    with tabs[4]:
        render_data_ledger(filtered_df)

    # Footer
    st.markdown(
        """
        <div class="revenue-footer">
            <span class="revenue-footer-brand">Revenue.OS // Eco-Analytics Engine</span> &nbsp;•&nbsp; Inspired by Dribbble Revenue & SaaS Design Systems
            <br>
            <span style="font-size:0.72rem; color:#94A3B8; margin-top:0.3rem; display:inline-block;">
                Built with Python, Streamlit, Pandas & Plotly. Strictly derived from authentic country records.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
