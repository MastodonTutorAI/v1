import torch
from transformers import pipeline
from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

load_dotenv()
hf_token = os.getenv("HF_TOKEN")
model_id = os.getenv("MODEL_ID")
client = None

def initialize_chatbot():
    """Initialize the chatbot pipeline."""
    if(torch.cuda.is_available()):
        pipe = init_pipe_gpu()
    else:  
        pipe = init_pipe_cpu()
    return pipe

def initialize_chatbot_serverless():
    global client
    client = InferenceClient(api_key=hf_token)

def init_pipe_gpu():
    pipe = pipeline(
        "text-generation",
        model=model_id,
        device=0
    )
    return pipe

def init_pipe_cpu():
    pipe = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    return pipe

def generate_response(pipe, messages, max_new_tokens=256):
    """Generate a response using the chatbot."""
    outputs = pipe(messages, max_new_tokens=max_new_tokens)
    response = outputs[0]["generated_text"]
    return response

def generate_response_serverless(messages, max_new_tokens=256):
    print(messages)
    try:
        stream = client.chat.completions.create(
            model=model_id, 
            messages=messages, 
            max_tokens=max_new_tokens,
            stream=True
        )
        response = ""
        for chunk in stream:
            response += chunk.choices[0].delta.content
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        raise RuntimeError(e)
    
def update_chat_history(messages, role, content):
    """Update chat history with the given role and content."""
    messages.append({"role": role, "content": content})
    return messages

def display_conversation(messages):
    """Print the chat history in a user-friendly format."""
    for message in messages:
        role = "🧑‍💻 User" if message["role"] == "user" else "🤖 Personal Bot"
        print(f"{role}: {message['content']}\n")
