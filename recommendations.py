import streamlit as st
import plotly.express as px
from utils.data_engine import run_clustering, get_recommendations

def render():
    st.title("🎯 Personalized Course Recommendations")
    st.markdown("---")

    with st.spinner("Loading recommendation engine..."):
        profile, sil, cluster_summary, txn, courses, X_scaled, labels = run_clustering()

    col_left, col_right = st.columns([1,3])
    with col_left:
        st.subheader("🔧 Filters")
        selected_user    = st.selectbox("Select Learner", profile["UserID"].tolist())
        filter_level     = st.selectbox("Filter by Level",    ["All","Beginner","Intermediate","Advanced"])
        filter_category  = st.selectbox("Filter by Category", ["All"] + sorted(courses["CourseCategory"].unique().tolist()))
        n_recs           = st.slider("Number of Recommendations", 3, 12, 6)

    user_row = profile[profile["UserID"]==selected_user].iloc[0]
    badge_colors = {
        "🎓 Deep Specialists":"#6c63ff","🌐 Broad Explorers":"#43b89c",
        "💼 Career-Oriented Learners":"#e07b39","🔰 Casual Beginners":"#5e9bdb",
    }
    seg   = user_row["Segment"]
    color = badge_colors.get(seg,"#888")

    with col_right:
        st.markdown(f"""
        <div style="background:{color}18;border-left:5px solid {color};padding:1rem;border-radius:10px;margin-bottom:1rem;">
        <h4 style="margin:0;color:{color};">{selected_user}</h4>
        <span style="background:{color};color:white;padding:0.2rem 0.8rem;border-radius:15px;font-size:0.85rem;">{seg}</span>
        <div style="margin-top:0.6rem;display:flex;gap:2rem;flex-wrap:wrap;">
            <div>📚 <b>{int(user_row['total_courses_enrolled'])}</b> courses</div>
            <div>🌐 <b>{int(user_row['diversity_score'])}</b> categories</div>
            <div>⭐ <b>{user_row['avg_course_rating']:.2f}</b> avg rating</div>
            <div>💰 <b>${user_row['avg_spending']:.1f}</b> avg spend</div>
        </div></div>
        """, unsafe_allow_html=True)

        recs = get_recommendations(selected_user, profile, txn, courses, n=n_recs,
                                   filter_level=filter_level, filter_category=filter_category)
        if recs.empty:
            st.warning("No recommendations found. Try widening the filters.")
        else:
            st.subheader(f"📋 Top {len(recs)} Recommended Courses")
            level_icons = {"Beginner":"🟢","Intermediate":"🟡","Advanced":"🔴"}
            for _, row in recs.iterrows():
                st.markdown(f"""
                <div class="rec-card" style="border-left:4px solid {color};background:white;color:#333;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <b>{row['CourseName']}</b>
                    <span>⭐ {row['CourseRating']:.2f} &nbsp; 💰 ${row['CoursePrice']:.0f}</span>
                </div>
                <div style="margin-top:0.4rem;font-size:0.85rem;display:flex;gap:1rem;flex-wrap:wrap;">
                    <span>{level_icons.get(row['CourseLevel'],'⚪')} {row['CourseLevel']}</span>
                    <span>📁 {row['CourseCategory']}</span>
                    <span>🕐 {row['CourseDuration']:.0f}h</span>
                    <span>{"🆓 Free" if row['CourseType']=="Free" else "💳 Paid"}</span>
                </div></div>
                """, unsafe_allow_html=True)

    if not recs.empty:
        st.markdown("---")
        st.subheader("📊 Recommendation Analytics")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(recs, x="CourseName", y="CourseRating", color="CourseCategory",
                         title="Rating of Recommended Courses")
            fig.update_layout(xaxis_tickangle=-30, margin=dict(t=40))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.scatter(recs, x="CourseDuration", y="CourseRating",
                              size="CoursePrice", color="CourseLevel",
                              hover_data=["CourseName"], title="Duration vs Rating (bubble=price)",
                              color_discrete_sequence=px.colors.qualitative.Safe)
            fig2.update_layout(margin=dict(t=40))
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Most Popular Courses in Learner's Segment")
    cluster = profile[profile["UserID"]==selected_user]["Cluster"].values[0]
    peers   = profile[profile["Cluster"]==cluster]["UserID"]
    top_courses = txn[txn["UserID"].isin(peers)]["CourseID"].value_counts().head(8).reset_index()
    top_courses.columns = ["CourseID","Enrollments"]
    top_courses = top_courses.merge(courses[["CourseID","CourseName","CourseCategory"]], on="CourseID", how="left")
    fig3 = px.bar(top_courses, x="Enrollments", y="CourseName", orientation="h",
                  color="CourseCategory", color_discrete_sequence=px.colors.qualitative.Vivid)
    fig3.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=20))
    st.plotly_chart(fig3, use_container_width=True)
