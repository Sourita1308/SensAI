"""
utils/ui_styles.py
SensAI — Multimodal Accessibility AI System
Modern UI Design System & Reusable Component Library

Provides:
- Google Fonts injection (Plus Jakarta Sans, Inter, Outfit)
- Dark Space / Light Daylight Glassmorphism theme with neon accent gradients
- Dynamic Dark/Light Theme Switcher tokens
- Micro-animations, responsive layout utilities, and styled Streamlit overrides
- Reusable HTML/CSS component renderers for hero banners, metric cards, and result boxes
"""

import streamlit as st
from typing import Optional


def get_custom_css(theme: str = "dark") -> str:
    """
    Returns the complete CSS stylesheet for SensAI's modern Glassmorphic theme.
    Supports both "dark" (Dark Space) and "light" (Daylight Studio) themes.
    Inject via st.markdown(get_custom_css(theme), unsafe_allow_html=True).
    """
    if theme == "light":
        tokens = """
        --bg-main: #f8fafc;
        --bg-card: rgba(255, 255, 255, 0.85);
        --bg-card-hover: rgba(255, 255, 255, 0.96);
        --border-glass: rgba(15, 23, 42, 0.12);
        --border-highlight: rgba(99, 102, 241, 0.65);
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --accent-indigo: #6366f1;
        --accent-violet: #8b5cf6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        --glow-indigo: 0 8px 24px rgba(99, 102, 241, 0.2);
        --glow-cyan: 0 8px 24px rgba(6, 182, 212, 0.2);
        --sidebar-bg: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
        --hero-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.94) 0%, rgba(241, 245, 249, 0.98) 100%);
        --hero-title-grad: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        --result-bg: rgba(255, 255, 255, 0.95);
        --metric-bg: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
        --chip-bg: rgba(15, 23, 42, 0.06);
        --chip-border: rgba(15, 23, 42, 0.15);
        --chip-text: #1e293b;
        --tab-list-bg: rgba(226, 232, 240, 0.85);
        --sidebar-label-bg: rgba(15, 23, 42, 0.05);
        --bar-empty: rgba(15, 23, 42, 0.12);
        --card-inner-bg: rgba(241, 245, 249, 0.7);
        """
    else:
        tokens = """
        --bg-main: #090b14;
        --bg-card: rgba(22, 28, 48, 0.68);
        --bg-card-hover: rgba(30, 38, 64, 0.78);
        --border-glass: rgba(255, 255, 255, 0.09);
        --border-highlight: rgba(99, 102, 241, 0.45);
        --text-primary: #ffffff;
        --text-secondary: #a8b3cf;
        --text-muted: #6b7280;
        --accent-indigo: #6366f1;
        --accent-violet: #8b5cf6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        --glow-indigo: 0 0 20px rgba(99, 102, 241, 0.25);
        --glow-cyan: 0 0 20px rgba(6, 182, 212, 0.25);
        --sidebar-bg: linear-gradient(180deg, #0b0e1b 0%, #0e1223 100%);
        --hero-bg: linear-gradient(135deg, rgba(30, 30, 64, 0.85) 0%, rgba(18, 20, 38, 0.95) 100%);
        --hero-title-grad: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        --result-bg: rgba(13, 17, 30, 0.85);
        --metric-bg: linear-gradient(145deg, rgba(22, 28, 48, 0.8) 0%, rgba(16, 20, 36, 0.9) 100%);
        --chip-bg: rgba(255, 255, 255, 0.06);
        --chip-border: rgba(255, 255, 255, 0.12);
        --chip-text: #e2e8f0;
        --tab-list-bg: rgba(14, 18, 32, 0.6);
        --sidebar-label-bg: rgba(255, 255, 255, 0.03);
        --bar-empty: rgba(255, 255, 255, 0.1);
        --card-inner-bg: rgba(15, 23, 42, 0.4);
        """

    return f"""
<style>
    /* ── 1. Google Fonts Import ────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* ── 2. Global CSS Variables & Theme Tokens ────────────────────────── */
    :root {{
        {tokens}
    }}

    /* ── 3. Base Streamlit Overrides & Typography ───────────────────────── */
    html, body, [class*="css"], .stApp, div[data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif !important;
        background: var(--bg-main) !important;
        color: var(--text-primary) !important;
        transition: background 0.35s ease, color 0.35s ease;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: var(--text-primary) !important;
    }}

    /* Text elements inherit theme text color */
    .stMarkdown p, .stMarkdown li, .stRadio label, .stSlider label, .stFileUploader label, .stSelectbox label, .stToggle label, .stCheckbox label {{
        color: var(--text-primary) !important;
    }}
    .stCaption, .stMarkdown small {{
        color: var(--text-secondary) !important;
    }}

    /* Hide default Streamlit decoration top header */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Main Container Padding Adjustment */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }}

    /* ── 4. Custom Scrollbars ───────────────────────────────────────────── */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-main);
    }}
    ::-webkit-scrollbar-thumb {{
        background: rgba(99, 102, 241, 0.3);
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(99, 102, 241, 0.6);
    }}

    /* ── 5. Sidebar Styling ─────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-glass) !important;
    }}
    
    section[data-testid="stSidebar"] .stRadio label {{
        background: var(--sidebar-label-bg);
        color: var(--text-primary) !important;
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 6px;
        border: 1px solid transparent;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }}
    section[data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.35);
        transform: translateX(4px);
    }}

    /* ── 6. Glassmorphism Card System ───────────────────────────────────── */
    .glass-card {{
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.22);
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        color: var(--text-primary);
    }}
    .glass-card:hover {{
        border-color: var(--border-highlight);
        box-shadow: var(--glow-indigo);
    }}

    .hero-banner {{
        background: var(--hero-bg);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35), 0 0 30px rgba(99, 102, 241, 0.15);
        position: relative;
        overflow: hidden;
    }}
    .hero-banner::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: var(--accent-gradient);
    }}

    /* ── 7. Neon Accent Badges & Status Pills ───────────────────────────── */
    .badge-gradient {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #c4c6ff;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}

    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #10b981;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }}
    .status-pill.inactive {{
        background: rgba(239, 68, 68, 0.12);
        border-color: rgba(239, 68, 68, 0.4);
        color: #ef4444;
    }}
    .status-pill.info {{
        background: rgba(6, 182, 212, 0.12);
        border-color: rgba(6, 182, 212, 0.4);
        color: #06b6d4;
    }}

    .pulse-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
        animation: pulse 1.8s infinite;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.95); opacity: 0.7; }}
        50% {{ transform: scale(1.35); opacity: 1; }}
        100% {{ transform: scale(0.95); opacity: 0.7; }}
    }}

    /* ── 8. Result Display Box & Metric Cards ────────────────────────────── */
    .result-box-modern {{
        background: var(--result-bg);
        border: 1px solid var(--border-glass);
        border-left: 4px solid var(--accent-indigo);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        font-size: 1.15rem;
        line-height: 1.6;
        color: var(--text-primary);
        margin: 1rem 0;
        min-height: 75px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }}
    
    .metric-card-modern {{
        background: var(--metric-bg);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 1.1rem;
        text-align: center;
        transition: all 0.3s ease;
    }}
    .metric-card-modern:hover {{
        border-color: var(--accent-indigo);
        box-shadow: var(--glow-indigo);
        transform: translateY(-2px);
    }}
    .metric-label {{
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.95rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
    }}

    /* ── 9. Interactive Chip Bar ────────────────────────────────────────── */
    .chip-bar {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 0.8rem 0;
    }}
    .chip {{
        background: var(--chip-bg);
        border: 1px solid var(--chip-border);
        border-radius: 8px;
        padding: 5px 12px;
        font-size: 0.88rem;
        color: var(--chip-text);
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    .chip:hover {{
        background: rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-1px);
    }}

    /* ── 10. Styled Streamlit Buttons & Tabs ────────────────────────────── */
    .stButton > button {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.25rem !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.35) 0%, rgba(139, 92, 246, 0.35) 100%) !important;
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 18px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-2px) !important;
    }}

    /* Tabs Override */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        background: var(--tab-list-bg);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid var(--border-glass);
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 42px;
        border-radius: 10px !important;
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0 18px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    }}
</style>
"""


