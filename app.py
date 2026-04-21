import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from fpdf import FPDF
import os

# ---------- PAGE ----------
st.set_page_config(page_title="AI Clinical System", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp {
    background-color: #0b1f3a;
    color: white;
    text-align: center;
}

html, body, [class*="css"] {
    color: white;
    text-align: center;
}

.login-box {
    background: #112a4d;
    padding: 30px;
    border-radius: 15px;
    width: 350px;
    margin: auto;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

# ---------- IMAGE ----------
st.image(
    "https://i.pinimg.com/736x/93/64/09/9364092181bf28c06f6cc3b0de401ad3.jpg",
    use_container_width=True
)

st.title("AI Clinical Dashboard")
st.caption("Machine Learning based medical risk prediction")

# ---------- LOGIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.subheader("Doctor Login")

    user = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "doctor" and password == "1234":
            st.session_state.logged_in = True
            st.success("Welcome Doctor 💙")
        else:
            st.error("Wrong credentials")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------- TRAINING DATA ----------
data = pd.DataFrame({
    "hb": [10, 14, 9, 13, 11, 15, 8, 12, 16, 9],
    "wbc": [12000, 6000, 15000, 7000, 11000, 5000, 16000, 8000, 5500, 14000],
    "crp": [10, 2, 15, 3, 8, 1, 20, 4, 2, 18],
    "glucose": [130, 90, 150, 85, 120, 80, 160, 95, 88, 140],
    "risk": [1, 0, 1, 0, 1, 0, 1, 0, 0, 1]
})

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

# ---------- INPUTS ----------
st.sidebar.header("Patient Data")

patient_id = st.sidebar.text_input("Patient ID", "P001")
age = st.sidebar.number_input("Age", 0, 120, 25)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
pregnant = st.sidebar.checkbox("Pregnant")

hb = st.sidebar.number_input("Hemoglobin", 0.0, 20.0, 12.0)
wbc = st.sidebar.number_input("WBC", 0.0, 20000.0, 7000.0)
crp = st.sidebar.number_input("CRP", 0.0, 100.0, 3.0)
glucose = st.sidebar.number_input("Glucose", 0.0, 300.0, 90.0)

# ---------- PREDICTION ----------
def predict_risk(hb, wbc, crp, glucose):

    input_data = np.array([[hb, wbc, crp, glucose]])

    pred = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    if prob < 0.3:
        risk = "🟢 Low Risk"
    elif prob < 0.6:
        risk = "🟡 Moderate Risk"
    else:
        risk = "🔴 High Risk"

    return risk, prob

# ---------- RUN ----------
if st.sidebar.button("Run AI Prediction"):

    risk, prob = predict_risk(hb, wbc, crp, glucose)

    st.subheader("AI Prediction Result")

    st.write("Patient ID:", patient_id)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Hb", hb)
    col2.metric("WBC", wbc)
    col3.metric("CRP", crp)
    col4.metric("Glucose", glucose)

    st.markdown("---")

    st.subheader("Risk Prediction")

    st.write(risk)
    st.write("Probability:", round(prob, 2))

    # ---------- GRAPH ----------
    st.subheader("Lab Visualization")

    labels = ["Hb", "WBC", "CRP", "Glucose"]
    values = [hb, wbc/1000, crp, glucose/10]

    fig, ax = plt.subplots()
    ax.plot(labels, values, marker="o")
    ax.set_facecolor("#0b1f3a")
    fig.patch.set_facecolor("#0b1f3a")
    ax.tick_params(colors="white")

    st.pyplot(fig)

    # ---------- REPORT ----------
    report = f"""
AI Medical Report

Patient ID: {patient_id}

Hb: {hb}
WBC: {wbc}
CRP: {crp}
Glucose: {glucose}

Prediction: {risk}
Probability: {round(prob, 2)}
"""

    st.subheader("Report")
    st.text(report)
