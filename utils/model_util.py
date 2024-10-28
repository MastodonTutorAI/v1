import os
import torch
from transformers import pipeline
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
model_id = os.getenv("MODEL_ID")
use_huggingface_inference = os.getenv("USE_HF_INFERENCE", "false").lower() == "true"

# Initialize Hugging Face Client (if needed)
client = InferenceClient(api_key=hf_token) if use_huggingface_inference else None

def initialize_chatbot():
    """Initialize the chatbot, either locally or via the Hugging Face endpoint."""
    if use_huggingface_inference:
        print("Using Hugging Face Inference API...")
        return client
    else:
        print("Using local model pipeline...")
        pipe = pipeline(
            "text-generation",
            model=model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        return pipe

def generate_response(pipe_or_client, messages, max_new_tokens=256):
    """Generate a response using either local pipeline or Hugging Face inference."""
    if use_huggingface_inference:
        stream = pipe_or_client.chat.completions.create(
            model=model_id, 
            messages=messages, 
            max_tokens=max_new_tokens,
            stream=True
        )
        response = ""
        for chunk in stream:
            response += chunk.choices[0].delta.content
        return response
    else:
        outputs = pipe_or_client(messages, max_new_tokens=max_new_tokens)
        return outputs

def update_chat_history(messages, role, content):
    """Update chat history with the given role and content."""
    messages.append({"role": role, "content": content})
    return messages

def display_conversation(messages):
    """Print the chat history in a user-friendly format."""
    for message in messages:
        role = "🧑‍💻 User" if message["role"] == "user" else "🤖 Personal Bot"
        print(f"{role}: {message['content']}\n")