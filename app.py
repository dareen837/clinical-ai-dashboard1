import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
st.set_page_config(page_title="AI Clinical System", layout="wide")
st.image("https://i.pinimg.com/736x/93/64/09/9364092181bf28c06f6cc3b0de401ad3.jpg", use_container_width=True)

st.title("🏥 AI Clinical Dashboard")
st.caption("Welcome to your medical system")

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Clinical System", layout="wide")

# ---------- LOGIN SYSTEM ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.sidebar.title("🔐 Login")
    user = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if user == "doctor" and password == "1234":
            st.session_state.logged_in = True
            st.success("Welcome Doctor 💙")
        else:
            st.error("Invalid credentials")

login()

if not st.session_state.logged_in:
    st.stop()

# ---------- TITLE ----------
st.title("🏥 AI Clinical Decision Support System")
st.caption("Patient Analysis • Risk Scoring • Medical Reports")

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

# ---------- ANALYSIS ----------
def analyze():

    findings = []
    score = 0

    hb_limit = 12 if gender == "Female" else 13
    if age < 18:
        hb_limit = 11

    if hb < hb_limit:
        findings.append("🩸 Low Hb → anemia")
        score += 1

    if wbc > 11000:
        findings.append("🦠 High WBC → infection")
        score += 1

    if crp > 5:
        findings.append("🔥 High CRP → inflammation")
        score += 1

    if glucose > 110:
        findings.append("🍬 High glucose → hyperglycemia")
        score += 1

    if gender == "Female" and pregnant:
        if hb < 11:
            findings.append("🤰 Pregnancy + low Hb risk")
        if glucose > 95:
            findings.append("🤰 Gestational diabetes risk")

    if score == 0:
        risk = "🟢 Low Risk"
    elif score <= 2:
        risk = "🟡 Mild Risk"
    elif score <= 3:
        risk = "🟠 Moderate Risk"
    else:
        risk = "🔴 High Risk"

    return findings, risk

# ---------- AI REPORT ----------
def generate_report(findings, risk, patient_id):

    report = f"""
    🏥 AI Medical Report

    Patient ID: {patient_id}

    ----------------------
    Findings:
    """

    for f in findings:
        report += f"\n- {f}"

    report += f"""

    ----------------------
    Final Risk:
    {risk}

    ----------------------
    Recommendation:
    Clinical follow-up recommended.
    """

    return report

# ---------- PDF ----------
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.cell(200, 8, txt=line, ln=True)

    file_path = "report.pdf"
    pdf.output(file_path)

    return file_path

# ---------- RUN ----------
if st.sidebar.button("Run Analysis"):

    findings, risk = analyze()

    # metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Hb", hb)
    col2.metric("WBC", wbc)
    col3.metric("CRP", crp)
    col4.metric("Glucose", glucose)

    st.divider()

    # risk
    if "Low" in risk:
        st.success(risk)
    elif "Mild" in risk:
        st.warning(risk)
    else:
        st.error(risk)

    # findings
    st.subheader("Clinical Findings")

    for f in findings:
        st.markdown(f"🩺 {f}")

    # graph
    st.subheader("Lab Profile")

    labels = ["Hb", "WBC", "CRP", "Glucose"]
    values = [hb, wbc/1000, crp, glucose/10]

    fig, ax = plt.subplots()
    ax.plot(labels, values, marker="o")
    st.pyplot(fig)

    # report
    report = generate_report(findings, risk, patient_id)

    st.subheader("🧠 AI Report")
    st.text(report)

    # pdf
    file_path = create_pdf(report)

    with open(file_path, "rb") as f:
        st.download_button(
            "⬇️ Download PDF Report",
            f,
            file_name="medical_report.pdf",
            mime="application/pdf"
        )

# ---------- DATABASE ----------
st.divider()
st.subheader("📁 Patient Database")

data = {
    "PatientID": patient_id,
    "Age": age,
    "Gender": gender,
    "Hb": hb,
    "WBC": wbc,
    "CRP": crp,
    "Glucose": glucose
}

df = pd.DataFrame([data])

file = "patients_data.csv"

if os.path.exists(file):
    db = pd.read_csv(file)
    db = pd.concat([db, df], ignore_index=True)
else:
    db = df

db.to_csv(file, index=False)

st.dataframe(db, use_container_width=True)
