"""
Auth utilities: login/register forms and session state management.
"""

import streamlit as st
import httpx
import os
import time
from frontend.utils.api_client import login, register, BACKEND_URL


def wake_backend():
    """Ping the backend to wake it up if it's sleeping (Render free tier)."""
    if st.session_state.get("_backend_awake"):
        return True
    
    with st.spinner("⏳ Waking up the server (free tier may take up to 60 seconds)..."):
        for attempt in range(6):  # Try 6 times, ~60 seconds total
            try:
                with httpx.Client(timeout=15) as client:
                    resp = client.get(f"{BACKEND_URL}/health")
                    if resp.status_code == 200:
                        st.session_state._backend_awake = True
                        return True
            except Exception:
                pass
            if attempt < 5:
                time.sleep(10)
    
    return False


def init_session_state():
    """Initialize authentication session state keys."""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False


def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return st.session_state.get("logged_in", False) and st.session_state.get("token") is not None


def do_logout():
    """Clear session state to log out."""
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.logged_in = False


def show_auth_page():
    """
    Render the login/register page with a tabbed interface.
    Returns True if user just authenticated successfully.
    """
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <h1 style="
                background: linear-gradient(135deg, #6C63FF 0%, #3B82F6 50%, #8B5CF6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                font-weight: 800;
                letter-spacing: -0.02em;
            ">💰 Expense Tracker</h1>
            <p style="color: #9CA3AF; font-size: 1.1rem; margin-top: -0.5rem;">
                Take control of your finances
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Wake up backend if sleeping (Render free tier)
    if not wake_backend():
        st.error("⚠️ Server is currently unavailable. Please wait a moment and refresh the page.")
        st.info("💡 On the free plan, the server may take up to 60 seconds to wake up. Try refreshing in a minute.")
        return False

    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### Welcome back!")
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

            if submitted:
                if not username or not password:
                    st.error("Please fill in all fields")
                    return False
                result = login(username, password)
                if isinstance(result, dict) and result.get("error"):
                    st.error(f"❌ {result['detail']}")
                    return False
                else:
                    st.session_state.token = result["access_token"]
                    st.session_state.username = username
                    st.session_state.logged_in = True
                    st.success("✅ Login successful!")
                    st.rerun()
                    return True

    with tab_register:
        with st.form("register_form", clear_on_submit=True):
            st.markdown("#### Create your account")
            new_username = st.text_input("Username", key="reg_username", placeholder="Choose a username (min 3 chars)")
            new_password = st.text_input("Password", type="password", key="reg_password", placeholder="Choose a password (min 6 chars)")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Confirm your password")
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted:
                if not new_username or not new_password:
                    st.error("Please fill in all fields")
                    return False
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    return False
                if len(new_username) < 3:
                    st.error("Username must be at least 3 characters")
                    return False
                if len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                    return False

                result = register(new_username, new_password)
                if isinstance(result, dict) and result.get("error"):
                    st.error(f"❌ {result['detail']}")
                    return False
                else:
                    st.success("✅ Account created! Please login.")
                    return False

    return False
