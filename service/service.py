import os
import sys
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.file_processor import extract_text_and_images
from data.mongodb_handler import MongoDBHandler
from data.embedding_handler import ChromaDBManager
from utils import groq_util_module as groq_model

class Service:

    def __init__(self):
        self.mongodb = MongoDBHandler()
        self.chroma_db_manager = ChromaDBManager()
        self.summarizer = groq_model.GroqCorseSummarizer(self.mongodb)
        self.quiz_generator = groq_model.GroqQuizGenerator()
        print('Service initialized')
    
    def set_course_details(self, course_details):
        """Sets the course details including ID, summary, and name"""
        self.course_id = course_details['course_id']
        self.course_summary = course_details['course_summary']
        self.course_name = course_details['course_name']

    #Embedding Creation
    def save_file(self, file_content):
        # Saves the file content and starts a thread to create embeddings
        file_id = self.save_file_db(file_content, self.course_id)

        # Start thread to complete remaining process
        threading.Thread(target=self.create_embedding, args=(file_id, file_content)).start()
    
    def create_embedding(self, file_id, file_content):
        """
        Generates embeddings for different file types like PDF, text, pptx, etc.
        After extracting text from the document, the text is stored in MongoDB.
        Then, embeddings are created and stored in Chroma.
        """
        extracted_text = ''
        try:
            print('__**In thread: Create Embeddings...**__')
            extracted_text = extract_text_and_images(file_content)
            if not extracted_text:
                raise ValueError("Failed to extract text from the given file.")

            print("**Extracted Text: "+str(file_id)+"**")
            
            # After saving to DB, create embeddings in Chroma
            self.store_vector(course_id=self.course_id, document_id=str(file_id), extracted_text=extracted_text)
            print("**Embeddings Created: "+str(file_id)+"**")
            
            # Create document summary
            self.summarizer.save_document_summary(file_id, extracted_text)
            print("**Document Summary Created: "+str(file_id)+"**")

            # Save extracted text to MongoDB
            self.update_file_db(file_id, extracted_text, 'Completed')
            print('__**In thread: Completed...**__')
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            # Save status failed
            self.update_file_db(file_id, extracted_text if extracted_text else '', 'Failed')
        
    #Save to MongoDB (Abstract Layer)
    def initialize_collections(self):
        """
        Initializes tables and loads data into MongoDB.
        """
        self.mongodb.initialize_collections()

    def save_file_db(self, file_content, course_id):
        """
        Saves the file and their extracted text to MongoDB.
        """
        return self.mongodb.save_file(file_content, course_id)

    def update_file_db(self, file_id, extracted_text, status):
        """Updates the file status and extracted text in MongoDB"""
        contents = {}
        contents['status'] = status
        contents['extracted_text'] = extracted_text
        self.mongodb.update_file(file_id, contents)

    def get_file_db(self, course_id):
        """
        Retrieves the file and extracted text from the specified MongoDB collection.
        """
        return self.mongodb.get_files(course_id)

    def create_course(self, course_id, course_name, professor_name, description, professor_id):
        """
        Creates a new course in MongoDB.
        """
        course_id = self.mongodb.create_course(
            course_id, course_name, professor_name, description, professor_id)
        if course_id:
            self.chroma_db_manager.create_course_db(course_id=course_id)
            self.chroma_db_manager._initialize_course_db_map()
        return course_id

    def get_courses(self, professor_id):
        """
        Retrieves all courses from MongoDB.
        """
        return self.mongodb.get_courses(professor_id)

    def get_all_courses(self):
        """Retrieves all courses from MongoDB"""
        return self.mongodb.get_all_courses()

    def get_student_courses(self, student_id):
        """
        Retrieves all courses for the given student ID
        """
        return self.mongodb.get_student_courses(student_id)

    def delete_file(self, file_id):
        """
        Deletes the file and extracted text from the specified MongoDB collection.
        """
        self.remove_vector(file_id=file_id)
        return self.mongodb.remove_file(file_id)

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

    def get_conversation(self, user_id):
        """
        Retrieves a conversation from MongoDB.
        """
        return self.mongodb.get_conversation(self.course_id, user_id)

    def remove_course(self):
        """
        Removes course and metadata from MongoDB.
        """
        return self.mongodb.remove_course(self.course_id)

    def set_assistant_available(self, file_id, document_summary, value):
        """Sets the availability of the assistant for a document"""
        self.chroma_db_manager.change_availability(
            course_id=self.course_id, document_id=str(file_id), available=value)
        return self.mongodb.set_assistant_available(self.course_id, self.course_summary, file_id, document_summary, value)

    def create_student_course(self, user_id, course_id):
        """Creates a student-course association in MongoDB"""
        self.mongodb.create_student_course(user_id, course_id)

    #Vector Operations
    def store_vector(self, course_id, document_id, extracted_text):
        """
        Stores a vector in the chroma vector store with associated metadata.
        """
        self.chroma_db_manager.store_vector(
            course_id, document_id, extracted_text)

    def search_vector(self, query_text, top_k=5):
        """
        Searches for similar vectors in the Chroma vector store based on the query vector.
        """
        print(f"Searching vector for {query_text}...")
        return self.chroma_db_manager.search_vector(course_id=self.course_id, query_text=query_text, k=top_k)

    def remove_vector(self, file_id):
        """Removes a vector from ChromaDB"""
        self.chroma_db_manager.remove_vector(
            course_id=self.course_id, document_id=str(file_id))

    def get_model_conversation(self):
        """Retrieves a conversation model for the course"""
        course_id = self.course_id
        homework_files_ids = self.get_homework_file_ids()
        return groq_model.GroqConversationManager(service=self, course_name=self.course_name,course_summary= self.course_summary, course_id=course_id, homework_files_ids=homework_files_ids)
    
    def get_homework_file_ids(self):
        """Retrieves homework file IDs for the course"""
        return self.mongodb.get_homework_file_ids(self.course_id)

