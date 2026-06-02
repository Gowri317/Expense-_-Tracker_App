"""
Budgets page: form to set category-wise budget limits and view current configurations.
"""

import streamlit as st
from datetime import date

from frontend.utils.api_client import get_categories, get_budgets, set_budget, delete_budget


def render_budgets():
    """Render the budgets configuration page."""

    st.markdown(
        """
        <h1 style="margin-bottom: 0.25rem;">
            <span class="gradient-text">Category Budgets</span>
        </h1>
        <p style="color: #9CA3AF; margin-top: 0;">Set monthly spending limits for each category to stay on track</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Fetch all categories
    categories = get_categories()
    if isinstance(categories, dict) and categories.get("error"):
        st.error(f"Could not load categories: {categories.get('detail', 'Unknown error')}")
        return

    # ─── Month Selector ──────────────────────────────────────────────────

    col_month, col_spacer = st.columns([1, 3])
    with col_month:
        today = date.today()
        selected_month = st.date_input(
            "Select Month",
            value=today.replace(day=1),
            key="budgets_month_selector",
        )
        month_str = selected_month.strftime("%Y-%m")

    # ─── Fetch Existing Budgets ─────────────────────────────────────────

    budgets = get_budgets(month_str)
    if isinstance(budgets, dict) and budgets.get("error"):
        st.error(f"Could not load budgets: {budgets.get('detail', 'Unknown error')}")
        budgets = []

    st.markdown("---")

    col_form, col_list = st.columns([1, 1.5])

    # ─── Set Budget Form ─────────────────────────────────────────────────

    with col_form:
        st.markdown(
            """
            <div style="
                background: rgba(108, 99, 255, 0.05);
                border: 1px solid rgba(108, 99, 255, 0.12);
                border-radius: 16px;
                padding: 1.5rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.5rem 0;">🎯 Set Budget Limit</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("set_budget_form", clear_on_submit=True):
            # Select category
            cat_names = [c["name"] for c in categories]
            cat_map = {c["name"]: c["id"] for c in categories}
            selected_cat = st.selectbox("Category", cat_names)

            # Enter budget amount
            amount = st.number_input(
                "Monthly Limit (₹)",
                min_value=1.0,
                step=500.0,
                format="%.2f",
                placeholder="e.g. 5000",
            )

            submitted = st.form_submit_button(
                "🎯 Set Budget",
                use_container_width=True,
                type="primary",
            )

            if submitted:
                if amount <= 0:
                    st.error("Amount must be greater than zero")
                elif not selected_cat:
                    st.error("Please select a category")
                else:
                    result = set_budget(
                        category_id=cat_map[selected_cat],
                        amount=amount,
                        month=month_str,
                    )
                    if isinstance(result, dict) and result.get("error"):
                        st.error(f"❌ {result['detail']}")
                    else:
                        st.success(f"✅ Budget of ₹{amount:,.2f} set for **{selected_cat}** in {month_str}!")
                        st.rerun()

    # ─── Configured Budgets List ─────────────────────────────────────────

    with col_list:
        st.markdown(
            """
            <div style="
                background: rgba(108, 99, 255, 0.05);
                border: 1px solid rgba(108, 99, 255, 0.12);
                border-radius: 16px;
                padding: 1.5rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.5rem 0;">📋 Configured Budgets for {month_str}</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not budgets:
            st.info(f"No budgets configured yet for {month_str}.")
        else:
            # Table headers
            st.markdown(
                """
                <div style="
                    display: grid;
                    grid-template-columns: 2fr 2fr 1fr;
                    font-weight: 600;
                    color: #9CA3AF;
                    padding-bottom: 0.5rem;
                    border-bottom: 1px solid rgba(108, 99, 255, 0.15);
                    margin-bottom: 0.5rem;
                ">
                    <div>Category</div>
                    <div>Budget Limit</div>
                    <div style="text-align: right;">Action</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for idx, budget in enumerate(budgets):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**{budget.get('category_name', 'Unknown')}**")
                with col2:
                    st.markdown(f"₹{budget['amount']:,.2f}")
                with col3:
                    if st.button("🗑️", key=f"del_bud_{budget['id']}_{idx}", use_container_width=True, help="Remove Budget"):
                        result = delete_budget(budget["id"])
                        if isinstance(result, dict) and result.get("error"):
                            st.error(f"❌ {result['detail']}")
                        else:
                            st.success("Budget limit deleted!")
                            st.rerun()

                st.markdown(
                    "<hr style='margin: 0.3rem 0; border-color: rgba(108,99,255,0.08);'/>",
                    unsafe_allow_html=True,
                )
