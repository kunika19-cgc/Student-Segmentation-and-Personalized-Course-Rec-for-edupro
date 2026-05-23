# 🎓 EduPro Student Intelligence Platform
**Student Segmentation & Personalized Course Recommendation System**  
*Unified Mentor Data Science Internship Project*

---

## 🚀 How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy on Streamlit Cloud
1. Push this folder to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select repo → main file: `app.py` → Deploy

## 🌐 Deploy on Render
1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect repo → it will auto-detect `render.yaml`
4. Deploy

## 📂 Project Structure
```
├── app.py                      ← Main entry point
├── home.py                     ← Overview dashboard
├── explorer.py                 ← Learner profile explorer
├── clusters.py                 ← Cluster visualization
├── recommendations.py          ← Course recommendations
├── comparison.py               ← Segment comparison
├── methodology.py              ← Pipeline documentation
├── requirements.txt            ← Dependencies
├── render.yaml                 ← Render deployment config
├── EduPro_Online_Platform.xlsx ← Dataset
└── utils/
    └── data_engine.py          ← ML logic
```

## 🧠 Features
- K-Means Clustering (k=4) with Elbow + Silhouette validation
- 4 named learner segments
- Hybrid recommendation engine
- Interactive Plotly dashboards
- PCA cluster visualization
