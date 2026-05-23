import streamlit as st

def render():
    st.title("⚙️ Data Science Methodology")
    st.markdown("---")

    st.subheader("1️⃣ Dataset Overview")
    st.markdown("""
| Sheet | Records | Key Fields |
|-------|---------|------------|
| Users | 3,000 | UserID, Age, Gender |
| Courses | 60 | CourseID, Category, Level, Rating, Price |
| Transactions | 10,000 | UserID, CourseID, Date, Amount |
| Teachers | 60 | TeacherID, Expertise, Rating |
""")

    st.subheader("2️⃣ Feature Engineering")
    st.markdown("""
**Engagement:** `total_courses_enrolled`, `enrollment_frequency`, `active_months`  
**Preference:** `preferred_category`, `preferred_level`, `avg_course_rating`  
**Behavioral:** `avg_spending`, `diversity_score`, `learning_depth_index`, `paid_course_ratio`
""")

    st.subheader("3️⃣ ML Pipeline")
    st.markdown("""
```
Raw Data → Feature Engineering → StandardScaler → K-Means (k=4)
                                                        ↓
                                              Segment Labeling
                                                        ↓
                                    Hybrid Recommendation Engine
                             (Rating × 0.5 + Peer Popularity × 0.5)
```
""")

    st.subheader("4️⃣ Learner Segments")
    c1, c2 = st.columns(2)
    with c1:
        st.info("**🎓 Deep Specialists** — High depth, advanced courses, focused domain")
        st.info("**💼 Career-Oriented** — High spending, certification-focused")
    with c2:
        st.info("**🌐 Broad Explorers** — High diversity, many categories")
        st.info("**🔰 Casual Beginners** — Low engagement, infrequent learners")

    st.subheader("5️⃣ Evaluation Metrics")
    st.markdown("""
| Metric | Purpose |
|--------|---------|
| Silhouette Score | Cluster quality (higher = better) |
| Elbow Method | Optimal K selection |
| Recommendation Score | Rating × 0.5 + Peer Popularity × 0.5 |
""")

    st.subheader("6️⃣ Tech Stack")
    st.markdown("""
| Layer | Technology |
|-------|------------|
| Data Processing | pandas, numpy |
| Machine Learning | scikit-learn |
| Visualization | plotly |
| Web App | Streamlit |
| Data Format | Excel (.xlsx) |
""")
