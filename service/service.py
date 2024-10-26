#Renamed file to file_processor 
from utils.file_processor import extract_text_and_images  # Kanishk's import
from data.mongodb_handler import MongoDBHandler
import os
import sys
import mimetypes
import io

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Service:

    def __init__(self, faiss_index=""):
        """
        Initialize the Service class with MongoDB client and FAISS index for vector storage.
        """
        self.mongodb = MongoDBHandler()  # MongoDB instance
        self.vector_store = faiss_index  # FAISS instance to store vectors
        print('Service initialized')

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

            # # After saving to DB, create embeddings in FAISS
            # self.store_vector(self.create_vector(extracted_text),
            #                 {"file_content": file_content})
        except Exception as e:
            print(f"Error processing file: {e}")
            raise RuntimeError(f"Failed to process file: {e}")
  
    # 2. Save to MongoDB (Abstract Layer)
    # DEEP
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
    
    def create_course(self, course_name, professor_name, description, professor_id):
        """
        Creates a new course in MongoDB.
        """
        return self.mongodb.create_course(course_name, professor_name, description, professor_id)

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
    
    # 3. Vector Operations
    # SHREYAS
    def store_vector(self, vector, metadata):
        """
        Stores a vector in the FAISS vector store with associated metadata.
        """
        self.vector_store.add_vector(vector, metadata)

    # RAHUL
    def search_vector(self, query_vector):
        """
        Searches for similar vectors in the FAISS vector store based on the query vector.
        """
        return self.vector_store.search(query_vector)

    # SHREYAS
    def remove_vector(self, vector_id):
        """
        Removes a vector from the FAISS vector store.
        """
        self.vector_store.remove(vector_id)

    # 4. MongoDB Operations for Conversations
    # DEEP
    def fetch_conversation(self, user_id):
        """
        Fetches conversation history for the current user from MongoDB.
        """
        pass  # Logic to fetch user conversation from MongoDB

    # DEEP
    def save_conversation(self, user_id, conversation):
        """
        Saves the current conversation for the current user in MongoDB.
        """
        pass  # Logic to save the current conversation in MongoDB

    # 5. Create prompt using chat history
    # DEEP/AJINKYA
    def create_prompt(self, user_id, current_question):
        """
        Creates a prompt by combining the user's chat history and the current question.
        """
        chat_history = self.fetch_conversation(user_id)
        prompt = chat_history + "\nQ: " + current_question
        return prompt

    # 6. Set Default Prompt
    def set_default_prompt(self):
        """
        Sets a default prompt if no conversation history is found.
        """
        return "Default prompt to use if no chat history exists."

    # 7. Call Model API for Response
    # AJINKYA
    def get_response(self, prompt):
        """
        Calls the model API to get a response based on the given prompt.
        """
        response = self.model.query(prompt)
        return response

    # Additional Embedding Functions
    # SHREYAS
    def create_vector(self, text):
        """
        Creates vector embeddings for the given text.
        """
        pass  # Logic to convert the text into vector embeddings

    def initialize_collections(self):
        """
        Initializes tables and loads data into MongoDB.
        """
        self.mongodb.initialize_collections()

# To load data for development purposes.
# file_service = Service()
# file_service.initialize_collections()