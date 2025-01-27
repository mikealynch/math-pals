import streamlit as st
import sqlite3
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

# Generate a random subtraction question
def generate_question():
    num1 = random.randint(1, 12)
    num2 = random.randint(1, 12)
    if num1 < num2:  # Ensure no negative results
        num1, num2 = num2, num1
    return num1, num2

# Initialize the database
init_db()

# Streamlit app
st.title("Math Practice: Subtraction Table")

# Session state to track progress if not initialized
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "question" not in st.session_state:
    st.session_state.question = generate_question()

# Display the question
num1, num2 = st.session_state.question
st.write(f"What is {num1} - {num2}?")

# Input form for the answer
with st.form("answer_form"):
    user_answer = st.number_input("Your Answer:", step=1, format="%d")
    submit_button = st.form_submit_button("Submit")

# Process the answer
if submit_button:
    correct_answer = num1 - num2
    is_correct = user_answer == correct_answer

    # Update the database
    insert_record(f"{num1} - {num2}", user_answer, correct_answer, is_correct)

    # Provide feedback to the user
    if is_correct:
        st.success("Correct! Well done!")
        st.session_state.correct_count += 1
    else:
        st.error(f"Incorrect. The correct answer is {correct_answer}.")

    # Check if target is reached
    if st.session_state.correct_count >= 28:
        st.balloons()
        st.write("Congratulations! You answered 28 questions correctly!")
        st.session_state.correct_count = 0  # Reset for the next session
    else:
        st.write(f"Correct answers: {st.session_state.correct_count}/28")

    # Generate a new question
    st.session_state.question = generate_question()

# Optionally show previous attempts
if st.checkbox("Show Previous Attempts"):
    conn = sqlite3.connect("subtraction_practice.db")
    df = pd.read_sql_query("SELECT * FROM subtraction_practice ORDER BY date DESC", conn)
    st.dataframe(df)
    conn.close()
