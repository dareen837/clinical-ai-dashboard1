from fpdf import FPDF
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Clinical Dashboard", layout="wide")

# ---------- TITLE ----------
st.title("🧠 Clinical AI Interpretation Dashboard")
st.write("Rule-based system for lab interpretation and visualization")

# ---------- INPUTS ----------
st.sidebar.header("Patient Data")

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
        findings.append("🩸 Low Hb → possible anemia")
        score += 1

    if wbc > 11000:
        findings.append("🦠 High WBC → infection/inflammation")
        score += 1

    if crp > 5:
        findings.append("🔥 High CRP → active inflammation")
        score += 1

    if glucose > 110:
        findings.append("🍬 High glucose → hyperglycemia")
        score += 1

    if gender == "Female" and pregnant:
        if hb < 11:
            findings.append("🤰 Pregnancy + low Hb → iron deficiency risk")
        if glucose > 95:
            findings.append("🤰 Pregnancy + high glucose → gestational diabetes risk")

    if score == 0:
        risk = "🟢 Low Risk"
    elif score <= 2:
        risk = "🟡 Mild Risk"
    elif score <= 3:
        risk = "🟠 Moderate Risk"
    else:
        risk = "🔴 High Risk"

    return findings, risk


# ---------- PDF FUNCTION ----------
def create_pdf(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in report_text.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)

    file_path = "patient_report.pdf"
    pdf.output(file_path)

    return file_path


# ---------- RUN ----------
if st.sidebar.button("Analyze"):

    findings, risk = analyze()

    # report text
    full_report = "\n".join(findings) + "\n\nRisk Level: " + risk

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔬 Findings")
        for f in findings:
            st.write(f)

    with col2:
        st.subheader("⚠️ Risk Level")
        st.markdown(f"### {risk}")

    # ---------- GRAPH ----------
    st.subheader("📊 Lab Visualization")

    labels = ["Hb", "WBC", "CRP", "Glucose"]
    values = [hb, wbc/1000, crp, glucose/10]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title("Patient Lab Profile (Scaled)")
    st.pyplot(fig)

    # ---------- PDF BUTTON ----------
    if st.button("📄 Generate Patient Report PDF"):

        file_path = create_pdf(full_report)

        with open(file_path, "rb") as f:
            pdf_data = f.read()

        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_data,
            file_name="patient_report.pdf",
            mime="application/pdf"
        )
