"""
Add Expense page: form to create a new expense entry.
"""

import streamlit as st
from datetime import date

from frontend.utils.api_client import get_categories, create_expense, create_category


def render_add_expense():
    """Render the add expense form."""

    st.markdown(
        """
        <h1 style="margin-bottom: 0.25rem;">
            <span class="gradient-text">Add Expense</span>
        </h1>
        <p style="color: #9CA3AF; margin-top: 0;">Record a new expense</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Fetch categories
    categories = get_categories()
    if isinstance(categories, dict) and categories.get("error"):
        st.error(f"Could not load categories: {categories.get('detail', 'Unknown error')}")
        return

    # ─── Expense Form ─────────────────────────────────────────────────────

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            <div style="
                background: rgba(108, 99, 255, 0.05);
                border: 1px solid rgba(108, 99, 255, 0.12);
                border-radius: 16px;
                padding: 1.5rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.5rem 0;">💸 Expense Details</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("add_expense_form", clear_on_submit=True):
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                step=0.50,
                format="%.2f",
                placeholder="Enter amount",
            )

            # Category dropdown
            cat_names = [c["name"] for c in categories]
            cat_map = {c["name"]: c["id"] for c in categories}
            selected_cat = st.selectbox("Category", cat_names)

            expense_date = st.date_input("Date", value=date.today())

            note = st.text_area(
                "Note (optional)",
                placeholder="What was this expense for?",
                max_chars=500,
                height=100,
            )

            submitted = st.form_submit_button(
                "💸 Add Expense",
                use_container_width=True,
                type="primary",
            )

            if submitted:
                if amount <= 0:
                    st.error("Amount must be greater than zero")
                elif not selected_cat:
                    st.error("Please select a category")
                else:
                    result = create_expense(
                        amount=amount,
                        category_id=cat_map[selected_cat],
                        expense_date=expense_date,
                        note=note,
                    )
                    if isinstance(result, dict) and result.get("error"):
                        st.error(f"❌ {result['detail']}")
                    else:
                        st.success(f"✅ Expense of ₹{amount:,.2f} added to **{selected_cat}**!")
                        st.balloons()

    # ─── Add Custom Category ──────────────────────────────────────────────

    with col2:
        st.markdown(
            """
            <div style="
                background: rgba(108, 99, 255, 0.05);
                border: 1px solid rgba(108, 99, 255, 0.12);
                border-radius: 16px;
                padding: 1.5rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.5rem 0;">🏷️ Custom Category</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("add_category_form", clear_on_submit=True):
            new_cat_name = st.text_input(
                "Category Name",
                placeholder="e.g., Groceries, Gym",
            )
            cat_submitted = st.form_submit_button(
                "➕ Add Category",
                use_container_width=True,
            )

            if cat_submitted:
                if not new_cat_name:
                    st.error("Category name is required")
                else:
                    result = create_category(new_cat_name)
                    if isinstance(result, dict) and result.get("error"):
                        st.error(f"❌ {result['detail']}")
                    else:
                        st.success(f"✅ Category **{new_cat_name}** created!")
                        st.rerun()

        # Show existing categories
        st.markdown("##### Available Categories")
        for cat in categories:
            badge_color = "#6C63FF" if cat.get("user_id") else "#3B82F6"
            label = "Custom" if cat.get("user_id") else "Default"
            st.markdown(
                f"""
                <div style="
                    display: inline-block;
                    background: rgba(108, 99, 255, 0.1);
                    border: 1px solid {badge_color}40;
                    border-radius: 20px;
                    padding: 4px 12px;
                    margin: 2px 4px;
                    font-size: 0.85rem;
                    color: {badge_color};
                ">{cat['name']}</div>
                """,
                unsafe_allow_html=True,
            )
