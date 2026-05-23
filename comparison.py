import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_engine import run_clustering

def render():
    st.title("📈 Segment Comparison Panels")
    st.markdown("---")

    with st.spinner("Loading data..."):
        profile, sil, cluster_summary, txn, courses, X_scaled, labels = run_clustering()

    segments = sorted(profile["Segment"].unique().tolist())
    selected = st.multiselect("Select Segments to Compare", segments, default=segments)
    filtered = profile[profile["Segment"].isin(selected)]
    if filtered.empty:
        st.warning("Please select at least one segment.")
        return

    badge_colors = {
        "🎓 Deep Specialists":"#6c63ff","🌐 Broad Explorers":"#43b89c",
        "💼 Career-Oriented Learners":"#e07b39","🔰 Casual Beginners":"#5e9bdb",
    }
    agg = filtered.groupby("Segment").agg(
        Learners      =("UserID","count"),
        Avg_Courses   =("total_courses_enrolled","mean"),
        Avg_Diversity =("diversity_score","mean"),
        Avg_Depth     =("learning_depth_index","mean"),
        Avg_Spending  =("avg_spending","mean"),
        Avg_Rating    =("avg_course_rating","mean"),
        Paid_Ratio    =("paid_course_ratio","mean"),
    ).round(2).reset_index()

    st.markdown("---")
    st.subheader("📌 Key Metrics Comparison")
    cols = st.columns(len(selected)) if selected else []
    for i, seg in enumerate(selected):
        row = agg[agg["Segment"]==seg]
        if row.empty: continue
        row = row.iloc[0]
        c = badge_colors.get(seg,"#888")
        cols[i].markdown(f"""
        <div style="background:{c}18;border:2px solid {c};border-radius:12px;padding:1rem;text-align:center;">
        <div style="font-weight:700;color:{c};font-size:0.9rem;">{seg}</div>
        <div style="font-size:1.6rem;font-weight:800;">{int(row['Learners'])}</div>
        <div style="font-size:0.8rem;color:#555;">learners</div><hr style="border-color:{c}40;">
        <div>📚 {row['Avg_Courses']:.1f} courses</div>
        <div>🌐 {row['Avg_Diversity']:.1f} categories</div>
        <div>💰 ${row['Avg_Spending']:.1f} avg spend</div>
        <div>⭐ {row['Avg_Rating']:.2f} rating</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🕸️ Multi-Segment Radar Comparison")
    features = ["total_courses_enrolled","diversity_score","learning_depth_index","avg_course_rating","paid_course_ratio"]
    flabels  = ["Courses","Diversity","Depth","Avg Rating","Paid Ratio"]
    maxes    = profile[features].max()
    color_list = list(badge_colors.values())
    fig_radar = go.Figure()
    for i, seg in enumerate(selected):
        vals = [profile[profile["Segment"]==seg][f].mean()/maxes[f] for f in features]
        vals += [vals[0]]
        fig_radar.add_trace(go.Scatterpolar(r=vals, theta=flabels+[flabels[0]],
                            fill='toself', name=seg, line_color=color_list[i%len(color_list)], opacity=0.7))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,1])),
                             legend=dict(orientation="h",y=-0.2), margin=dict(t=30))
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 Avg Courses Enrolled")
        fig = px.bar(agg, x="Segment", y="Avg_Courses", color="Segment",
                     color_discrete_sequence=list(badge_colors.values()))
        fig.update_layout(showlegend=False, xaxis_tickangle=-20, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("💰 Avg Spending ($)")
        fig2 = px.bar(agg, x="Segment", y="Avg_Spending", color="Segment",
                      color_discrete_sequence=list(badge_colors.values()))
        fig2.update_layout(showlegend=False, xaxis_tickangle=-20, margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("🗂️ Preferred Category Heatmap")
    cat_dist = filtered.groupby(["Segment","preferred_category"])["UserID"].count().reset_index()
    cat_dist.columns = ["Segment","Category","Count"]
    pivot = cat_dist.pivot_table(index="Segment", columns="Category", values="Count", fill_value=0)
    fig3 = px.imshow(pivot, text_auto=True, color_continuous_scale="Blues", aspect="auto")
    fig3.update_layout(margin=dict(t=20))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Course Level Preference by Segment")
    lvl_txn = txn[["UserID","TransactionID","CourseID"]].merge(
        courses[["CourseID","CourseLevel"]], on="CourseID", how="left")
    lvl_txn = lvl_txn.merge(profile[["UserID","Segment"]], on="UserID", how="left")
    lvl_txn = lvl_txn[lvl_txn["Segment"].isin(selected)]
    lvl_dist = lvl_txn.groupby(["Segment","CourseLevel"])["TransactionID"].count().reset_index()
    lvl_dist.columns = ["Segment","Level","Count"]
    fig4 = px.bar(lvl_dist, x="Segment", y="Count", color="Level", barmode="group",
                  color_discrete_sequence=["#43b89c","#667eea","#f5576c"])
    fig4.update_layout(xaxis_tickangle=-20, margin=dict(t=10))
    st.plotly_chart(fig4, use_container_width=True)
