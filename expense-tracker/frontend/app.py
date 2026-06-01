"""
Expense Tracker — Streamlit Frontend
Main entry point with navigation, authentication, and page routing.
"""

import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.utils.auth import init_session_state, is_authenticated, show_auth_page, do_logout

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Global font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0E1117 0%, #1A1D29 100%);
        border-right: 1px solid rgba(108, 99, 255, 0.15);
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.1) 0%, rgba(59, 130, 246, 0.08) 100%);
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(108, 99, 255, 0.15);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
    }

    /* Form inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border-color: rgba(108, 99, 255, 0.3) !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #6C63FF !important;
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Success/Error messages */
    .stAlert {
        border-radius: 10px;
    }

    /* Divider */
    hr {
        border-color: rgba(108, 99, 255, 0.15) !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Card container */
    .card {
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.08) 0%, rgba(59, 130, 246, 0.05) 100%);
        border: 1px solid rgba(108, 99, 255, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #6C63FF 0%, #3B82F6 50%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# ─── Initialize Session State ────────────────────────────────────────────────

init_session_state()

# ─── Auth Gate ────────────────────────────────────────────────────────────────

if not is_authenticated():
    show_auth_page()
    st.stop()

# ─── Sidebar Navigation ──────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; padding: 1rem 0;">
            <h2 class="gradient-text" style="margin: 0; font-size: 1.5rem;">💰 Expense Tracker</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # User info
    st.markdown(
        f"""
        <div style="
            background: rgba(108, 99, 255, 0.1);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
        ">
            <span style="color: #9CA3AF; font-size: 0.85rem;">Logged in as</span><br/>
            <span style="color: #FAFAFA; font-weight: 600;">👤 {st.session_state.username}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation
    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "💸 Add Expense", "💰 Add Income", "🎯 Budgets", "📜 History"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    if st.button("🚪 Logout", use_container_width=True):
        do_logout()
        st.rerun()

    st.markdown(
        """
        <div style="text-align: center; padding-top: 2rem; color: #4B5563; font-size: 0.75rem;">
            v1.0.0 • Built with ❤️
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Page Router ──────────────────────────────────────────────────────────────

if page == "📊 Dashboard":
    from frontend.pages.dashboard import render_dashboard
    render_dashboard()
elif page == "💸 Add Expense":
    from frontend.pages.add_expense import render_add_expense
    render_add_expense()
elif page == "💰 Add Income":
    from frontend.pages.add_income import render_add_income
    render_add_income()
elif page == "🎯 Budgets":
    from frontend.pages.budgets import render_budgets
    render_budgets()
elif page == "📜 History":
    from frontend.pages.history import render_history
    render_history()
