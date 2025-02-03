import streamlit as st
import matplotlib.pyplot as plt

st.title("📊 Student Dashboard")

level = st.session_state.get("level", 1)
score = st.session_state.get("score", 0)

st.write(f"🎯 Current Mastery Level: {level}")
st.write(f"🔥 Total Score: {score}")

# Progress visualization
categories = ["Knowledge", "Application", "Reasoning"]
scores = [min(level * 20, 100) for _ in categories]

plt.bar(categories, scores, color=['blue', 'green', 'red'])
plt.xlabel("Skill Areas")
plt.ylabel("Proficiency (%)")
st.pyplot(plt)

if st.button("Go Back"):
    st.switch_page("app.py")