# Deep Learning Project: Mastodon Tutor AI

A web-based assistant for students and professors, providing personalized help based on course materials. The UI is built with Streamlit, conversations/files are stored in MongoDB, and vector storage is handled using FAISS with a locally fine-tuned model from Hugging Face.

## Project Structure

```
student_assistant_project/
│
├── .env                        # Environment variables for sensitive data
├── .gitignore                  # Git ignore file
├── README.md                   # Project description
├── requirements.txt            # Python dependencies
├── streamlit_app.py            # Streamlit UI entry point
│
├── config/
│   └── config.py               # Configuration loader (reads from .env)
│
├── data/
│   ├── mongodb_handler.py      # Functions to interact with MongoDB
│   ├── faiss_handler.py        # Functions to store and query vectors with FAISS
│   └── file_processor.py       # Functions to process and extract content from files
│
├── models/
│   ├── fine_tune_model.py      # Script to fine-tune a model from Hugging Face
│   └── embeddings.py           # Script to create embeddings and store them in FAISS
│
├── vector_store/
│   ├── faiss_index/            # Directory to store FAISS indices
│
├── utils/
│   ├── logger.py               # Logging utility
│   └── helpers.py              # Helper functions
│
└── templates/
    └── streamlit_ui/           # Custom HTML templates for Streamlit UI
```

## Prerequisites

- **Python 3.8+**: The project is written in Python and requires version 3.8 or newer.
- **MongoDB**: Used for storing conversations and files.
- **FAISS**: For vector storage and similarity search.
- **CUDA (Optional)**: If you plan to run the models on GPU.

### Python Dependencies

All Python dependencies are listed in the `requirements.txt` file. Install them using the following command:

```sh
pip install -r requirements.txt
```

## Setup Instructions

### Step 1: Clone the Repository

```sh
git clone https://github.com/deep3072/Mastodon-TutorAI.git
cd mastodon-tutorai
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the root directory. Here is an example of what should go into the `.env` file:

```sh
MONGODB_URI="your_mongodb_uri_here"
FAISS_INDEX_PATH="./vector_store/faiss_index"
MODEL_PATH="./models/fine_tuned_model"
```

- **`MONGODB_URI`**: Your MongoDB connection string.
- **`FAISS_INDEX_PATH`**: Path to store FAISS indices.
- **`MODEL_PATH`**: Path where the fine-tuned Hugging Face model will be saved.

### Step 3: Install Dependencies

Use the following command to install all necessary Python packages:

```sh
pip install -r requirements.txt
```

This will install packages such as `streamlit`, `pymongo`, `faiss-cpu` (or `faiss-gpu` if you're using GPU), and `transformers`.

### Step 4: Run the Streamlit Application

Launch the Streamlit UI using:

```sh
streamlit run run.py
```

This will start the web-based UI where students and professors can interact with the assistant.

## Directory Overview

- **`config/`**: Contains configuration scripts, including loading environment variables.
- **`data/`**: Manages data interaction with MongoDB and FAISS.
- **`models/`**: Contains scripts for fine-tuning the model and generating embeddings.
- **`utils/`**: Logging and helper utilities.
- **`templates/`**: Custom HTML templates for the Streamlit UI.

## How to Use

1. **UI Interface**:
   - Access the web interface on `localhost:8000` (or as per the address provided by Streamlit).
   - Enter your questions in the input box, and the assistant will respond using the content provided by your professor.

2. **Uploading Files**:
   - Use the UI to upload course materials like PDFs and slides.
   - The assistant will then process and embed the content for future interactions.


