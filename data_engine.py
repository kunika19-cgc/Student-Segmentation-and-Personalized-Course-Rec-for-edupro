import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import streamlit as st

@st.cache_data
def load_data():
    xl = pd.read_excel("EduPro_Online_Platform.xlsx", sheet_name=None)
    users = xl["Users"]
    courses = xl["Courses"]
    transactions = xl["Transactions"]
    return users, courses, transactions

@st.cache_data
def build_learner_profiles():
    users, courses, transactions = load_data()

    # Use only needed columns to avoid merge conflicts
    txn = transactions[["TransactionID","UserID","CourseID","TransactionDate","Amount"]].copy()
    crs = courses[["CourseID","CourseCategory","CourseLevel","CourseRating","CourseType","CoursePrice","CourseDuration","CourseName"]].copy()

    merged = txn.merge(crs, on="CourseID", how="left")

    # Engagement
    total_enrolled = merged.groupby("UserID")["CourseID"].count().rename("total_courses_enrolled")
    avg_spending   = merged.groupby("UserID")["Amount"].mean().rename("avg_spending")
    total_spending = merged.groupby("UserID")["Amount"].sum().rename("total_spending")

    merged["YearMonth"] = pd.to_datetime(merged["TransactionDate"]).dt.to_period("M")
    active_months = merged.groupby("UserID")["YearMonth"].nunique().rename("active_months")

    # Preference
    preferred_category = (
        merged.groupby(["UserID","CourseCategory"])["CourseID"].count()
        .reset_index().sort_values("CourseID", ascending=False)
        .drop_duplicates("UserID").set_index("UserID")["CourseCategory"]
        .rename("preferred_category")
    )
    preferred_level = (
        merged.groupby(["UserID","CourseLevel"])["CourseID"].count()
        .reset_index().sort_values("CourseID", ascending=False)
        .drop_duplicates("UserID").set_index("UserID")["CourseLevel"]
        .rename("preferred_level")
    )
    avg_rating = merged.groupby("UserID")["CourseRating"].mean().rename("avg_course_rating")

    # Behavioral
    diversity_score = merged.groupby("UserID")["CourseCategory"].nunique().rename("diversity_score")

    lvl = merged.groupby(["UserID","CourseLevel"])["CourseID"].count().unstack(fill_value=0)
    for l in ["Beginner","Intermediate","Advanced"]:
        if l not in lvl.columns:
            lvl[l] = 0
    learning_depth = ((lvl["Advanced"] + lvl["Intermediate"]) / lvl.sum(axis=1).replace(0,1)).rename("learning_depth_index")

    fp = merged.groupby(["UserID","CourseType"])["CourseID"].count().unstack(fill_value=0)
    for t in ["Free","Paid"]:
        if t not in fp.columns:
            fp[t] = 0
    paid_ratio = (fp["Paid"] / (fp["Free"] + fp["Paid"]).replace(0,1)).rename("paid_course_ratio")

    profile = pd.concat([
        total_enrolled, avg_spending, total_spending, active_months,
        preferred_category, preferred_level, avg_rating,
        diversity_score, learning_depth, paid_ratio
    ], axis=1).reset_index()

    profile = profile.merge(users[["UserID","Age","Gender"]], on="UserID", how="left")
    profile["avg_spending"] = profile["avg_spending"].fillna(0)
    profile["avg_course_rating"] = profile["avg_course_rating"].fillna(0)
    profile["diversity_score"] = profile["diversity_score"].fillna(1)
    profile["learning_depth_index"] = profile["learning_depth_index"].fillna(0)
    profile["paid_course_ratio"] = profile["paid_course_ratio"].fillna(0)
    profile["active_months"] = profile["active_months"].fillna(1)
    profile["enrollment_frequency"] = profile["total_courses_enrolled"] / profile["active_months"]

    # Return clean txn (no extra columns)
    clean_txn = transactions[["TransactionID","UserID","CourseID","TransactionDate","Amount","PaymentMethod","TeacherID"]].copy()
    return profile, clean_txn, courses

