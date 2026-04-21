import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Smart Clinical System", layout="wide")

st.title("🧠 Clinical AI + Patient Database System")

# ---------- INPUTS ----------
st.sidebar.header("Patient Data")

patient_id = st.sidebar.text_input("Patient ID", "P001")
age = st.sidebar.number_input("Age", 0, 120, 25)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
pregnant = st.sidebar.checkbox("Pregnant (Female only)")

hb = st.sidebar.number_input("Hemoglobin (Hb)", 0.0, 20.0, 12.0)
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
        risk = "🟢 Low"
    elif score <= 2:
        risk = "🟡 Mild"
    elif score <= 3:
        risk = "🟠 Moderate"
    else:
        risk = "🔴 High"

    return findings, risk


# ---------- SAVE TO DATABASE ----------
def save_data(patient_id, age, gender, hb, wbc, crp, glucose, risk):

    data = {
        "PatientID": patient_id,
        "Age": age,
        "Gender": gender,
        "Hb": hb,
        "WBC": wbc,
        "CRP": crp,
        "Glucose": glucose,
        "Risk": risk
    }

    df = pd.DataFrame([data])

    file = "patients_data.csv"

    if os.path.exists(file):
        df.to_csv(file, mode='a', header=False, index=False)
    else:
        df.to_csv(file, index=False)


# ---------- UI ACTION ----------
if st.sidebar.button("Analyze & Save"):

    findings, risk = analyze()

    save_data(patient_id, age, gender, hb, wbc, crp, glucose, risk)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔬 Findings")
        for f in findings:
            st.write(f)

    with col2:
        st.subheader("⚠️ Risk")
        st.markdown(f"### {risk}")

    # ---------- GRAPH ----------
    st.subheader("📊 Lab Visualization")

    labels = ["Hb", "WBC", "CRP", "Glucose"]
    values = [hb, wbc/1000, crp, glucose/10]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    st.pyplot(fig)


# ---------- DATABASE VIEW ----------
st.subheader("📁 Patient Database")

if os.path.exists("patients_data.csv"):
    db = pd.read_csv("patients_data.csv")
    st.dataframe(db)

    # ---------- SEARCH ----------
    search_id = st.text_input("🔍 Search Patient by ID")

    if search_id:
        result = db[db["PatientID"] == search_id]
        st.write(result)

    # ---------- GRAPH FROM DB ----------
    st.subheader("📊 Risk Distribution")

    fig2, ax2 = plt.subplots()
    db["Risk"].value_counts().plot(kind="bar", ax=ax2)
    st.pyplot(fig2)

else:
    st.write("No data yet.")
