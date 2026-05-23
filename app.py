import streamlit as st

st.set_page_config(
    page_title="EduPro | Student Intelligence Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0f2027,#203a43,#2c5364); }
[data-testid="stSidebar"] * { color: white !important; }
.rec-card { border:1px solid #e0e0e0; border-radius:10px; padding:1rem; margin:0.5rem 0; background:#fafafa; }
</style>
""", unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/color/96/graduation-cap.png", width=70)
st.sidebar.title("EduPro Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "🏠 Home / Overview",
    "🔍 Learner Profile Explorer",
    "📊 Cluster Dashboard",
    "🎯 Course Recommendations",
    "📈 Segment Comparison",
    "⚙️ Methodology",
])
st.sidebar.markdown("---")
st.sidebar.info("**EduPro AI** · Unified Mentor Internship Project")

if page == "🏠 Home / Overview":
    from home import render; render()
elif page == "🔍 Learner Profile Explorer":
    from explorer import render; render()
elif page == "📊 Cluster Dashboard":
    from clusters import render; render()
elif page == "🎯 Course Recommendations":
    from recommendations import render; render()
elif page == "📈 Segment Comparison":
    from comparison import render; render()
elif page == "⚙️ Methodology":
    from methodology import render; render()
