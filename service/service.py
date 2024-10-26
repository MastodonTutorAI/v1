import os
import sys
import mimetypes

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.pdf_utility import extract_text_and_images  # Kanishk's import
from data.mongodb_handler import MongoDBHandler
from data.EmbeddingHandler import ChromaDBManager

class Service:

    def __init__(self, course_id):
        """
        Initialize the Service class with MongoDB client and FAISS index for vector storage.
        """
        self.mongodb = MongoDBHandler() 
        self.chroma_db_manager = ChromaDBManager()  
        self.course_id = course_id  
        print('Service initialized')

    #ALISHA
    #Checking for file type
    def get_file_type(self, file_content):
        file_name = getattr(file_content, 'name', None)
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            raise ValueError(f"Cannot determine file type for {file_name}")
        return mime_type

    # 1. Embedding Creation
    def create_embedding(self, file_content, course_id):
        """
        Generates embeddings for different file types like PDF, text, pptx, etc.
        After extracting text from the document, the text is stored in MongoDB.
        Then, embeddings are created and stored in FAISS.
        """
        file_type = self.get_file_type(file_content)
        if file_type == 'application/pdf':
            extracted_text = self.create_pdf_embedding(file_content)
        elif file_type == 'text/plain':
            extracted_text = self.create_text_embedding(file_content)
        elif file_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            extracted_text = self.create_pptx_embedding(file_content)

        # Save extracted text to MongoDB
        self.save_file_db(file_content, extracted_text, course_id)

        # After saving to DB, create embeddings in FAISS
        self.store_vector(course_id, 1, extracted_text)

    # KANISHK
    def create_pdf_embedding(self, file_content):
        """
        Extracts text from a PDF file and returns it.
        """
        try:
            file_type = self.get_file_type(file_content)
            extracted_text = extract_text_and_images(file_type,file_content)
            if not extracted_text:
                raise ValueError("Failed to extract text from the given file.")
            
            # Save extracted text to MongoDB
            self.save_file_db(file_content, extracted_text, course_id)

            # After saving to DB, create embeddings in FAISS
            self.store_vector(self.create_vector(extracted_text),
                            {"file_content": file_content})
        except Exception as e:
            print(f"Error processing file: {e}")
            raise RuntimeError(f"Failed to process file: {e}")
  
    # 2. Save to MongoDB (Abstract Layer)
    # DEEP
    def save_file_db(self, file_content, extracted_text, course_id):
        """
        Saves the file and their extracted text to MongoDB.
        """
        self.mongodb.save_file(file_content, extracted_text, course_id)

    def delete_file_db(self, file, collection_name):
        """
        Deletes the file and extracted text from the specified MongoDB collection.
        """
        pass  # Logic to delete file and text in MongoDB goes here

    # 3. Vector Operations
    # SHREYAS
    def store_vector(self, course_id, document_id, extracted_text):
        """
        Stores a vector in the FAISS vector store with associated metadata.
        """
        self.chroma_db_manager.store_vector(course_id, document_id, extracted_text)

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

    def initialize_collections(self):
        """
        Initializes tables and loads data into MongoDB.
        """
        self.mongodb.initialize_collections()
