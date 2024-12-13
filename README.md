# Deep Learning Project: Mastodon TutorAI

A web-based assistant designed for students and professors, offering personalized support based on course materials. The user interface is developed using Streamlit, with conversations and files stored in MongoDB, while vector storage is managed via ChromaDB.

This project is part of the ***Deep Learning*** course at ***Purdue University Fort Wayne***, under the guidance of ***Professor Zesheng Chen***. Its primary goal is to empower students by providing an AI assistant that enhances their learning experience and serves as a virtual teaching assistant for the professor.

![Login Page](https://github.com/MastodonTutorAI/v1/blob/deployment/assets/ss1.png)
![Demo](https://github.com/MastodonTutorAI/v1/blob/deployment/assets/video.gif)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/LLAMA-FF6F61?style=for-the-badge&logo=llama&logoColor=white" alt="LLAMA">
  <img src="https://img.shields.io/badge/ChromaDB-00ADD8?style=for-the-badge&logo=chromadb&logoColor=white" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
</p>

## Features
- ### Two Roles:
  - Admin: Controls course material for the assistant.
  - Student: Uses the assistant to get answers or explanations related to the course.
- ### File Upload:
  - Admin can upload three types of files: PDF, TXT, and PPTX.
  - Admin can control access to these files, determining which files should be accessible by the assistant to answer student questions.
- ### Course Management:
  - Admin can create and delete courses.
- ### Assignment Protection:
  - Students will not receive answers to questions related to any assignments, only simple explanations.
- ### Quiz:
   - Student can generate quiz on course material.

## Prerequisites

- **Python 3.8+**: The project is written in Python and requires version 3.8 or newer.
- **MongoDB**: Used for storing conversations and files.
- **OPEN_AI_API_KEY**: API key for accessing OpenAI services.
- **GROQ_API_KEY**: API key for accessing GROQ services.
- **HUGGING_FACE_TOKEN**: Token for accessing Hugging Face models and services.

## Setup Instructions

### Step 1: Clone the Repository

```sh
git clone https://github.com/MastodonTutorAI/v1.git
cd mastodon-tutorai
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the root directory. Here is an example of what should go into the `.env` file:

```sh
HF_TOKEN = "your_token"
MODEL_ID=meta-llama/Llama-3.2-1B-Instruct
MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DB_NAME = "MastodonAI"
OPENAI_API_KEY = "your_key"
GROQ_API_KEY = "your_key"
MODEL_ID_GROQ = "llama-3.1-70b-versatile"
HISTORY_LENGTH=10
```

### Step 3: Install Dependencies

Use the following command to install all necessary Python packages:

```sh
pip install -r requirements.txt
```

### Step 4: Initialize MongoDB collections

Make sure you installed mongodb to follow below steps.
Open termial in root directory and follow below commands:

```sh
python
>>> from data.mongodb_handler import MongoDBHandler
>>> mongodb = MongoDBHandler()
>>> mongodb.initialize_collections()
>>> exit()
```

### Step 5: Create sample data in MongoDB

- We need atleast one admin user to login.
- Go to MongoDB compass and open database(MastodonAI) then users collection.
- Insert below document:
```sh
#For Admin
{
  "username": "admin",
  "hashed_password": "$2b$12$uyWry9cQt7y8V9b.t4gGm.7CNrbXyIm67DlTLnQzP3e3MyqE2qjo.",
  "user_role": "admin"
}

#For Student
{
  "username": "student",
  "hashed_password": "$2b$12$VMjtivv4KnXNAdJziB.ty.gcdcQ1SlYprsSh4rYfDKYer5gIJGIiG",
  "user_role": "student"
}
```
- Need hashed password check data/mongodb_handler.py for more details.

### Step 6: Setup ChromaDB
Create empty folder chroma_db in data/

### Step 6: Run the Streamlit Application

Launch the Streamlit UI using below in terminal:

```sh
streamlit run run.py
```

This will start the web-based UI where students and professors can interact with the assistant.

## How to Use

**UI Interface**:
   - Access the web interface on `localhost:8000` (or as per the address provided by Streamlit).
   - Create new course as Admin below is one example:
   ```sh
   "course_id": "CS59000",
   "course_name": "Deep Learning",
   "professor_name": "ABC",
   "description": "Deep Learning"
   ```
   - AFter that go to View Content of course and upload file, once RAG status changes to Completed, Grant Access to that file.
   - Go to View Assistant of course and start interation with assistant for that file.


