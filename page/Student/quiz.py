import os
import json
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import re

# Load environment variables from .env file
load_dotenv()

# Model configuration
REPO_ID = "unsloth/Llama-3.2-1B-Instruct-GGUF"
MODEL_FILENAME = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"

# Initialize Streamlit session state
if "questions" not in st.session_state:
    st.session_state.questions = []

if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = {}

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "model_loaded" not in st.session_state:
    with st.spinner("Downloading and loading the model..."):
        def download_model(repo_id, model_filename, save_dir=None):
            try:
                model_path = hf_hub_download(
                    repo_id=repo_id, filename=model_filename, cache_dir=save_dir
                )
                return model_path
            except Exception as e:
                st.error(f"Error downloading the model: {e}")
                return None

        MODEL_PATH = download_model(REPO_ID, MODEL_FILENAME)
        if MODEL_PATH and os.path.exists(MODEL_PATH):
            try:
                st.session_state.llm = Llama(model_path=MODEL_PATH)
                st.session_state.model_loaded = True
                st.success("Model loaded successfully!")
            except Exception as e:
                st.error(f"Error loading the model: {e}")
                st.stop()
        else:
            st.error("Model download failed or file path is invalid.")
            st.stop()


# Function to extract summaries from JSON
def extract_summaries_from_string(course_summary):
    """
    Extracts all 'Summary' fields from the course_summary string and concatenates them into a single string.
    """
    try:
        # Use regex to extract content within "Summary": "..."
        summaries = re.findall(r'"Summary":\s*"([^"]+)"', course_summary)

        if not summaries:
            raise ValueError(
                "No summaries found in the course summary string.")

        # Concatenate all summaries into a single string
        return " ".join(summaries)
    except Exception as e:
        st.error(f"Error extracting summaries: {e}")
        return "No valid summary available."


# Function to generate 5 questions using course summary
def generate_questions(topic, course_summary):
    """
    Generate 5 multiple-choice questions using the given topic and course summary.
    """
    # parsed_summary = extract_summaries(course_summary)
    # print(parsed_summary)
    print(course_summary)
    prompt = f"""
    Create 5 multiple-choice questions based on the topic: {topic}.
    Use the following course summary to guide the question generation:
    {course_summary}

    Strictly follow this format for each question:
    Q: [Question]
    A. Option 1
    B. Option 2
    C. Option 3
    D. Option 4
    Answer: [Correct Option]

    Example:
    Q: What is the capital of France?
    A. Paris
    B. London
    C. Berlin
    D. Rome
    Answer: A. Paris
    """
    try:
        response = st.session_state.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a quiz generator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        questions_text = response["choices"][0]["message"]["content"]
        return questions_text
    except Exception as e:
        st.error(f"Error during question generation: {e}")
        return None

# Function to parse multiple questions from a batch


def parse_questions(output):
    """
    Parse a batch of 5 questions into individual questions, options, and correct answers.
    """
    questions = []
    correct_answers = {}
    current_question = None
    options = []

    lines = output.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("Q:"):
            if current_question and len(options) == 4:
                questions.append((current_question, options))
                correct_answers[len(questions) - 1] = correct_answer
            current_question = line[2:].strip()
            options = []
            correct_answer = None
        elif line.startswith(("A.", "B.", "C.", "D.")):
            options.append(line)
        elif line.startswith("Answer:"):
            correct_answer = line.split("Answer:")[-1].strip()

    # Append the last question
    if current_question and len(options) == 4:
        questions.append((current_question, options))
        correct_answers[len(questions) - 1] = correct_answer

    return questions, correct_answers


# Function to generate a quiz
def generate_quiz(topic, course_summary):
    """
    Generate a quiz with 5 questions.
    """
    questions_text = generate_questions(topic, course_summary)
    if questions_text:
        questions, correct_answers = parse_questions(questions_text)
        return questions, correct_answers
    else:
        st.warning("Failed to generate questions.")
        return [], {}


# Streamlit UI for quiz generation
st.title("Pop Quiz Generator")
st.write("Generate a quiz for selected course to practice your knowledge!")

# Use courses from session state
if "courses" not in st.session_state or not st.session_state.courses:
    st.error("No courses available in the session state.")
    st.stop()

courses = st.session_state.courses

selected_course = st.selectbox(
    "Select a course:",
    options=list(courses.keys()),
    format_func=lambda x: courses[x]["course_name"],
)
print(selected_course)

if st.button("Generate Quiz"):
    with st.spinner("Generating quiz..."):
        course_name = courses[selected_course]["course_name"]
        course_summary = courses[selected_course]["course_summary"]
        print(course_summary)
        extracted_summary = extract_summaries_from_string(
            course_summary)  # Use updated function
        st.session_state.questions, st.session_state.correct_answers = generate_quiz(
            course_name, extracted_summary
        )
        if not st.session_state.questions:
            st.warning(
                "Quiz generation failed. Please check the course summary.")


# Displaying the quiz
if st.session_state.questions:
    for idx, (question, options) in enumerate(st.session_state.questions):
        if idx not in st.session_state.user_answers:
            st.session_state.user_answers[idx] = None

        st.session_state.user_answers[idx] = st.radio(
            f"{idx + 1}. {question}",
            options,
            key=f"question_{idx}",
        )

    if st.button("Submit Quiz"):
        correct_count = 0
        for idx, (question, options) in enumerate(st.session_state.questions):
            correct_answer = st.session_state.correct_answers[idx]
            user_answer = st.session_state.user_answers[idx]

            if user_answer == correct_answer:
                correct_count += 1
                st.success(f"Question {idx + 1}: Correct!")
            else:
                st.error(
                    f"Question {idx + 1}: Incorrect! Correct answer: {correct_answer}"
                )

        st.write(
            f"Your Score: {correct_count}/{len(st.session_state.questions)}")
