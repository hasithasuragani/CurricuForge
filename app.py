import streamlit as st
import os
import json
from dotenv import load_dotenv
from groq import Groq
from auth import login_page, logout
from pdf_generator import export_curriculum_pdf
from datetime import datetime

# ---------------- SETUP ----------------
load_dotenv()
MODEL_NAME = "llama-3.1-8b-instant"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CURRICULA_FILE = "curricula.json"

# ---------------- STORAGE HELPERS ----------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ---------------- AI FUNCTIONS ----------------
def generate_curriculum(subject, level, duration, skills, goal):
    prompt = f"""
You are an expert curriculum designer.

Create a detailed academic curriculum.

Subject: {subject}
Level: {level}
Duration: {duration}
Skills: {', '.join(skills)}
Goal: {goal}

Include:
1. Course Overview
2. Learning Outcomes
3. Week-wise Breakdown
4. Teaching Methodology
5. Assessment Strategy
"""
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content

def generate_student_roadmap(topic, level, duration, goal):
    prompt = f"""
You are a personal AI learning coach.

Create a personalized learning roadmap.

Topic: {topic}
Level: {level}
Duration: {duration}
Goal: {goal}

Include:
1. Learning Overview
2. Weekly Learning Plan
3. Skills to Gain
4. Resources Suggestions
5. Final Outcome
"""
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content

def generate_quiz(curriculum_text):
    prompt = f"""
Create 5 MCQs from the curriculum below.

Format:
Q1: Question
A. Option
B. Option
C. Option
D. Option
Answer: A
"""
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt + curriculum_text}],
    )
    return res.choices[0].message.content

def generate_rubric(curriculum_text):
    prompt = f"""
Create a Bloom’s Taxonomy aligned rubric for this curriculum:
{curriculum_text}
"""
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content

# ---------------- PAGE CONFIG ----------------
st.set_page_config("CurricuForge", "🎓", layout="wide")

# ---------------- MODERN DARK UI THEME ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, h4 {
    color: #38bdf8 !important;
    font-weight: 700;
}

section[data-testid="stSidebar"] {
    background-color: #020617;
    border-right: 1px solid #1e293b;
}

input, textarea, select {
    background-color: #1e293b !important;
    color: #e5e7eb !important;
    border-radius: 8px !important;
    border: 1px solid #334155 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #2563eb, #38bdf8);
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    border: none;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0px 8px 20px rgba(56,189,248,0.3);
}

.stSuccess {
    background-color: #022c22;
    border-left: 4px solid #10b981;
}

.stInfo {
    background-color: #0c1e3a;
    border-left: 4px solid #38bdf8;
}

.block-container {
    padding: 2rem 3rem;
}

hr {
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "student_roadmap" not in st.session_state:
    st.session_state.student_roadmap = None

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    login_page()
    st.stop()

# ---------------- LOAD DATA ----------------
curricula = load_json(CURRICULA_FILE, [])

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.write(f"👤 **{st.session_state.user_email}**")
    st.write(f"🎭 Role: **{st.session_state.user_role}**")
    if st.button("Logout"):
        logout()
    st.divider()

# ---------------- MAIN ----------------
st.title("🎓 CurricuForge")
st.subheader("Forge Future-Ready Curricula with AI")

# ================= TEACHER =================
if st.session_state.user_role == "teacher":
    st.success("Teacher Dashboard")

    with st.form("curriculum_form"):
        col1, col2 = st.columns(2)

        with col1:
            subject = st.text_input("Subject")
            level = st.selectbox("Level", ["High School", "Undergraduate", "Postgraduate", "Professional"])

        with col2:
            duration = st.selectbox("Duration", ["4 Weeks", "8 Weeks", "12 Weeks", "6 Months"])
            skills = st.multiselect(
                "Skills",
                [
                    "Critical Thinking",
                    "Problem Solving",
                    "Industry Readiness",
                    "Hands-on Projects",
                    "Research Skills",
                ],
            )

        goal = st.text_area("Learning Goal")
        submit = st.form_submit_button("Generate Curriculum")

    if submit and subject and goal and skills:
        curriculum = generate_curriculum(subject, level, duration, skills, goal)

        curricula.append(
            {
                "id": len(curricula) + 1,
                "title": f"{subject} ({level})",
                "timestamp": datetime.now().strftime("%d %b %Y %H:%M"),
                "content": curriculum,
                "rubric": None,
                "quiz": None,
            }
        )

        save_json(CURRICULA_FILE, curricula)
        st.success("Curriculum saved successfully")

    if curricula:
        choice = st.selectbox("Select Curriculum", [c["title"] for c in curricula])
        selected = next(c for c in curricula if c["title"] == choice)

        st.markdown(selected["content"])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("Generate Rubric"):
                selected["rubric"] = generate_rubric(selected["content"])
                save_json(CURRICULA_FILE, curricula)

        with col2:
            if st.button("Generate Quiz"):
                selected["quiz"] = generate_quiz(selected["content"])
                save_json(CURRICULA_FILE, curricula)

        with col3:
            if st.button("📄 Download PDF"):
                path = export_curriculum_pdf(
                    selected["title"],
                    selected["content"],
                    selected.get("rubric"),
                )
                with open(path, "rb") as f:
                    st.download_button("Download Curriculum PDF", f, "Curriculum.pdf")

        with col4:
            if st.button("✏️ Edit Curriculum"):
                st.session_state.edit_mode = True

        if st.session_state.edit_mode:
            st.subheader("✏️ Edit Curriculum")

            new_title = st.text_input("Edit Course Title", value=selected["title"])
            new_content = st.text_area(
                "Edit Curriculum Content (add/remove topics)",
                value=selected["content"],
                height=400
            )

            col_save, col_cancel = st.columns(2)

            with col_save:
                if st.button("💾 Save Changes"):
                    selected["title"] = new_title
                    selected["content"] = new_content
                    save_json(CURRICULA_FILE, curricula)
                    st.session_state.edit_mode = False
                    st.success("Curriculum updated successfully")
                    st.rerun()

            with col_cancel:
                if st.button("Cancel"):
                    st.session_state.edit_mode = False
                    st.rerun()

        if selected.get("rubric"):
            st.subheader("Rubric")
            st.markdown(selected["rubric"])

        if selected.get("quiz"):
            st.subheader("Quiz")
            st.text(selected["quiz"])

# ================= STUDENT =================
else:
    st.success("Student Learning Roadmap")

    with st.form("student_form"):
        topic = st.text_input("What do you want to learn?")
        level = st.selectbox("Your Level", ["Beginner", "Intermediate", "Advanced"])
        duration = st.selectbox("Duration", ["2 Weeks", "4 Weeks", "8 Weeks", "3 Months"])
        goal = st.text_area("Your Goal")

        submit = st.form_submit_button("Generate Learning Roadmap")

    if submit and topic and goal:
        st.session_state.student_roadmap = generate_student_roadmap(
            topic, level, duration, goal
        )

    if st.session_state.student_roadmap:
        roadmap = st.session_state.student_roadmap

        st.subheader("Your Personalized Roadmap")
        st.markdown(roadmap)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate Rubric"):
                rubric = generate_rubric(roadmap)
                st.subheader("Rubric")
                st.markdown(rubric)

        with col2:
            if st.button("📄 Download PDF"):
                path = export_curriculum_pdf(
                    f"{topic} Roadmap",
                    roadmap,
                )
                with open(path, "rb") as f:
                    st.download_button("Download PDF", f, "Learning_Roadmap.pdf")
