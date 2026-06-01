"""
Add Income page: form to create a new income entry.
"""

import streamlit as st
from datetime import date

from frontend.utils.api_client import create_income


def render_add_income():
    """Render the add income form."""

    st.markdown(
        """
        <h1 style="margin-bottom: 0.25rem;">
            <span class="gradient-text">Add Income</span>
        </h1>
        <p style="color: #9CA3AF; margin-top: 0;">Record a new income entry</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            <div style="
                background: rgba(16, 185, 129, 0.05);
                border: 1px solid rgba(16, 185, 129, 0.15);
                border-radius: 16px;
                padding: 1.5rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.5rem 0;">💰 Income Details</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("add_income_form", clear_on_submit=True):
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                step=100.00,
                format="%.2f",
                placeholder="Enter amount",
            )

            source = st.text_input(
                "Source",
                placeholder="e.g., Salary, Freelance, Dividends",
            )

            income_date = st.date_input("Date", value=date.today())

            submitted = st.form_submit_button(
                "💰 Add Income",
                use_container_width=True,
                type="primary",
            )

            if submitted:
                if amount <= 0:
                    st.error("Amount must be greater than zero")
                elif not source:
                    st.error("Please enter an income source")
                else:
                    result = create_income(
                        amount=amount,
                        source=source,
                        income_date=income_date,
                    )
                    if isinstance(result, dict) and result.get("error"):
                        st.error(f"❌ {result['detail']}")
                    else:
                        st.success(f"✅ Income of ₹{amount:,.2f} from **{source}** added!")
                        st.balloons()

    with col2:
        st.markdown(
            """
            <div style="
                background: rgba(16, 185, 129, 0.05);
                border: 1px solid rgba(16, 185, 129, 0.15);
                border-radius: 16px;
                padding: 1.5rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.5rem 0;">💡 Tips</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tips = [
            ("🏢", "Salary", "Record your monthly salary"),
            ("💻", "Freelance", "Track project-based income"),
            ("📈", "Investments", "Dividend and interest income"),
            ("🎁", "Gifts", "Money received as gifts"),
            ("🏠", "Rental", "Rental income from property"),
        ]

        for emoji, title, desc in tips:
            st.markdown(
                f"""
                <div style="
                    background: rgba(16, 185, 129, 0.08);
                    border-radius: 10px;
                    padding: 0.6rem 0.9rem;
                    margin-bottom: 0.5rem;
                ">
                    <span style="font-size: 1.1rem;">{emoji}</span>
                    <strong style="color: #10B981;"> {title}</strong>
                    <br/><span style="color: #9CA3AF; font-size: 0.8rem;">{desc}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
