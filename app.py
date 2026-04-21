import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# ---------- PAGE ----------
st.set_page_config(page_title="AI Clinical System", layout="centered")

st.title("🏥 AI Clinical Dashboard")
st.caption("Explainable AI Medical Prediction System")

st.subheader("SHAP Visualization")

fig = shap.force_plot(
    explainer.expected_value[1],
    shap_vals,
    input_data[0],
    feature_names=feature_names,
    matplotlib=True
)

st.pyplot(fig)

# ---------- TRAINING DATA ----------
data = pd.DataFrame({
    "Hb": [10, 14, 9, 13, 11, 15, 8, 12, 16, 9],
    "WBC": [12000, 6000, 15000, 7000, 11000, 5000, 16000, 8000, 5500, 14000],
    "CRP": [10, 2, 15, 3, 8, 1, 20, 4, 2, 18],
    "Glucose": [130, 90, 150, 85, 120, 80, 160, 95, 88, 140],
    "Risk": [1, 0, 1, 0, 1, 0, 1, 0, 0, 1]
})

X = data[["Hb", "WBC", "CRP", "Glucose"]]
y = data["Risk"]

# ---------- MODEL ----------
from sklearn.ensemble import RandomForestClassifier

@st.cache_resource
def train_model():

    data = pd.DataFrame({
        "hb": [10, 14, 9, 13, 11, 15, 8, 12, 16, 9, 13, 7],
        "wbc": [12000, 6000, 15000, 7000, 11000, 5000, 16000, 8000, 5500, 14000, 9000, 17000],
        "crp": [10, 2, 15, 3, 8, 1, 20, 4, 2, 18, 5, 22],
        "glucose": [130, 90, 150, 85, 120, 80, 160, 95, 88, 140, 100, 170],
        "risk": [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1]
    })

    X = data[["hb", "wbc", "crp", "glucose"]]
    y = data["risk"]

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    return model

model = train_model()

import shap

# ---------- FEATURES ----------
feature_names = ["Hb", "WBC", "CRP", "Glucose"]

# ---------- EXPLAINABLE AI FUNCTION ----------
def explain_prediction(model, hb, wbc, crp, glucose):

    input_data = np.array([[hb, wbc, crp, glucose]])

    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    importances = model.feature_importances_

    explanation = []

    for name, importance in zip(feature_names, importances):
        explanation.append(f"{name} contribution: {round(importance*100, 2)}%")

    if prediction == 1:
        risk = "🔴 High Risk"
    else:
        risk = "🟢 Low Risk"

    return risk, prob, explanation

def explain_with_shap(model, hb, wbc, crp, glucose):

    input_data = np.array([[hb, wbc, crp, glucose]])

    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    shap_values = explainer.shap_values(input_data)

    # في binary classification ناخد class 1
    shap_vals = shap_values[1][0]

    explanation = []

    for name, value in zip(feature_names, shap_vals):

        direction = "increase risk" if value > 0 else "decrease risk"

        explanation.append(
            f"{name}: {round(value, 3)} → {direction}"
        )

    risk = "🔴 High Risk" if prediction == 1 else "🟢 Low Risk"

    return risk, prob, explanation, shap_vals

# ---------- INPUTS ----------
st.sidebar.header("Patient Data")

patient_id = st.sidebar.text_input("Patient ID", "P001")
hb = st.sidebar.number_input("Hemoglobin", 0.0, 20.0, 12.0)
wbc = st.sidebar.number_input("WBC", 0.0, 20000.0, 7000.0)
crp = st.sidebar.number_input("CRP", 0.0, 100.0, 3.0)
glucose = st.sidebar.number_input("Glucose", 0.0, 300.0, 90.0)

# ---------- RUN ----------
if st.sidebar.button("Run AI Analysis"):

    risk, prob, explanation = explain_prediction(model, hb, wbc, crp, glucose)

    st.subheader("🧠 Prediction Result")

    st.write("Patient ID:", patient_id)
    st.write("Risk:", risk)
    st.write("Probability:", round(prob, 2))

    st.markdown("---")

    st.subheader("📊 Why this prediction? (Explainable AI)")

    for e in explanation:
        st.write("•", e)

risk, prob, explanation, shap_vals = explain_with_shap(
    model, hb, wbc, crp, glucose
)

st.subheader("🧠 SHAP Explainable AI Result")

st.write("Risk:", risk)
st.write("Probability:", round(prob, 2))

st.subheader("📊 Why this decision? (SHAP Analysis)")

for e in explanation:
    st.write("•", e)
