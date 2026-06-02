"""
History page: tabbed view of expenses and income with filtering, editing, and deletion.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta

from frontend.utils.api_client import (
    get_expenses,
    get_incomes,
    get_categories,
    update_expense,
    delete_expense,
    update_income,
    delete_income,
)


def render_history():
    """Render the history page with filterable tables and edit/delete actions."""

    st.markdown(
        """
        <h1 style="margin-bottom: 0.25rem;">
            <span class="gradient-text">Transaction History</span>
        </h1>
        <p style="color: #9CA3AF; margin-top: 0;">View, filter, edit, and delete your transactions</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ─── Filters ──────────────────────────────────────────────────────────

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        date_range = st.date_input(
            "Date Range",
            value=(date.today() - timedelta(days=30), date.today()),
            key="history_date_range",
        )
    with filter_col2:
        categories = get_categories()
        cat_options = ["All Categories"]
        cat_map = {}
        if isinstance(categories, list):
            cat_options += [c["name"] for c in categories]
            cat_map = {c["name"]: c["id"] for c in categories}
        selected_cat = st.selectbox("Category Filter", cat_options, key="history_cat_filter")

    with filter_col3:
        st.markdown("<br/>", unsafe_allow_html=True)
        refresh = st.button("🔄 Refresh", use_container_width=True)

    # Parse date range
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = date_range
        end_date = date.today()

    category_filter = cat_map.get(selected_cat) if selected_cat != "All Categories" else None

    st.markdown("---")

    # ─── Tabs ─────────────────────────────────────────────────────────────

    tab_expenses, tab_income = st.tabs(["💸 Expenses", "💰 Income"])

    # ─── Expenses Tab ─────────────────────────────────────────────────────

    with tab_expenses:
        expenses = get_expenses(
            start_date=start_date,
            end_date=end_date,
            category_id=category_filter,
        )

        if isinstance(expenses, dict) and expenses.get("error"):
            st.error(f"Could not load expenses: {expenses.get('detail', 'Unknown error')}")
        elif not expenses:
            st.info("No expenses found for the selected period")
        else:
            # Summary stats
            total = sum(e["amount"] for e in expenses)
            st.markdown(
                f"""
                <div style="
                    background: rgba(239, 68, 68, 0.08);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    border-radius: 12px;
                    padding: 0.75rem 1.25rem;
                    margin-bottom: 1rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span style="color: #9CA3AF;">
                        Showing <strong style="color: #FAFAFA;">{len(expenses)}</strong> expenses
                    </span>
                    <span style="color: #EF4444; font-weight: 700; font-size: 1.1rem;">
                        Total: ₹{total:,.2f}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Display each expense as a card with edit/delete
            for idx, expense in enumerate(expenses):
                with st.container():
                    cols = st.columns([1, 2, 2, 3, 1, 1])

                    with cols[0]:
                        st.markdown(f"**₹{expense['amount']:,.2f}**")
                    with cols[1]:
                        cat_name = expense.get("category_name", "Unknown")
                        st.markdown(
                            f"<span style='background: rgba(108,99,255,0.15); padding: 2px 10px; "
                            f"border-radius: 12px; font-size: 0.85rem; color: #6C63FF;'>"
                            f"{cat_name}</span>",
                            unsafe_allow_html=True,
                        )
                    with cols[2]:
                        st.markdown(f"📅 {expense['date']}")
                    with cols[3]:
                        note = expense.get("note", "")
                        st.markdown(f"<span style='color: #9CA3AF;'>{note or '—'}</span>", unsafe_allow_html=True)
                    with cols[4]:
                        if st.button("✏️", key=f"edit_exp_{expense['id']}_{idx}", help="Edit"):
                            st.session_state[f"editing_expense_{expense['id']}"] = True
                    with cols[5]:
                        if st.button("🗑️", key=f"del_exp_{expense['id']}_{idx}", help="Delete"):
                            result = delete_expense(expense["id"])
                            if isinstance(result, dict) and result.get("error"):
                                st.error(f"❌ {result['detail']}")
                            else:
                                st.success("Expense deleted!")
                                st.rerun()

                    # Inline edit form
                    if st.session_state.get(f"editing_expense_{expense['id']}", False):
                        with st.form(f"edit_expense_form_{expense['id']}"):
                            st.markdown("##### Edit Expense")
                            edit_cols = st.columns(3)
                            with edit_cols[0]:
                                new_amount = st.number_input(
                                    "Amount",
                                    value=float(expense["amount"]),
                                    min_value=0.01,
                                    key=f"edit_amt_{expense['id']}",
                                )
                            with edit_cols[1]:
                                if isinstance(categories, list):
                                    cat_names_list = [c["name"] for c in categories]
                                    current_cat_idx = 0
                                    for i, c in enumerate(categories):
                                        if c["id"] == expense["category_id"]:
                                            current_cat_idx = i
                                            break
                                    new_cat = st.selectbox(
                                        "Category",
                                        cat_names_list,
                                        index=current_cat_idx,
                                        key=f"edit_cat_{expense['id']}",
                                    )
                                else:
                                    new_cat = None
                            with edit_cols[2]:
                                new_note = st.text_input(
                                    "Note",
                                    value=expense.get("note", ""),
                                    key=f"edit_note_{expense['id']}",
                                )

                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Save", use_container_width=True, type="primary"):
                                    update_data = {"amount": new_amount, "note": new_note}
                                    if new_cat and isinstance(categories, list):
                                        for c in categories:
                                            if c["name"] == new_cat:
                                                update_data["category_id"] = c["id"]
                                                break
                                    result = update_expense(expense["id"], **update_data)
                                    if isinstance(result, dict) and result.get("error"):
                                        st.error(f"❌ {result['detail']}")
                                    else:
                                        st.success("Expense updated!")
                                        del st.session_state[f"editing_expense_{expense['id']}"]
                                        st.rerun()
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel", use_container_width=True):
                                    del st.session_state[f"editing_expense_{expense['id']}"]
                                    st.rerun()

                    st.markdown(
                        "<hr style='margin: 0.3rem 0; border-color: rgba(108,99,255,0.08);'/>",
                        unsafe_allow_html=True,
                    )

    # ─── Income Tab ───────────────────────────────────────────────────────

    with tab_income:
        incomes = get_incomes(start_date=start_date, end_date=end_date)

        if isinstance(incomes, dict) and incomes.get("error"):
            st.error(f"Could not load income: {incomes.get('detail', 'Unknown error')}")
        elif not incomes:
            st.info("No income entries found for the selected period")
        else:
            # Summary stats
            total = sum(i["amount"] for i in incomes)
            st.markdown(
                f"""
                <div style="
                    background: rgba(16, 185, 129, 0.08);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    border-radius: 12px;
                    padding: 0.75rem 1.25rem;
                    margin-bottom: 1rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span style="color: #9CA3AF;">
                        Showing <strong style="color: #FAFAFA;">{len(incomes)}</strong> income entries
                    </span>
                    <span style="color: #10B981; font-weight: 700; font-size: 1.1rem;">
                        Total: ₹{total:,.2f}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Display each income entry
            for idx, income in enumerate(incomes):
                with st.container():
                    cols = st.columns([1, 2, 2, 1, 1])

                    with cols[0]:
                        st.markdown(f"**₹{income['amount']:,.2f}**")
                    with cols[1]:
                        st.markdown(
                            f"<span style='background: rgba(16,185,129,0.15); padding: 2px 10px; "
                            f"border-radius: 12px; font-size: 0.85rem; color: #10B981;'>"
                            f"{income['source']}</span>",
                            unsafe_allow_html=True,
                        )
                    with cols[2]:
                        st.markdown(f"📅 {income['date']}")
                    with cols[3]:
                        if st.button("✏️", key=f"edit_inc_{income['id']}_{idx}", help="Edit"):
                            st.session_state[f"editing_income_{income['id']}"] = True
                    with cols[4]:
                        if st.button("🗑️", key=f"del_inc_{income['id']}_{idx}", help="Delete"):
                            result = delete_income(income["id"])
                            if isinstance(result, dict) and result.get("error"):
                                st.error(f"❌ {result['detail']}")
                            else:
                                st.success("Income deleted!")
                                st.rerun()

                    # Inline edit form
                    if st.session_state.get(f"editing_income_{income['id']}", False):
                        with st.form(f"edit_income_form_{income['id']}"):
                            st.markdown("##### Edit Income")
                            edit_cols = st.columns(2)
                            with edit_cols[0]:
                                new_amount = st.number_input(
                                    "Amount",
                                    value=float(income["amount"]),
                                    min_value=0.01,
                                    key=f"edit_inc_amt_{income['id']}",
                                )
                            with edit_cols[1]:
                                new_source = st.text_input(
                                    "Source",
                                    value=income["source"],
                                    key=f"edit_inc_src_{income['id']}",
                                )

                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Save", use_container_width=True, type="primary"):
                                    result = update_income(
                                        income["id"],
                                        amount=new_amount,
                                        source=new_source,
                                    )
                                    if isinstance(result, dict) and result.get("error"):
                                        st.error(f"❌ {result['detail']}")
                                    else:
                                        st.success("Income updated!")
                                        del st.session_state[f"editing_income_{income['id']}"]
                                        st.rerun()
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel", use_container_width=True):
                                    del st.session_state[f"editing_income_{income['id']}"]
                                    st.rerun()

                    st.markdown(
                        "<hr style='margin: 0.3rem 0; border-color: rgba(16,185,129,0.08);'/>",
                        unsafe_allow_html=True,
                    )
