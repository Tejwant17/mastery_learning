import streamlit as st
from openai import OpenAI
import json
from datetime import datetime, timedelta
import time
import threading

client = OpenAI(
  api_key='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'# this is also the default, it can be omitted
)

def generate_quiz(topic, level):
    question_types = {
        1: "MCQ (Single Correct), True/False",
        2: "MCQ (Single/Multiple Correct), Matching",
        3: "Passage-Based, Multiple Response, Matching (Complex), Sequence Ordering"
    }

    prompt = f"""
        Generate {level}-level quiz questions for {topic}.
        Question types should be: {question_types[level]}.
        Ensure at least 8 questions for Level 1 & 2, and 6 for Level 3.
        Format output as JSON:
        [
          {{"question": "What is 2+2?", "options": ["2", "3", "4", "5"], "answer": "4", "type": "MCQ (Single Correct)"}},
          {{"question": "...", "options": ["..."], "answer": "...", "type": "..."}}
        ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return []

# Initialize session states
st.session_state.setdefault("level", 1)
st.session_state.setdefault("score", 0)
st.session_state.setdefault("questions", None)
st.session_state.setdefault("current_index", 0)
st.session_state.setdefault("answer_submitted", False)

topic = st.session_state.get("topic")
level = st.session_state["level"]

# Ensure session variables exist
if "topic" not in st.session_state:
    st.error("No topic selected. Go back and choose a topic first.")
    st.stop()

if "level" not in st.session_state:
    st.session_state.level = 1  # Default to Level 1

if "questions" not in st.session_state or st.session_state.questions is None:
    st.session_state.questions = generate_quiz(topic, level)
    st.session_state.current_index = 0
    st.session_state.score = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()

def update_timer():
    timer_placeholder = st.empty()
    while True:
        elapsed_time = datetime.now() - st.session_state.start_time
        remaining_time = max(0, 15 * 60 - elapsed_time.total_seconds())  # 15 min in seconds

        if remaining_time <= 0:
            st.warning("⏳ Time is up! Submitting your answers automatically...")
            st.session_state.current_index = len(st.session_state.questions)  # End the quiz
            return

        minutes, seconds = divmod(int(remaining_time), 60)
        timer_placeholder.markdown(f"⏳ **Time Left: {minutes} min {seconds} sec**")
        time.sleep(1)  # Pause for 1 second

# Start the timer in a new thread
timer_thread = threading.Thread(target=update_timer, daemon=True)
timer_thread.start()

if "timer_thread" not in st.session_state:
    st.session_state.timer_thread = threading.Thread(target=update_timer, daemon=True)
    st.session_state.timer_thread.start()

# Display Quiz Question
questions = st.session_state.questions
current_index = st.session_state.current_index

if current_index < len(questions):
    q = questions[current_index]

    st.subheader(f"Question {current_index + 1}")
    st.write(q["question"])

    # Store selection in session state but do not auto-submit
    st.session_state.selected_answer = st.radio("Select an option:", q["options"], index=None)

    if st.button("Submit Answer"):
        if st.session_state.selected_answer is None:
            st.warning("Please select an answer before submitting.")
        else:
            if st.session_state.selected_answer == q["answer"]:
                st.session_state.score += 1
                st.success("✅ Correct!")
            else:
                st.error("❌ Incorrect.")

            # Move to next question
            st.session_state.current_index += 1
            st.session_state.selected_answer = None  # Reset selection
            st.rerun()

if current_index >= len(questions):  # When quiz ends
    st.subheader("📊 Quiz Completed!")

    total_questions = st.session_state.get("current_index", 0)
    score = st.session_state.get("score", 0)
    level = st.session_state.get("level", 1)

    st.write(f"✅ **Your Score:** {score} / {total_questions} ({(score/total_questions) * 100:.2f}%)")

    level_requirements = {
        1: {"min_questions": 8, "next_level": 2},
        2: {"min_questions": 8, "next_level": 3},
        3: {"min_questions": 6, "next_level": 3}  # Max level
    }

    min_required = level_requirements[level]["min_questions"]
    passed = total_questions >= min_required and (score / total_questions) >= 0.8

    if passed:
        st.success(f"🎉 Congratulations! You passed Level {level}. Proceeding to Level {level_requirements[level]['next_level']}.")

        if st.button(f"🚀 Start Level {level_requirements[level]['next_level']}"):
            st.session_state.level = level_requirements[level]["next_level"]  # Increase level
            st.session_state.score = 0  # Reset score
            st.session_state.current_index = 0  # Reset question index
            st.session_state.questions = None  # Reset questions for new level
            st.rerun()  # Restart quiz in the same page

    else:
        st.error("❌ You need at least 80% accuracy and the minimum required questions to proceed.")

        if st.button(f"🔄 Retry Level {level}"):
            st.session_state.score = 0
            st.session_state.current_index = 0
            st.session_state.questions = None
            st.rerun()  # Restart quiz in the same page
