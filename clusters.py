import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.decomposition import PCA
from utils.data_engine import run_clustering, elbow_silhouette_data

def render():
    st.title("📊 Cluster Visualization Dashboard")
    st.markdown("---")

    with st.spinner("Running clustering..."):
        profile, sil, cluster_summary, txn, courses, X_scaled, labels = run_clustering()

    st.subheader("⚙️ Optimal Cluster Selection")
    with st.spinner("Computing elbow & silhouette..."):
        K, inertias, sils = elbow_silhouette_data()

    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=K, y=inertias, mode="lines+markers", marker=dict(color="#6c63ff",size=8), name="Inertia"))
        fig1.update_layout(title="Elbow Method", xaxis_title="K", yaxis_title="Inertia", margin=dict(t=40))
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=K, y=sils, mode="lines+markers", marker=dict(color="#f5576c",size=8), name="Silhouette"))
        fig2.update_layout(title="Silhouette Score", xaxis_title="K", yaxis_title="Score", margin=dict(t=40))
        st.plotly_chart(fig2, use_container_width=True)

    st.info(f"✅ Chosen K = 4  |  Silhouette Score = **{sil:.4f}**")

    st.markdown("---")
    st.subheader("🗺️ 2D Cluster Map (PCA)")
    pca    = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    pca_df = pd.DataFrame({"PC1":coords[:,0],"PC2":coords[:,1],
                            "Segment":profile["Segment"],"UserID":profile["UserID"],
                            "Courses":profile["total_courses_enrolled"],"Diversity":profile["diversity_score"]})
    fig3 = px.scatter(pca_df, x="PC1", y="PC2", color="Segment",
                      hover_data=["UserID","Courses","Diversity"],
                      color_discrete_sequence=px.colors.qualitative.Bold, opacity=0.7)
    fig3.update_traces(marker=dict(size=5))
    fig3.update_layout(legend=dict(orientation="h",y=-0.25), margin=dict(t=20))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("📐 Feature Distribution by Segment")
    feat = st.selectbox("Select Feature", [
        "total_courses_enrolled","avg_spending","diversity_score",
        "learning_depth_index","avg_course_rating","paid_course_ratio"
    ])
    fig4 = px.box(profile, x="Segment", y=feat, color="Segment",
                  color_discrete_sequence=px.colors.qualitative.Bold, points="outliers")
    fig4.update_layout(showlegend=False, margin=dict(t=20))
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Cluster Feature Centroids")
    agg = profile.groupby("Segment").agg(
        Count        =("UserID","count"),
        Avg_Courses  =("total_courses_enrolled","mean"),
        Avg_Diversity=("diversity_score","mean"),
        Avg_Depth    =("learning_depth_index","mean"),
        Avg_Spending =("avg_spending","mean"),
        Avg_Rating   =("avg_course_rating","mean"),
        Paid_Ratio   =("paid_course_ratio","mean"),
    ).round(2).reset_index()
    st.dataframe(agg.style.background_gradient(cmap="Blues", subset=["Avg_Courses","Avg_Diversity","Avg_Spending"]),
                 use_container_width=True, hide_index=True)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("👤 Age Distribution per Segment")
        fig5 = px.violin(profile, x="Segment", y="Age", color="Segment",
                         color_discrete_sequence=px.colors.qualitative.Pastel, box=True, points=False)
        fig5.update_layout(showlegend=False, margin=dict(t=20))
        st.plotly_chart(fig5, use_container_width=True)
    with col4:
        st.subheader("⚧ Gender Split per Segment")
        gen = profile.groupby(["Segment","Gender"])["UserID"].count().reset_index()
        gen.columns = ["Segment","Gender","Count"]
        fig6 = px.bar(gen, x="Segment", y="Count", color="Gender", barmode="group",
                      color_discrete_sequence=["#667eea","#f093fb"])
        fig6.update_layout(margin=dict(t=20), xaxis_tickangle=-20)
        st.plotly_chart(fig6, use_container_width=True)