def render_hero_header(
    title: str = "SensAI",
    subtitle: str = "Multimodal Accessibility AI Studio",
    badge_text: str = "v3.2 AI MULTIMODAL",
    is_live: bool = True
) -> None:
    """
    Renders the modern glassmorphic hero header with neon gradient badge and live status pills.
    """
    status_html = '<span class="status-pill"><span class="pulse-dot"></span> LIVE ENGINE READY</span>' if is_live else '<span class="status-pill inactive">STANDBY</span>'

    html_str = f"""<div class="hero-banner">
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
<div>
<div style="margin-bottom: 0.75rem;">
<span class="badge-gradient">♿ {badge_text}</span>
</div>
<h1 style="font-size: 2.6rem; margin: 0; background: var(--hero-title-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{title}</h1>
<p style="margin: 0.4rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem; font-weight: 400;">{subtitle}</p>
</div>
<div style="display: flex; gap: 0.75rem; align-items: center;">
{status_html}
<span class="status-pill info">🌐 EN • BN</span>
</div>
</div>
</div>"""

    st.markdown(html_str, unsafe_allow_html=True)


def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: str = "⚡"
) -> None:
    """
    Renders an animated metric stat card.
    """
    delta_html = f'<div style="font-size:0.78rem; color:#10b981; margin-top:4px;">▲ {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card-modern">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_result_box(
    text: str,
    title: str = "Recognized Output",
    icon: str = "✨",
    subtext: str = ""
) -> None:
    """
    Renders an elegant glassmorphic output box with title and typography.
    """
    sub_html = f'<div style="font-size: 0.85rem; color: var(--text-secondary); margin-top:0.5rem;">{subtext}</div>' if subtext else ""
    st.markdown(f"""
    <div style="margin-bottom: 0.5rem; font-weight: 600; color: var(--text-secondary); font-size: 0.95rem;">
        {icon} {title}
    </div>
    <div class="result-box-modern">
        {text}
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_pill(text: str, status_type: str = "active") -> str:
    """
    Returns an HTML string for an inline status pill badge.
    """
    pill_class = "status-pill"
    if status_type == "inactive":
        pill_class += " inactive"
    elif status_type == "info":
        pill_class += " info"
    return f'<span class="{pill_class}">{text}</span>'


def render_feature_card(title: str, description: str, icon: str = "🤖") -> None:
    """
    Renders a glassmorphic feature explanation card.
    """
    st.markdown(f"""
    <div class="glass-card" style="margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <h4 style="margin: 0; color: var(--text-primary); font-size: 1.15rem;">{title}</h4>
        </div>
        <p style="margin: 0; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.5;">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)
