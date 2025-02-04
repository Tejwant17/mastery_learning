import streamlit as st
from openai import OpenAI
# Sidebar Navigation
menu = st.sidebar.radio("Navigation", ["Home", "Take Quiz", "Dashboard"])

# Home Page
if menu == "Home":
    st.title("AI-Powered Adaptive Learning System")
    st.write("Select a topic and take a dynamic quiz generated by GPT-4!")

    api_key = st.text_input("Enter your OpenAI API Key:", type="password")

    # If an API key is provided either through environment or input, initialize OpenAI client
    if api_key:
        st.session_state["api_key"] = api_key  # Store API key in session state
        st.write("Thanks! You can now begin the quiz, access it from the sidebar.")
    else:
        st.error("API Key is required to use this service.")
        st.stop() # Stop further execution if API key is not available

# Topic Selection
elif menu == "Take Quiz":
    st.header("Enter a Topic")

    selected_topic = st.text_input("Enter a topic:", "")

    if st.button("Generate Quiz"):
        if selected_topic.strip():  # Ensure topic is not empty
            st.session_state.setdefault("topic", selected_topic)
            st.session_state.setdefault("questions", None)  # Reset questions
            st.session_state.setdefault("level", 1)  # Default to Level 1
            st.session_state["questions"] = None  # Reset questions if any
            st.switch_page("pages/quiz.py")  # Navigate to quiz
        else:
            st.warning("⚠️ Please enter a topic before starting the quiz.")

# Dashboard Page
elif menu == "Dashboard":
    st.header("Student Dashboard")
    st.write(f"Current Mastery Level: {st.session_state.get('level', 1)}")
    st.write(f"Total Score: {st.session_state.get('score', 0)}")
