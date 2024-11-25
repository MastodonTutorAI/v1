from pymongo import MongoClient, ASCENDING
import gridfs
import os
from bson.binary import Binary
from dotenv import load_dotenv
from bson.objectid import ObjectId
import bcrypt

load_dotenv()

class MongoDBHandler:
    def __init__(self):
        uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DB_NAME')
        if not uri or not db_name:
            raise ValueError("MONGODB_URI and MONGODB_DB_NAME must be set in the .env file")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.fs = gridfs.GridFS(self.db)

    # functions to create collections
    def create_users_collection(self):
        self.db.create_collection("users")
        print("Users collection created successfully.")

    def create_courses_collection(self):
        self.db.create_collection("courses")
        print("Courses collection created successfully.")

    def create_student_courses_collection(self):
        self.db.create_collection("student_courses")
        print("Student courses collection created successfully.")

    def create_professor_courses_collection(self):
        self.db.create_collection("professor_courses")
        print("Professor courses collection created successfully.")

    def create_course_material_metadata_collection(self):
        self.db.create_collection("course_material_metadata")
        print("Course material metadata collection created successfully.")
        
    def create_conversations_collection(self):
        self.db.create_collection("conversations")
        self.db.conversations.create_index([("conversation_id", ASCENDING)], unique=True)
        print("Conversations collection created successfully with indexes.")

    # initialize all collections
    def initialize_collections(self):
        self.create_users_collection()
        self.create_courses_collection()
        self.create_student_courses_collection()
        self.create_professor_courses_collection()
        self.create_course_material_metadata_collection()

    # function to save file and their extracted text to db
    def save_file(self, file_content, extracted_text, course_id):
        try:
            file_id = self.fs.put(file_content, course_id=course_id)
            
            course_material_metadata = {
                'file_id': file_id,
                'course_id': course_id,
                'file_name': file_content.name,
                'actual_file': Binary(file_content.getvalue()),
                'extracted_text': extracted_text,
                'available': False
            }
            self.db.course_material_metadata.insert_one(course_material_metadata)
            print("File uploaded successfully.")
            return file_id
        except Exception as e:
            raise Exception(f"Error saving file: {e}")
    
    def hash_password(self, password):
        """
        Hashes a password using bcrypt.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, password, hashed_password):
        """
        Verifies a password against a hashed password.
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def login(self, username, password):
        try:
            user = self.db.users.find_one({"username": username})
            if user and self.verify_password(password, user["hashed_password"]):
                print("Login successful.")
                return user
            else:
                print("Login failed: Invalid username or password.")
                return None
        except Exception as e:
            raise Exception(f"Error during login: {e}")
    
    def get_files(self, course_id):
        try:
            course_material_metadata = self.db.course_material_metadata.find({'course_id': course_id})
            print("Retrieved files successfully.")
            return course_material_metadata
        except Exception as e:
            raise Exception(f"Error retrieving files: {e}")
    
    def create_course(self, course_id, course_name, professor_name, description, professor_id):
        try:
            course = {
                'course_id': course_id,
                'course_name': course_name,
                'professor_name': professor_name,
                'description': description,
                'professor_id': professor_id
            }
            self.db.courses.insert_one(course)
            print("Course created successfully.")
            return course['course_id']
        except Exception as e:
            raise Exception(f"Error creating course: {e}")
    
    def create_professor_course(self, professor_id, course_id):
        try:
            professor_course = {
                'professor_id': professor_id,
                'course_id': course_id
            }
            self.db.professor_courses.insert_one(professor_course)
            print("Professor course created successfully.")
        except Exception as e:
            raise Exception(f"Error creating professor course: {e}")

    def get_courses(self, professor_id):
        try:
            courses = self.db.courses.find({'professor_id': professor_id})
            print("Retrieved courses successfully.")
            return courses
        except Exception as e:
            raise Exception(f"Error retrieving courses: {e}")
    
    # function to save conversation to db
    def save_conversation(self, conversation_data):
        try:
            conversation_id = self.db.conversations.insert_one(conversation_data).inserted_id
            print("Conversation saved successfully.")
            return conversation_id
        except Exception as e:
            raise Exception(f"Error saving conversation: {e}")

    # function to remove conversation from db
    def remove_conversation(self, conversation_id):
        try:
            result = self.db.conversations.delete_one({'_id': ObjectId(conversation_id)})
            if result.deleted_count > 0:
                print("Conversation removed successfully.")
                return True
            else:
                print("Conversation not found.")
                return False
        except Exception as e:
            raise Exception(f"Error removing conversation: {e}")

    def remove_course(self, course_id):
        try:
            # Delete course
            course_result = self.db.courses.delete_one({'course_id': course_id})
            if course_result.deleted_count == 0:
                print("Course not found.")
                return False

            # Delete course material metadata
            metadata_result = self.db.course_material_metadata.delete_many({'course_id': course_id})
            print(f"Deleted {metadata_result.deleted_count} course material metadata documents.")

            # Delete files from GridFS
            files = self.db.course_material_metadata.find({'course_id': course_id})
            for file in files:
                self.fs.delete(file['file_id'])
            print("Deleted associated files from GridFS.")

            print("Course removed successfully.")
            return True
        except Exception as e:
            raise Exception(f"Error removing course: {e}")

    def set_assistant_available(self, file_id, value):
        try:
            # Update the availability status for the given file_id
            result = self.db.course_material_metadata.update_one(
                {'file_id': file_id},
                {'$set': {'available': value}}
            )
            
            if result.matched_count == 0:
                print("File not found.")
                return False
    
            print("Availability status updated successfully.")
            return True
        except Exception as e:
            raise Exception(f"Error updating availability status: {e}")

    def remove_file(self, file_id):
        try:
            # Find the file in the course_material_metadata collection
            file = self.db.course_material_metadata.find_one({'file_id': file_id})
            if not file:
                print("File not found.")
                return False
    
            # Delete the file from GridFS
            self.fs.delete(file_id)
            print("File deleted from GridFS.")
    
            # Remove the file metadata from the course_material_metadata collection
            result = self.db.course_material_metadata.delete_one({'file_id': file_id})
            if result.deleted_count == 0:
                print("File metadata not found.")
                return False
    
            print("File metadata removed successfully.")
            return True
        except Exception as e:
            raise Exception(f"Error removing file: {e}")
