import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data_engine import run_clustering, load_data

def render():
    st.title("🎓 EduPro Student Intelligence Platform")
    st.markdown("### Personalized Learning · Data-Driven Segmentation · Adaptive Recommendations")
    st.markdown("---")

    with st.spinner("Loading data..."):
        profile, sil, cluster_summary, txn, courses, X_scaled, labels = run_clustering()
        users, _, _ = load_data()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("👥 Total Learners",   f"{len(users):,}")
    c2.metric("📚 Total Courses",    f"{len(courses):,}")
    c3.metric("🔁 Transactions",     f"{len(txn):,}")
    c4.metric("🧩 Segments Found",   f"{profile['Segment'].nunique()}")
    c5.metric("📐 Silhouette Score", f"{sil:.3f}")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Learner Segment Distribution")
        seg = profile["Segment"].value_counts().reset_index()
        seg.columns = ["Segment","Count"]
        fig = px.pie(seg, names="Segment", values="Count",
                     color_discrete_sequence=px.colors.qualitative.Bold, hole=0.4)
        fig.update_layout(showlegend=False, margin=dict(t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📚 Course Category Distribution")
        cat = courses["CourseCategory"].value_counts().reset_index()
        cat.columns = ["Category","Count"]
        fig2 = px.bar(cat, x="Count", y="Category", orientation="h",
                      color="Count", color_continuous_scale="Viridis")
        fig2.update_layout(margin=dict(t=10,b=10), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 Segment Behavioral Overview")
    agg = profile.groupby("Segment").agg(
        Learners      =("UserID","count"),
        Avg_Courses   =("total_courses_enrolled","mean"),
        Avg_Diversity =("diversity_score","mean"),
        Avg_Spending  =("avg_spending","mean"),
        Avg_Depth     =("learning_depth_index","mean"),
        Avg_Rating    =("avg_course_rating","mean"),
    ).round(2).reset_index()
    st.dataframe(agg.style.background_gradient(subset=["Avg_Courses","Avg_Diversity","Avg_Spending"], cmap="Blues"),
                 use_container_width=True, hide_index=True)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📅 Enrollments Over Time")
        t2 = txn.copy()
        t2["Month"] = pd.to_datetime(t2["TransactionDate"]).dt.to_period("M").dt.to_timestamp()
        monthly = t2.groupby("Month")["TransactionID"].count().reset_index()
        monthly.columns = ["Month","Enrollments"]
        fig3 = px.area(monthly, x="Month", y="Enrollments", color_discrete_sequence=["#667eea"])
        fig3.update_layout(margin=dict(t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("💰 Revenue by Course Category")
        rev = txn[["CourseID","Amount"]].merge(courses[["CourseID","CourseCategory"]], on="CourseID", how="left")
        rev_cat = rev.groupby("CourseCategory")["Amount"].sum().sort_values(ascending=False).reset_index()
        fig4 = px.bar(rev_cat, x="CourseCategory", y="Amount",
                      color="Amount", color_continuous_scale="Sunset")
        fig4.update_layout(margin=dict(t=10,b=10), xaxis_tickangle=-30)
        st.plotly_chart(fig4, use_container_width=True)
