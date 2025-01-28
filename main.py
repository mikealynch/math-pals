import streamlit as st
import sqlite3
import bcrypt
import random
from datetime import datetime

# Authentication database setup
def init_auth_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT
                )''')
    conn.commit()
    conn.close()

# Math practice database setup
def init_math_db():
    conn = sqlite3.connect("subtraction_practice.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtraction_practice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            question TEXT,
            user_answer INTEGER,
            correct_answer INTEGER,
            is_correct BOOLEAN,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Add user to auth database
def add_user(username, hashed_password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Validate user credentials
def validate_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        stored_password = result[0]
        return bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8"))
    return False

# Insert record into math database
def insert_record(username, question, user_answer, correct_answer, is_correct):
    conn = sqlite3.connect("subtraction_practice.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subtraction_practice (username, question, user_answer, correct_answer, is_correct, date) VALUES (?, ?, ?, ?, ?, ?)",
        (username, question, user_answer, correct_answer, is_correct, datetime.now())
    )
    conn.commit()
    conn.close()

# Generate a random subtraction question
def generate_question(previous_questions):
    while True:
        num1 = random.randint(9, 18)
        num2 = random.randint(5, 12)
        if num1 < num2:
            num1, num2 = num2, num1
        question = (num1, num2)
        if question not in previous_questions:
            previous_questions.add(question)
            return question

# Initialize databases
init_auth_db()
init_math_db()

# Session state variables
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "question" not in st.session_state:
    st.session_state.previous_questions = set()
    st.session_state.question = generate_question(st.session_state.previous_questions)
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "show_next" not in st.session_state:
    st.session_state.show_next = False

# Login page
def login_page():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login")

    if submit_login:
        if validate_user(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            math_practice_page()
        else:
            st.error("Invalid username or password. Please try again.")

# Register page
def register_page():
    st.title("Register")
    with st.form("registration_form"):
        username = st.text_input("Enter a username")
        password = st.text_input("Enter a password", type="password")
        submit_register = st.form_submit_button("Register")

    if submit_register:
        if username and password:
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            if add_user(username, hashed_password):
                st.success("User registered successfully! Please log in.")
                login_page()
            else:
                st.error("Username already exists. Please choose a different one.")
        else:
            st.warning("Please fill out all fields.")

# Math practice page
def math_practice_page():
    st.title("Math Practice: Subtraction Table")
    username = st.session_state["username"]

    num1, num2 = st.session_state.question

    if not st.session_state.show_next:
        with st.form("answer_form", clear_on_submit=True):
            st.markdown(f"<h2>What is {num1} - {num2}?</h2>", unsafe_allow_html=True)
            user_answer = st.number_input("Your Answer:", step=1, format="%d", key="user_answer")
            submit_button = st.form_submit_button("Submit")

            if submit_button:
                correct_answer = num1 - num2
                is_correct = user_answer == correct_answer

                if is_correct:
                    st.session_state.feedback = "Correct! Well done!"
                    st.session_state.correct_count += 1
                else:
                    st.session_state.feedback = f"Incorrect. The correct answer is {correct_answer}."

                insert_record(username, f"{num1} - {num2}", user_answer, correct_answer, is_correct)
                st.session_state.show_next = True
                st.rerun()

    if st.session_state.feedback:
        st.markdown(f"<h3>{st.session_state.feedback}</h3>", unsafe_allow_html=True)

    if st.session_state.show_next:
        if st.button("Next Question"):
            st.session_state.question = generate_question(st.session_state.previous_questions)
            st.session_state.feedback = ""
            st.session_state.show_next = False
            st.rerun()

    st.markdown(f"<h3>Correct answers: {st.session_state.correct_count}/28</h3>", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
if st.session_state["logged_in"]:
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.experimental_rerun()
    math_practice_page()
else:
    page = st.sidebar.radio("Go to", options=["Login", "Register"])

    if page == "Login":
        login_page()
    elif page == "Register":
        register_page()