@st.cache_data
def run_clustering(n_clusters=4):
    profile, txn, courses = build_learner_profiles()

    features_num = [
        "total_courses_enrolled","avg_spending","diversity_score",
        "learning_depth_index","avg_course_rating","enrollment_frequency","paid_course_ratio"
    ]
    le_cat = LabelEncoder()
    le_lvl = LabelEncoder()
    profile["preferred_category_enc"] = le_cat.fit_transform(profile["preferred_category"].fillna("Unknown"))
    profile["preferred_level_enc"]    = le_lvl.fit_transform(profile["preferred_level"].fillna("Beginner"))

    X = profile[features_num + ["preferred_category_enc","preferred_level_enc"]].copy()
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    profile["Cluster"] = kmeans.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, profile["Cluster"])

    cluster_summary = profile.groupby("Cluster").agg(
        avg_courses  =("total_courses_enrolled","mean"),
        avg_diversity=("diversity_score","mean"),
        avg_depth    =("learning_depth_index","mean"),
        avg_spending =("avg_spending","mean"),
    )

    ranked_depth     = cluster_summary["avg_depth"].rank(ascending=False)
    ranked_diversity = cluster_summary["avg_diversity"].rank(ascending=False)
    ranked_spending  = cluster_summary["avg_spending"].rank(ascending=False)
    ranked_courses   = cluster_summary["avg_courses"].rank(ascending=False)

    labels, assigned = {}, set()
    for lbl, rank_series in [
        ("🎓 Deep Specialists",        ranked_depth),
        ("🌐 Broad Explorers",          ranked_diversity),
        ("💼 Career-Oriented Learners", ranked_spending),
        ("🔰 Casual Beginners",         ranked_courses),
    ]:
        for c in rank_series.sort_values().index:
            if c not in assigned:
                labels[c] = lbl
                assigned.add(c)
                break

    profile["Segment"] = profile["Cluster"].map(labels)
    return profile, sil, cluster_summary, txn, courses, X_scaled, labels

@st.cache_data
def elbow_silhouette_data():
    profile, txn, courses = build_learner_profiles()
    features_num = [
        "total_courses_enrolled","avg_spending","diversity_score",
        "learning_depth_index","avg_course_rating","enrollment_frequency","paid_course_ratio"
    ]
    le_cat = LabelEncoder(); le_lvl = LabelEncoder()
    profile["preferred_category_enc"] = le_cat.fit_transform(profile["preferred_category"].fillna("Unknown"))
    profile["preferred_level_enc"]    = le_lvl.fit_transform(profile["preferred_level"].fillna("Beginner"))
    X = profile[features_num + ["preferred_category_enc","preferred_level_enc"]].copy()
    X_scaled = StandardScaler().fit_transform(X)
    inertias, sils = [], []
    for k in range(2,9):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        lbl = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        sils.append(silhouette_score(X_scaled, lbl))
    return list(range(2,9)), inertias, sils

def get_recommendations(user_id, profile, txn, courses, n=6, filter_level=None, filter_category=None):
    user_row = profile[profile["UserID"] == user_id]
    if user_row.empty:
        return pd.DataFrame()
    cluster  = user_row["Cluster"].values[0]
    enrolled = set(txn[txn["UserID"] == user_id]["CourseID"])
    peers    = profile[(profile["Cluster"] == cluster) & (profile["UserID"] != user_id)]["UserID"]

    peer_pop = txn[txn["UserID"].isin(peers)]["CourseID"].value_counts().reset_index()
    peer_pop.columns = ["CourseID","peer_popularity"]

    rec = courses[~courses["CourseID"].isin(enrolled)].merge(peer_pop, on="CourseID", how="left")
    rec["peer_popularity"] = rec["peer_popularity"].fillna(0)
    rec["score"] = rec["CourseRating"] * 0.5 + rec["peer_popularity"] * 0.5

    if filter_level and filter_level != "All":
        rec = rec[rec["CourseLevel"] == filter_level]
    if filter_category and filter_category != "All":
        rec = rec[rec["CourseCategory"] == filter_category]

    return rec.sort_values("score", ascending=False).head(n)
