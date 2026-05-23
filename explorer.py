import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_engine import run_clustering

def render():
    st.title("🔍 Learner Profile Explorer")
    st.markdown("Deep-dive into any individual learner's behavior, segment, and learning history.")
    st.markdown("---")

    with st.spinner("Loading profiles..."):
        profile, sil, cluster_summary, txn, courses, X_scaled, labels = run_clustering()

    col_sel, col_info = st.columns([1,3])
    with col_sel:
        st.subheader("Select Learner")
        selected_user = st.selectbox("User ID", profile["UserID"].tolist())
        st.markdown("**Filter by Segment**")
        seg_filter = st.selectbox("Segment", ["All"] + profile["Segment"].unique().tolist())
        if seg_filter != "All":
            ids = profile[profile["Segment"]==seg_filter]["UserID"].tolist()
            selected_user = st.selectbox("Users in Segment", ids)

    user_data = profile[profile["UserID"]==selected_user].iloc[0]
    user_txn  = txn[txn["UserID"]==selected_user][["CourseID","Amount","TransactionDate"]].merge(courses, on="CourseID", how="left")

    badge_colors = {
        "🎓 Deep Specialists":"#6c63ff",
        "🌐 Broad Explorers":"#43b89c",
        "💼 Career-Oriented Learners":"#e07b39",
        "🔰 Casual Beginners":"#5e9bdb",
    }
    seg   = user_data["Segment"]
    color = badge_colors.get(seg,"#888")

    with col_info:
        st.subheader(f"Learner: {selected_user}")
        st.markdown(f'<span style="background:{color};color:white;padding:0.3rem 0.9rem;border-radius:20px;font-weight:700;">{seg}</span>', unsafe_allow_html=True)
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Age",    int(user_data["Age"]) if pd.notna(user_data["Age"]) else "N/A")
        m2.metric("Gender", user_data["Gender"] if pd.notna(user_data["Gender"]) else "N/A")
        m3.metric("Courses Enrolled", int(user_data["total_courses_enrolled"]))
        m4.metric("Avg Spending",     f"${user_data['avg_spending']:.1f}")
        m5,m6,m7,m8 = st.columns(4)
        m5.metric("Preferred Category", user_data["preferred_category"] if pd.notna(user_data["preferred_category"]) else "N/A")
        m6.metric("Preferred Level",    user_data["preferred_level"]    if pd.notna(user_data["preferred_level"])    else "N/A")
        m7.metric("Diversity Score",    int(user_data["diversity_score"]))
        m8.metric("Avg Rating",         f"{user_data['avg_course_rating']:.2f} ⭐")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📁 Enrollment by Category")
        if not user_txn.empty:
            cat_count = user_txn["CourseCategory"].value_counts().reset_index()
            cat_count.columns = ["Category","Count"]
            fig = px.bar(cat_count, x="Category", y="Count", color="Count", color_continuous_scale="Purples")
            fig.update_layout(margin=dict(t=10,b=10), xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("📈 Learning Level Breakdown")
        if not user_txn.empty:
            lvl_count = user_txn["CourseLevel"].value_counts().reset_index()
            lvl_count.columns = ["Level","Count"]
            fig2 = px.pie(lvl_count, names="Level", values="Count",
                          color_discrete_sequence=["#667eea","#f093fb","#f5576c"], hole=0.3)
            fig2.update_layout(margin=dict(t=10,b=10))
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Full Enrollment History")
    if not user_txn.empty:
        show = ["CourseID","CourseName","CourseCategory","CourseLevel","CourseRating","Amount","TransactionDate"]
        st.dataframe(user_txn[show].sort_values("TransactionDate", ascending=False)
                     .style.background_gradient(subset=["CourseRating"], cmap="Greens"),
                     use_container_width=True, hide_index=True)

    st.subheader("🕸️ Learner Feature Radar")
    if not user_txn.empty:
        features = ["total_courses_enrolled","diversity_score","learning_depth_index","avg_course_rating","paid_course_ratio"]
        labels_r  = ["Courses","Diversity","Depth","Rating","Paid Ratio"]
        maxes    = profile[features].max()
        user_vals = [user_data[f]/maxes[f] for f in features]
        seg_avg   = profile[profile["Segment"]==seg][features].mean()
        seg_vals  = [seg_avg[f]/maxes[f] for f in features]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatterpolar(r=user_vals+[user_vals[0]], theta=labels_r+[labels_r[0]], fill='toself', name='This Learner', line_color='#6c63ff'))
        fig3.add_trace(go.Scatterpolar(r=seg_vals+[seg_vals[0]],   theta=labels_r+[labels_r[0]], fill='toself', name='Segment Avg',  line_color='#f5576c', opacity=0.5))
        fig3.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,1])), margin=dict(t=30,b=30))
        st.plotly_chart(fig3, use_container_width=True)
