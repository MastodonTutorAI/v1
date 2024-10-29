from utils.file_processor import extract_text_and_images  # Kanishk's import
from data.mongodb_handler import MongoDBHandler
from data.EmbeddingHandler import ChromaDBManager
from utils import model_util as model
import os
import sys
import mimetypes
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Service:

    def __init__(self):
        """
        Initialize the Service class with MongoDB client and FAISS index for vector storage.
        """
        self.mongodb = MongoDBHandler() 
        self.chroma_db_manager = ChromaDBManager()  
        # self.pipe = self.init_pipe_model()
        model.initialize_chatbot_serverless()
        print('Service initialized')

    def set_course_id(self, course_id):
        self.course_id = course_id

    #ALISHA
    #Checking for file type
    def get_file_type(self, file_name):
        if not file_name:
            raise ValueError("File name is missing; cannot determine file type")
        
        mime_type, _ = mimetypes.guess_type(file_name)

        if not mime_type:
            # Extract the file extension and raise an error if unknown
            file_extension = os.path.splitext(file_name)[1]
            if not file_extension:
                raise ValueError("File extension is missing; cannot determine file type")
            else:
                raise ValueError(f"Unknown file type for extension '{file_extension}' in {file_name}")

        return mime_type

    # 1. Embedding Creation
    def create_embedding(self, file_content, course_id):
        """
        Generates embeddings for different file types like PDF, text, pptx, etc.
        After extracting text from the document, the text is stored in MongoDB.
        Then, embeddings are created and stored in FAISS.
        """
        try:
            extracted_text = extract_text_and_images(file_content.type, file_content)
            if not extracted_text:
               raise ValueError("Failed to extract text from the given file.")
            
            # Save extracted text to MongoDB
            file_id = self.save_file_db(file_content, extracted_text, course_id)

            # After saving to DB, create embeddings in FAISS
            self.store_vector(course_id=course_id, document_id=file_id, extracted_text=extracted_text)
        except Exception as e:
            print(f"Error processing file: {e}")
            raise RuntimeError(f"Failed to process file: {e}")
  
    # 2. Save to MongoDB (Abstract Layer)
    # DEEP
    def initialize_collections(self):
        """
        Initializes tables and loads data into MongoDB.
        """
        self.mongodb.initialize_collections()

    def save_file_db(self, file_content, extracted_text, course_id):
        """
        Saves the file and their extracted text to MongoDB.
        """
        return self.mongodb.save_file(file_content, extracted_text, course_id)

    def get_file_db(self, course_id):
        """
        Retrieves the file and extracted text from the specified MongoDB collection.
        """
        return self.mongodb.get_files(course_id)
    
    def create_course(self, course_id, course_name, professor_name, description, professor_id):
        """
        Creates a new course in MongoDB.
        """
        course_id = self.mongodb.create_course(course_id, course_name, professor_name, description, professor_id)
        if course_id:
            self.chroma_db_manager.create_course_db(course_id=course_id)
        return course_id

    def get_courses(self, professor_id):
        """
        Retrieves all courses from MongoDB.
        """
        return self.mongodb.get_courses(professor_id)

    def delete_file_db(self, file, collection_name):
        """
        Deletes the file and extracted text from the specified MongoDB collection.
        """
        pass  # Logic to delete file and text in MongoDB goes here
    
    def login(self, username, hashed_password):
        """
        Validates the user login credentials from MongoDB.
        """
        return self.mongodb.login(username, hashed_password)
    
    def save_conversation(self, conversation_data):
        """
        Saves a conversation to MongoDB.
        """
        return self.mongodb.save_conversation(conversation_data)

    def remove_conversation(self, conversation_id):
        """
        Removes a conversation from MongoDB.
        """
        return self.mongodb.remove_conversation(conversation_id)

    def get_conversation(self, conversation_id):
        """
        Retrieves a conversation from MongoDB.
        """
        return self.mongodb.get_conversation(conversation_id)

    # 3. Vector Operations
    # SHREYAS
    def store_vector(self, course_id, document_id, extracted_text):
        """
        Stores a vector in the chroma vector store with associated metadata.
        """
        self.chroma_db_manager.store_vector(course_id, document_id, extracted_text)

    def search_vector(self, query_text):
        """
        Searches for similar vectors in the FAISS vector store based on the query vector.
        """
        return self.chroma_db_manager.search_vector(course_id=self.course_id, query_text=query_text)

    def remove_vector(self, vector_id):
        """
        Removes a vector from the FAISS vector store.
        """
        self.vector_store.remove(vector_id)

        # 4. MongoDB Operations for Conversations
    
    # 5. Create prompt using search_vector
    def create_prompt(self, messages, input):
        """
        Creates a prompt by combining the user's chat history and the current question.
        """
        chunks = self.search_vector(input)
        messages.append({"role": "system", "content": "Use below information to answer the question. " + str(chunks)})
        return messages

    # 6. Set Default Prompt
    def get_system_prompt(self):
        """
        Sets a system prompt
        """
        system_prompt = (
            "You will be acting as a professor's assistant for the graduate-level course named 'Cryptography and Network Security.' "
            "Your primary responsibility is to answer students' questions about course content with clarity, as if the professor were addressing the question directly in a classroom setting."

            "Here are the critical rules for your interaction:"
            "<rules>"
            "1. Answer questions in a conversational, humanized manner, emulating the teaching style of a professor. Be supportive, engaging, and clear."
            "2. Prioritize the provided course material to ensure responses align closely with the professor's teachings. If context is incomplete, supplement with your knowledge, but keep it course-relevant."
            "3. If a question or word is not related to the course material or context, do not answer based on the course material. Only provide responses related to cryptography and network security."
            "4. Break down complex cryptography and network security topics into simple, relatable explanations. Use examples, analogies, and step-by-step guidance to clarify difficult concepts."
            "5. Approach each question respectfully, as if asked directly by a student to the professor. Your responses should be informative, helpful, and patient, especially when students may be struggling with challenging material."
            "6. When appropriate, encourage deeper understanding and curiosity in students. Avoid overly technical jargon, but explain key terms in an accessible way."
            "</rules>"

            "Your goal is to provide context-driven, accurate responses that feel as though the professor is addressing the student, fostering understanding in cryptography and network security topics."
        )

        return system_prompt

    # 7. Call Model API for Response
    # AJINKYA
    def init_pipe_model(self):
        """Initializes the chatbot pipeline model."""
        try:
            return model.initialize_chatbot()
        except Exception as e:
            print(f"Error loading model: {e}")

    def get_response_model(self, messages, max_new_tokens=256):
        """Generates a chatbot response using the pipeline."""
        if not self.pipe:
            print("Model not initialized.")
            return "[Error: Model not initialized]"
        try:
            # messages = self.create_prompt(messages, messages[-1]["content"])
            return model.generate_response(self.pipe, messages, max_new_tokens)
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error generating response: {e}"

    def get_response_model_serverless(self, messages, max_new_tokens=256):
        """Generates a chatbot response using the serverless model."""
        try:
            # messages = self.create_prompt(messages, messages[-1]["content"])
            return model.generate_response_serverless(messages, max_new_tokens)
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error generating response: {e}"

    def update_model_chat_history(self, messages, role, content):
        """Updates the chat history with the latest user and model messages."""
        if not self.pipe:
            print("Model not initialized.")
            return "[Error: Model not initialized]"

        try:
            return model.update_chat_history(self.pipe, messages, role, content)
        except Exception as e:
            print(f"Error updating history: {e}")
            return "[Error updating history]"

    def display_chat(self, messages):
        """Displays the chat conversation."""
        if not messages:
            print("Chat not available.")
            return "[Error: No chat available]"

        try:
            return model.display_conversation(messages)
        except Exception as e:
            print(f"Error displaying conversation: {e}")
            return "[Error displaying conversation]"
        
# # To load data for development purposes.
# file_service = Service()
# # file_service.initialize_collections()
# response = file_service.get_response_model(["Hello!"], max_new_tokens=256)
# print(response)