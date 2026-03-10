import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Cyber Awareness During Conflict",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_risks():
    return pd.read_csv("data/risk_data.csv")

@st.cache_data
def load_controls():
    return pd.read_csv("data/control_data.csv")

risks = load_risks()
controls = load_controls()

st.title("🛡️ Cyber Awareness During Conflict")
st.caption("Interactive public-awareness dashboard for phishing, fake alerts, misinformation, and practical defensive actions.")

with st.sidebar:
    st.header("Filters")
    risk_levels = st.multiselect(
        "Risk level",
        options=sorted(risks["Risk Level"].unique().tolist()),
        default=sorted(risks["Risk Level"].unique().tolist())
    )
    audiences = st.multiselect(
        "Audience",
        options=sorted(risks["Audience"].unique().tolist()),
        default=sorted(risks["Audience"].unique().tolist())
    )
    categories = st.multiselect(
        "Category",
        options=sorted(risks["Category"].unique().tolist()),
        default=sorted(risks["Category"].unique().tolist())
    )
    st.markdown("---")
    st.subheader("Quick checklist")
    st.checkbox("Verify alerts through official channels", value=True, disabled=True)
    st.checkbox("Enable MFA on key accounts", value=True, disabled=True)
    st.checkbox("Avoid urgent links", value=True, disabled=True)
    st.checkbox("Update phone and apps", value=True, disabled=True)
    st.checkbox("Pause before forwarding suspicious content", value=True, disabled=True)

filtered = risks[
    risks["Risk Level"].isin(risk_levels)
    & risks["Audience"].isin(audiences)
    & risks["Category"].isin(categories)
].copy()

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Risk Explorer", "Recommendations", "About"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Visible Risk Areas", len(filtered))
    c2.metric("Avg. Public Impact", f'{filtered["Impact Score"].mean():.1f}/10' if len(filtered) else "0/10")
    c3.metric("High Risks", int((filtered["Risk Level"] == "High").sum()))
    c4.metric("Top Control Value", f'{controls["Practical Value"].max()}/10')

    st.markdown("### Public Cyber Risk Snapshot")
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        if len(filtered):
            bar = px.bar(
                filtered.sort_values("Impact Score", ascending=False),
                x="Risk Name",
                y="Impact Score",
                color="Risk Level",
                hover_data=["Why It Matters", "Recommendation"],
                title="Risk Areas by Relative Public Impact",
            )
            bar.update_layout(xaxis_title="", yaxis_title="Impact Score")
            st.plotly_chart(bar, use_container_width=True)
        else:
            st.info("No data matches the selected filters.")

    with col_b:
        donut_df = filtered.groupby("Risk Level", as_index=False).size()
        if len(donut_df):
            donut = px.pie(
                donut_df,
                names="Risk Level",
                values="size",
                hole=0.55,
                title="Risk Level Distribution",
            )
            st.plotly_chart(donut, use_container_width=True)
        else:
            st.info("No risk levels to display.")

    st.markdown("### Priority Messages for the Public")
    for _, row in filtered.sort_values(["Impact Score", "Risk Name"], ascending=[False, True]).head(5).iterrows():
        with st.container(border=True):
            st.subheader(f'{row["Risk Name"]} · {row["Impact Score"]}/10')
            st.write(row["Why It Matters"])
            st.markdown(f'**Recommendation:** {row["Recommendation"]}')

with tab2:
    st.markdown("### Explore Risk Details")
    st.dataframe(
        filtered[
            ["Risk Name", "Category", "Risk Level", "Audience", "Impact Score", "Why It Matters", "Recommendation"]
        ].sort_values(["Impact Score", "Risk Name"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )

    left, right = st.columns(2)

    with left:
        heat_df = filtered.pivot_table(
            index="Audience",
            columns="Category",
            values="Impact Score",
            aggfunc="mean"
        )
        if not heat_df.empty:
            heat = go.Figure(
                data=go.Heatmap(
                    z=heat_df.values,
                    x=heat_df.columns,
                    y=heat_df.index,
                    text=heat_df.round(1).values,
                    texttemplate="%{text}",
                    hoverongaps=False,
                )
            )
            heat.update_layout(title="Average Impact by Audience and Category")
            st.plotly_chart(heat, use_container_width=True)
        else:
            st.info("No heatmap available for the selected filters.")

    with right:
        scat = px.scatter(
            filtered,
            x="Likelihood Score",
            y="Impact Score",
            size="Impact Score",
            color="Risk Level",
            hover_name="Risk Name",
            title="Likelihood vs. Impact",
        )
        scat.update_layout(xaxis_title="Likelihood Score", yaxis_title="Impact Score")
        st.plotly_chart(scat, use_container_width=True)

with tab3:
    st.markdown("### Most Effective Public Defensive Actions")
    controls_sorted = controls.sort_values("Practical Value", ascending=False)
    control_chart = px.bar(
        controls_sorted,
        x="Control",
        y="Practical Value",
        color="Priority",
        hover_data=["Why It Helps"],
        title="Recommended Controls by Practical Value",
    )
    control_chart.update_layout(xaxis_title="", yaxis_title="Practical Value")
    st.plotly_chart(control_chart, use_container_width=True)

    st.markdown("### Action Cards")
    cols = st.columns(2)
    for idx, (_, row) in enumerate(controls_sorted.iterrows()):
        with cols[idx % 2]:
            with st.container(border=True):
                st.subheader(row["Control"])
                st.write(row["Why It Helps"])
                st.markdown(f'**Priority:** {row["Priority"]}')
                st.progress(int(row["Practical Value"] * 10))

    st.markdown("### Copy-ready public guidance")
    guidance = """1. Verify emergency-style messages through official channels only.
2. Do not enter passwords after clicking message links.
3. Turn on MFA for email, banking, and social accounts.
4. Keep phones, browsers, and messaging apps updated.
5. Pause before forwarding crisis-related content."""
    st.code(guidance, language="markdown")

with tab4:
    st.markdown("### What this project is")
    st.write(
        "This is a defensive, awareness-first dashboard. It is designed for public cyber education, "
        "portfolio use, classroom demonstration, and LinkedIn presentation."
    )

    st.markdown("### What this project is not")
    st.write(
        "It does not include target enumeration, live system scanning, exploitation steps, or operational guidance."
    )

    st.markdown("### Suggested use")
    st.write(
        "Use this dashboard alongside the PDF report, charts, and LinkedIn post as a portfolio-ready mini project."
    )

    st.markdown("### Export note")
    st.info("For screenshots: run the dashboard locally, maximize the browser window, and capture each tab for LinkedIn or GitHub.")
