import os
import streamlit as st
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

def download_model(repo_id, model_filename, save_dir=None):
    """
    Downloads a model from Hugging Face and returns its local path.

    Args:
        repo_id (str): The repository ID on Hugging Face.
        model_filename (str): The specific model file to download.
        save_dir (str, optional): Directory to save the downloaded model.

    Returns:
        str: The full local path to the downloaded model file.
    """
    try:
        model_path = hf_hub_download(repo_id=repo_id, filename=model_filename, cache_dir=save_dir)
        st.success(f"Model downloaded successfully: {model_path}")
        return model_path
    except Exception as e:
        st.error(f"Error downloading the model: {e}")
        return None



st.title("Interactive Quiz Generator")
st.write(
    "Generate a quiz based on your selected topic and number of questions. Answer the questions and see your results.")


REPO_ID = "unsloth/Llama-3.2-1B-Instruct-GGUF"
MODEL_FILENAME = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"


if "model_loaded" not in st.session_state:
    with st.spinner("Downloading and loading the model..."):
        MODEL_PATH = download_model(REPO_ID, MODEL_FILENAME)

        # Check if the model was successfully downloaded and the path is correct
        if MODEL_PATH and os.path.exists(MODEL_PATH):
            st.write(f"Model path: {MODEL_PATH}")  # Display the model path
            try:
                # Initialize the Llama model only after it's downloaded successfully
                st.session_state.llm = Llama.from_pretrained(
                    repo_id=REPO_ID,
                    filename='Llama-3.2-1B-Instruct-Q4_K_M.gguf',
                )
                st.session_state.model_loaded = True
                st.success("Model loaded successfully!")
            except Exception as e:
                st.error(f"Error loading the model: {e}")
        else:
            st.error("Model download failed or file path is invalid.")
            st.stop()



def generate_quiz(topic, num_questions):
    prompt_Making = f"""

    Create a quiz on the topic: {topic}.
    The quiz should consist of {num_questions} multiple-choice questions, each with four options and an answer key. Format as:
    Q1: [Question]
    A. Option 1
    B. Option 2
    C. Option 3
    D. Option 4
    Answer: [Correct Option]
    """
    prompt = [{"role": "system", "content": "You are a quiz generator which generates quiz based on topic provided"},
              {"role": "user", "content": f"{prompt_Making}"}]
    # Ensure llm is properly loaded before using it
    if "llm" in st.session_state:
        try:
            response = st.session_state.llm.create_chat_completion(messages=prompt)
            quiz_content = response["choices"][0]["message"]["content"]
            return quiz_content
        except Exception as e:
            st.error(f"Error during quiz generation: {e}")
            return ""
    else:
        st.error("Model not loaded properly. Please try again.")
        return ""



topic = st.text_input("Enter a topic for the quiz:", "General Knowledge")
num_questions = st.slider("Number of questions:", min_value=1, max_value=10, value=5)


if st.button("Generate Quiz"):
    with st.spinner("Generating your quiz..."):
        try:
            quiz = generate_quiz(topic, num_questions)
            if quiz:
                st.success("Quiz Generated Successfully!")

                questions = quiz.split('\n\n')
                answers = []
                for question in questions:

                    if question.strip():
                        question_text = question.split('\n')[0]
                        options = [line for line in question.split('\n')[1:] if
                                   line.startswith("A.") or line.startswith("B.") or line.startswith(
                                       "C.") or line.startswith("D.")]
                        correct_answer = question.split('Answer: ')[-1].strip()
                        user_answer = st.radio(f"{question_text}", options, key=question_text)
                        answers.append((user_answer, correct_answer))


                if st.button("Submit Answers"):
                    correct_count = 0
                    for idx, (user_answer, correct_answer) in enumerate(answers):
                        question_text = questions[idx].split('\n')[0]
                        if user_answer == correct_answer:
                            correct_count += 1
                            st.success(f"Q{idx + 1}: {question_text} - Correct!")
                        else:
                            st.error(f"Q{idx + 1}: {question_text} - Incorrect! Correct Answer: {correct_answer}")

                    st.write(f"Total Correct Answers: {correct_count}/{len(answers)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
