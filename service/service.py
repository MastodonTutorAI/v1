import os
import sys

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.mongodb_handler import MongoDBHandler

class Service:
    
    def __init__(self, faiss_index = ""):
        """
        Initialize the Service class with MongoDB client and FAISS index for vector storage.
        """
        self.mongodb = MongoDBHandler()  # MongoDB instance
        self.vector_store = faiss_index  # FAISS instance to store vectors
        print('Service initialized')

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
        self.store_vector(self.create_vector(extracted_text), {"file_content": file_content})

    #KANISHK 
    def create_pdf_embedding(self, file_path):
        """
        Extracts text from a PDF file and returns it.
        """
        # Logic to extract text from PDF goes here
        # Extract text from Image
        pass
    
    #ALISHA 
    def create_text_embedding(self, file_path):
        """
        Extracts text from a text file and returns it.
        """
        # Logic to extract text from a text file goes here
        pass
    
    #ALISHA 
    def create_pptx_embedding(self, file_path):
        """
        Extracts text from a PPTX file and returns it.
        """
        # Logic to extract text from a PPTX file goes here
        # Extract text from Image
        pass

    # 2. Save to MongoDB (Abstract Layer)
    #DEEP
    def save_file_db(self, file_content, extracted_text, course_id):
        """
        Saves the file and their extracted text to MongoDB.
        """
        self.mongodb.save_file(file_content, extracted_text, course_id)
    
    def delete_file_db(self, file, collection_name):
        """
        Saves the file and extracted text to the specified MongoDB collection.
        """
        # Logic to save file and text in MongoDB goes here
        pass

    # 3. Vector Operations
    #SHREYAS
    def store_vector(self, vector, metadata):
        """
        Stores a vector in the FAISS vector store with associated metadata.
        """
        self.vector_store.add_vector(vector, metadata)

    #RAHUL
    def search_vector(self, query_vector):
        """
        Searches for similar vectors in the FAISS vector store based on the query vector.
        """
        return self.vector_store.search(query_vector)

    #SHREYAS
    def remove_vector(self, vector_id):
        """
        Removes a vector from the FAISS vector store.
        """
        self.vector_store.remove(vector_id)

    # 4. MongoDB Operations for Conversations
    #DEEP
    def fetch_conversation(self, user_id):
        """
        Fetches conversation history for the current user from MongoDB.
        """
        # Logic to fetch user conversation from MongoDB
        pass
    
    #DEEP
    def save_conversation(self, user_id, conversation):
        """
        Saves the current conversation for the current user in MongoDB.
        """
        # Logic to save the current conversation in MongoDB
        pass

    # 5. Create prompt using chat history
    #DEEP/AJINKYA
    def create_prompt(self, user_id, current_question):
        """
        Creates a prompt by combining the user's chat history and the current question.
        """
        chat_history = self.fetch_conversation(user_id)
        # Combine chat history and current question to form the prompt
        prompt = chat_history + "\nQ: " + current_question
        return prompt

    # 6. Set Default Prompt
    def set_default_prompt(self):
        """
        Sets a default prompt if no conversation history is found.
        """
        return "Default prompt to use if no chat history exists."

    # 7. Call Model API for Response
    #AJINKYA
    def get_response(self, prompt):
        """
        Calls the model API to get a response based on the given prompt.
        """
        # Logic to call a model API (e.g., OpenAI GPT, Hugging Face model) to get a response
        response = self.model.query(prompt)
        return response

    # Additional Embedding Functions
    #SHREYAS
    def create_vector(self, text):
        """
        Creates vector embeddings for the given text.
        """
        # Logic to convert the text into vector embeddings
        pass
    
    def initialize_collections(self):
        """"
        To initialize tables and load data in mongodb
        """     
        self.mongodb.initialize_collections()
               
# To load data for development purpose.
file_service = Service()
file_service.initialize_collections()