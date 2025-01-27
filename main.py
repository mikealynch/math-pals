import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect("subtraction_practice.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtraction_practice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            user_answer INTEGER,
            correct_answer INTEGER,
            is_correct BOOLEAN,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Insert record into database
def insert_record(question, user_answer, correct_answer, is_correct):
    conn = sqlite3.connect("subtraction_practice.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subtraction_practice (question, user_answer, correct_answer, is_correct, date) VALUES (?, ?, ?, ?, ?)",
        (question, user_answer, correct_answer, is_correct, datetime.now())
    )
    conn.commit()
    conn.close()

# Clear all records from the database
def clear_database():
    conn = sqlite3.connect("subtraction_practice.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtraction_practice")
    conn.commit()
    conn.close()

# Generate a random subtraction question
# Ensure no duplicates in the same session
def generate_question(previous_questions):
    while True:
        num1 = random.randint(1, 12)
        num2 = random.randint(1, 12)
        if num1 < num2:  # Ensure no negative results
            num1, num2 = num2, num1
        question = (num1, num2)
        if question not in previous_questions:
            previous_questions.add(question)
            return question

# Initialize the database
init_db()

# Streamlit app
st.title("Math Practice: Subtraction Table")

# Session state to track progress if not initialized
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "question" not in st.session_state:
    st.session_state.previous_questions = set()
    st.session_state.question = generate_question(st.session_state.previous_questions)
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# Display the question
num1, num2 = st.session_state.question
correct_answer = num1 - num2  # Calculate the correct answer

st.markdown(f"<h2>What is {num1} - {num2}?</h2>", unsafe_allow_html=True)

# Debugging tool: Display the correct answer below the question
st.markdown(f"<h4>Expected Answer: {correct_answer}</h4>", unsafe_allow_html=True)

# Display feedback if available
if st.session_state.feedback:
    st.markdown(f"<h3>{st.session_state.feedback}</h3>", unsafe_allow_html=True)

# Input form for the answer
with st.form("answer_form"):
    user_answer = st.number_input(
        "Your Answer:", step=1, format="%d", key=f"answer_input_{num1}_{num2}",
        label_visibility="visible", help="Enter your answer here."
    )
    st.markdown(
        "<style>input[type=number] { font-size: 1.5em !important; }</style>",
        unsafe_allow_html=True
    )
    submit_button = st.form_submit_button("Submit")

# Process the answer
if submit_button:
    is_correct = user_answer == correct_answer

    # Update the database
    insert_record(f"{num1} - {num2}", user_answer, correct_answer, is_correct)

    # Provide feedback to the user
    if is_correct:
        st.session_state.feedback = "Correct! Well done!"
        st.session_state.correct_count += 1
    else:
        st.session_state.feedback = f"Incorrect. The correct answer is {correct_answer}."

    # Check if target is reached
    if st.session_state.correct_count >= 28:
        st.balloons()
        st.session_state.feedback = "Congratulations! You answered 28 questions correctly!"
        st.session_state.correct_count = 0  # Reset for the next session
        st.session_state.previous_questions.clear()  # Reset questions to avoid duplicates

    # Generate a new question
    st.session_state.question = generate_question(st.session_state.previous_questions)

# Display progress
st.markdown(f"<h3>Correct answers: {st.session_state.correct_count}/28</h3>", unsafe_allow_html=True)

# Optionally show previous attempts
if st.checkbox("Show Previous Attempts"):
    conn = sqlite3.connect("subtraction_practice.db")
    df = pd.read_sql_query("SELECT * FROM subtraction_practice ORDER BY date DESC", conn)
    st.dataframe(df)
    conn.close()

# Debug button to display entire SQL database
if st.button("Debug: Show SQL Database"):
    conn = sqlite3.connect("subtraction_practice.db")
    df = pd.read_sql_query("SELECT * FROM subtraction_practice", conn)
    st.write("### Full Database Contents")
    st.dataframe(df)
    conn.close()

# Button to clear the SQL database
if st.button("Clear Database"):
    clear_database()
    st.warning("Database cleared!")
