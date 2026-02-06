import streamlit as st

USERS = {
    "teacher@test.com": {"password": "teacher123", "role": "teacher"},
    "student@test.com": {"password": "student123", "role": "student"},
}

def login_page():
    st.title("🔐 Login to CurricuForge")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in USERS and USERS[email]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.user_role = USERS[email]["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.info(
        "Teacher → teacher@test.com / teacher123\n\n"
        "Student → student@test.com / student123"
    )

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
