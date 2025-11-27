import sys
import os

# Ensure repo root (project root) is in the path
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from agent import main as run_agent
import asyncio
import os
import tempfile
import json



# --- Page Configuration ---
st.set_page_config(
    page_title="Summury and Quiz AI",
    page_icon="🧠",
    layout="wide",
)




# --- Initialize Session State ---
if 'quiz_generated' not in st.session_state:
    st.session_state['quiz_generated'] = False
if 'quiz_data' not in st.session_state:
    st.session_state['quiz_data'] = []
if 'summary_text' not in st.session_state:
    st.session_state['summary_text'] = ""
if 'score' not in st.session_state:
    st.session_state['score'] = 0
if 'answers' not in st.session_state:
    st.session_state['answers'] = {}

# --- Main Application ---
st.title("🧠 Summarizer & Quiz Generator")

st.markdown(
    "Upload your PDF study notes, and let the AI assistant create a summary and a quiz for you."
)

# PDF uploader
uploaded_file = st.file_uploader(
    "Upload your Study Notes (PDF)",
    type=["pdf"],
    help="Please upload a PDF file containing your notes."
)

# If a file is uploaded, manage the state
if uploaded_file:
    # This block handles the logic for when a quiz has NOT been generated yet.
    if not st.session_state.quiz_generated:
        
        # --- Options for Quiz Generation ---
        st.subheader("Quiz Options")
        col1, col2 = st.columns(2)
        with col1:
            quiz_type = st.selectbox("Quiz Type:", ("Multiple Choice", "True/False"))
        with col2:
            num_questions = st.number_input("Number of Questions:", min_value=3, max_value=15, value=5, step=1)
        
        if st.button("✨ Generate Summary & Quiz", use_container_width=True):
            with st.spinner("🤖 The AI agent is processing your document... Please wait."):
                try:
                    # Save uploaded file to a temporary path
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    # Run the agent and get the result, passing all options
                    result = asyncio.run(run_agent(
                        file_path=tmp_file_path, 
                        quiz_type=quiz_type, 
                        num_questions=num_questions
                    ))
                    os.remove(tmp_file_path) # Clean up temp file

                    if result:
                        # Parse the agent's response
                        try:
                            summary_part, quiz_part = result.split("---QUIZ---")
                            st.session_state.summary_text = summary_part.replace("---SUMMARY---", "").strip()
                            json_str = quiz_part.strip().lstrip("```json").rstrip("```").strip()
                            st.session_state.quiz_data = json.loads(json_str)
                            st.session_state.quiz_generated = True # Set the flag
                            # Reset score and answers for the new quiz
                            st.session_state.score = 0
                            st.session_state.answers = {}
                            st.balloons()
                            st.rerun() # Rerun to enter the display logic below
                        except (ValueError, json.JSONDecodeError) as e:
                            st.error(f"Error parsing the agent's response. Please try again. Details: {e}")
                            st.session_state.summary_text = result
                    else:
                        st.error("The agent did not return a result. Please check the console for logs.")

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                        os.remove(tmp_file_path)


    # This block handles displaying the quiz AFTER it has been generated
    if st.session_state.quiz_generated:
        st.header("Results")
        summary_tab, quiz_tab = st.tabs(["📝 Summary", "❓ Quiz"])

        with summary_tab:
            st.subheader("Generated Summary")
            st.markdown(st.session_state.summary_text)

        with quiz_tab:
            st.subheader("Generated Quiz")
            if not st.session_state.quiz_data:
                st.warning("No quiz data to display.")
            else:
                total_questions = len(st.session_state.quiz_data)
                st.metric(label="Your Score", value=f"{st.session_state.score} / {total_questions}")
                st.divider()

                for i, question_data in enumerate(st.session_state.quiz_data):
                    st.markdown(f"**Question {i+1}: {question_data['question']}**")
                    if i in st.session_state.answers:
                        st.radio("Your selection:", options=question_data['options'], key=f"q_{i}_display",
                                 index=question_data['options'].index(st.session_state.answers[i]['user_answer']),
                                 disabled=True, label_visibility="collapsed")
                        if st.session_state.answers[i]['is_correct']:
                            st.success("You answered: Correct! 🎉")
                        else:
                            st.error(f"You answered: Incorrect. The correct answer was: **{st.session_state.answers[i]['correct_answer']}**")
                    else:
                        with st.form(key=f"quiz_form_{i}"):
                            user_answer = st.radio("Choose your answer:", options=question_data['options'],
                                                   key=f"q_{i}_option", label_visibility="collapsed")
                            submitted = st.form_submit_button("Check Answer")
                            if submitted:
                                correct_answer = question_data['answer']
                                is_correct = (user_answer.strip() == correct_answer.strip())
                                if is_correct:
                                    st.session_state.score += 1
                                st.session_state.answers[i] = {
                                    'user_answer': user_answer,
                                    'correct_answer': correct_answer,
                                    'is_correct': is_correct
                                }
                                st.rerun()
        
        if st.button("↩️ Start Over"):
            st.session_state.quiz_generated = False
            st.session_state.quiz_data = []
            st.session_state.summary_text = ""
            st.session_state.score = 0
            st.session_state.answers = {}
            st.rerun()

else:
    # If no file is uploaded, reset the state
    st.session_state.quiz_generated = False
    st.session_state.quiz_data = []
    st.session_state.summary_text = ""
    st.session_state.score = 0
    st.session_state.answers = {}
    st.info("Please upload a PDF file to get started.")