"""
Dashboard page: monthly summary cards, pie chart, and bar chart.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, datetime

from frontend.utils.api_client import get_summary, get_expenses, get_incomes, get_budget_progress


# Color palette for charts
CHART_COLORS = [
    "#6C63FF", "#3B82F6", "#8B5CF6", "#EC4899", "#F59E0B",
    "#10B981", "#EF4444", "#06B6D4", "#F97316", "#84CC16",
]


def render_dashboard():
    """Render the dashboard page with summary cards and charts."""

    st.markdown(
        """
        <h1 style="margin-bottom: 0.25rem;">
            <span class="gradient-text">Dashboard</span>
        </h1>
        <p style="color: #9CA3AF; margin-top: 0;">Your financial overview at a glance</p>
        """,
        unsafe_allow_html=True,
    )

    # ─── Month Selector ──────────────────────────────────────────────────

    col_month, col_spacer = st.columns([1, 3])
    with col_month:
        today = date.today()
        selected_month = st.date_input(
            "Select Month",
            value=today.replace(day=1),
            key="dashboard_month",
        )
        month_str = selected_month.strftime("%Y-%m")

    st.markdown("---")

    # ─── Fetch Summary ────────────────────────────────────────────────────

    summary = get_summary(month_str)

    if isinstance(summary, dict) and summary.get("error"):
        st.error(f"Could not load summary: {summary.get('detail', 'Unknown error')}")
        return

    total_income = summary.get("total_income", 0)
    total_expenses = summary.get("total_expenses", 0)
    net_savings = summary.get("net_savings", 0)
    breakdown = summary.get("category_breakdown", [])

    # ─── Summary Cards ────────────────────────────────────────────────────

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="💰 Total Income",
            value=f"₹{total_income:,.2f}",
            delta=None,
        )
    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=f"₹{total_expenses:,.2f}",
            delta=None,
        )
    with col3:
        delta_color = "normal" if net_savings >= 0 else "inverse"
        st.metric(
            label="📈 Net Savings",
            value=f"₹{net_savings:,.2f}",
            delta=f"{'Surplus' if net_savings >= 0 else 'Deficit'}",
            delta_color=delta_color,
        )

    st.markdown("<br/>", unsafe_allow_html=True)

    # ─── Charts ───────────────────────────────────────────────────────────

    chart_col1, chart_col2 = st.columns(2)

    # Pie chart — expenses by category
    with chart_col1:
        st.markdown(
            """
            <div style="
                background: rgba(108, 99, 255, 0.05);
                border: 1px solid rgba(108, 99, 255, 0.12);
                border-radius: 16px;
                padding: 1rem 1.25rem 0.5rem 1.25rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.25rem 0;">Expenses by Category</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if breakdown:
            df_cat = pd.DataFrame(breakdown)
            fig_pie = px.pie(
                df_cat,
                values="total",
                names="category_name",
                color_discrete_sequence=CHART_COLORS,
                hole=0.45,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA", family="Inter"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11),
                ),
                margin=dict(t=20, b=40, l=20, r=20),
                height=350,
            )
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont_size=11,
                marker=dict(line=dict(color="#0E1117", width=2)),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses recorded this month")

    # Bar chart — income vs expenses comparison
    with chart_col2:
        st.markdown(
            """
            <div style="
                background: rgba(108, 99, 255, 0.05);
                border: 1px solid rgba(108, 99, 255, 0.12);
                border-radius: 16px;
                padding: 1rem 1.25rem 0.5rem 1.25rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.25rem 0;">Income vs Expenses</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Build a 6-month comparison
        months_data = []
        current = selected_month
        for i in range(6):
            m = current.month - i
            y = current.year
            if m <= 0:
                m += 12
                y -= 1
            m_str = f"{y}-{m:02d}"
            m_summary = get_summary(m_str)
            if isinstance(m_summary, dict) and not m_summary.get("error"):
                months_data.append({
                    "Month": datetime(y, m, 1).strftime("%b %Y"),
                    "Income": m_summary.get("total_income", 0),
                    "Expenses": m_summary.get("total_expenses", 0),
                    "sort_key": f"{y}-{m:02d}",
                })

        if months_data:
            months_data.sort(key=lambda x: x["sort_key"])
            df_months = pd.DataFrame(months_data)

            fig_bar = go.Figure()
            fig_bar.add_trace(
                go.Bar(
                    name="Income",
                    x=df_months["Month"],
                    y=df_months["Income"],
                    marker_color="#10B981",
                    marker=dict(
                        line=dict(width=0),
                        cornerradius=6,
                    ),
                )
            )
            fig_bar.add_trace(
                go.Bar(
                    name="Expenses",
                    x=df_months["Month"],
                    y=df_months["Expenses"],
                    marker_color="#EF4444",
                    marker=dict(
                        line=dict(width=0),
                        cornerradius=6,
                    ),
                )
            )
            fig_bar.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA", family="Inter"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                ),
                margin=dict(t=20, b=40, l=60, r=20),
                height=350,
                xaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
                yaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data available for comparison")

    # ─── Category Breakdown Table ─────────────────────────────────────────

    if breakdown:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="
                background: rgba(108, 99, 255, 0.05);
                border: 1px solid rgba(108, 99, 255, 0.12);
                border-radius: 16px;
                padding: 1rem 1.25rem 0.5rem 1.25rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.25rem 0;">Category Breakdown</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        df_table = pd.DataFrame(breakdown)
        df_table.columns = ["Category", "Amount (₹)", "Percentage (%)"]
        df_table["Amount (₹)"] = df_table["Amount (₹)"].apply(lambda x: f"₹{x:,.2f}")
        df_table["Percentage (%)"] = df_table["Percentage (%)"].apply(lambda x: f"{x:.1f}%")
        df_table.index = range(1, len(df_table) + 1)
        st.dataframe(df_table, use_container_width=True, hide_index=False)

    # ─── Budget Progress Section ──────────────────────────────────────────

    progress_data = get_budget_progress(month_str)
    if isinstance(progress_data, list) and len(progress_data) > 0:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="
                background: rgba(108, 99, 255, 0.05);
                border: 1px solid rgba(108, 99, 255, 0.12);
                border-radius: 16px;
                padding: 1rem 1.25rem 0.5rem 1.25rem;
                margin-bottom: 1rem;
            ">
                <h4 style="color: #FAFAFA; margin: 0 0 0.25rem 0;">🎯 Monthly Budget Limits Progress</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for p in progress_data:
            spent = p["amount_spent"]
            limit = p["budget_limit"]
            percentage = p["percentage_used"]
            cat_name = p["category_name"]

            # Determine color and text alerts
            if percentage <= 80:
                bar_color = "linear-gradient(90deg, #10B981 0%, #059669 100%)"
                badge_html = f"<span style='color: #10B981; font-weight: 600; font-size: 0.85rem;'>✅ Safe ({percentage:.1f}%)</span>"
            elif percentage <= 100:
                bar_color = "linear-gradient(90deg, #F59E0B 0%, #D97706 100%)"
                badge_html = f"<span style='color: #F59E0B; font-weight: 600; font-size: 0.85rem;'>⚠️ Approaching Limit ({percentage:.1f}%)</span>"
            else:
                bar_color = "linear-gradient(90deg, #EF4444 0%, #DC2626 100%)"
                over_amt = spent - limit
                badge_html = f"<span style='background: rgba(239, 68, 68, 0.15); color: #EF4444; font-weight: 700; font-size: 0.85rem; padding: 2px 8px; border-radius: 8px;'>🚨 Exceeded by ₹{over_amt:,.2f} ({percentage:.1f}%)</span>"

            percentage_clamped = min(percentage, 100.0)

            st.markdown(
                f"""
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="font-weight: 600; color: #FAFAFA;">{cat_name}</span>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <span style="color: #9CA3AF; font-size: 0.9rem;">₹{spent:,.2f} of ₹{limit:,.2f}</span>
                            {badge_html}
                        </div>
                    </div>
                    <div style="width: 100%; background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; height: 10px; overflow: hidden;">
                        <div style="width: {percentage_clamped}%; background: {bar_color}; height: 100%; border-radius: 8px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
