import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import shap

# ---------- PAGE ----------
st.set_page_config(page_title="AI Clinical System", layout="centered")

st.title("🏥 AI Clinical Dashboard")
st.caption("Explainable AI Medical Prediction System")

# ---------- TRAINING DATA ----------
@st.cache_resource
def train_model():

    data = pd.DataFrame({
        "Hb": [10, 14, 9, 13, 11, 15, 8, 12, 16, 9, 13, 7],
        "WBC": [12000, 6000, 15000, 7000, 11000, 5000, 16000, 8000, 5500, 14000, 9000, 17000],
        "CRP": [10, 2, 15, 3, 8, 1, 20, 4, 2, 18, 5, 22],
        "Glucose": [130, 90, 150, 85, 120, 80, 160, 95, 88, 140, 100, 170],
        "Risk": [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1]
    })

    X = data[["Hb", "WBC", "CRP", "Glucose"]]
    y = data["Risk"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

model = train_model()

# ---------- SHAP SETUP ----------
explainer = shap.TreeExplainer(model)

feature_names = ["Hb", "WBC", "CRP", "Glucose"]

# ---------- INPUTS ----------
st.sidebar.header("Patient Data")

patient_id = st.sidebar.text_input("Patient ID", "P001")
hb = st.sidebar.number_input("Hemoglobin", 0.0, 20.0, 12.0)
wbc = st.sidebar.number_input("WBC", 0.0, 20000.0, 7000.0)
crp = st.sidebar.number_input("CRP", 0.0, 100.0, 3.0)
glucose = st.sidebar.number_input("Glucose", 0.0, 300.0, 90.0)

# ---------- PREDICTION ----------
def predict(model, hb, wbc, crp, glucose):

    input_data = np.array([[hb, wbc, crp, glucose]])

    pred = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    risk = "🔴 High Risk" if pred == 1 else "🟢 Low Risk"

    return risk, prob, input_data

# ---------- SHAP EXPLANATION (FIXED SAFE VERSION) ----------
def explain_shap(input_data):

    shap_values = explainer.shap_values(input_data)

    # ✅ Safe handling (fixes IndexError across versions)
    if isinstance(shap_values, list):
        shap_vals = shap_values[1][0]
    else:
        shap_vals = shap_values[0]

    explanation = []

    for name, value in zip(feature_names, shap_vals):
        direction = "increases risk" if value > 0 else "decreases risk"
        explanation.append(f"{name}: {round(value, 3)} → {direction}")

    return shap_vals, explanation

# ---------- RUN ----------
if st.sidebar.button("Run AI Analysis"):

    risk, prob, input_data = predict(model, hb, wbc, crp, glucose)

    st.subheader("🧠 Prediction Result")

    st.write("Patient ID:", patient_id)
    st.write("Risk:", risk)
    st.write("Probability:", round(prob, 2))

    st.markdown("---")

    # ---------- SHAP ----------
    shap_vals, explanation = explain_shap(input_data)

    st.subheader("📊 Why this prediction? (SHAP Explanation)")

    for e in explanation:
        st.write("•", e)

    # ---------- VISUALIZATION ----------
    st.subheader("📊 Feature Impact")

    fig, ax = plt.subplots()
    ax.barh(feature_names, shap_vals)
    ax.set_xlabel("Impact on Prediction")

    st.pyplot(fig)
