from pymongo import MongoClient
import gridfs
import os
from bson.binary import Binary
from dotenv import load_dotenv

load_dotenv()

class MongoDBHandler:
    def __init__(self):
        uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('MONGODB_DB_NAME')
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

    # initialize all collections
    def initialize_collections(self):
        self.create_users_collection()
        self.create_courses_collection()
        self.create_student_courses_collection()
        self.create_professor_courses_collection()
        self.create_course_material_metadata_collection()

    # function to save file and their extracted text to db
    def save_file(self, file_content, extracted_text, course_id):
        file_id = self.fs.put(file_content, course_id=course_id)
        
        course_material_metadata = {
            'file_id': file_id,
            'course_id': course_id,
            'actual_file': Binary(file_content),
            'extracted_text': extracted_text
        }
        self.db.course_material_metadata.insert_one(course_material_metadata)
        print("File uploaded successfully.")

    def login(self, username, hashed_password):
        user = self.db.users.find_one({"username": username, "hashed_password": hashed_password})
        return user