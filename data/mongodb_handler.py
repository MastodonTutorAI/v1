from pymongo import MongoClient, ASCENDING
import gridfs
import os
from bson.binary import Binary
from dotenv import load_dotenv
from bson.objectid import ObjectId
import bcrypt
from pymongo.errors import DuplicateKeyError
import re

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
        self.create_conversations_collection()

    def update_file(self, file_id, contents):
        try:
            status = contents['status']
            extracted_text = contents['extracted_text']
            
            is_homework = self.classify_homework_file(extracted_text)

            self.db.course_material_metadata.update_one(
                {'_id': file_id},
                {
                    '$set': {
                        'status': status, 
                        'extracted_text': extracted_text,
                        'is_homework': is_homework
                    }
                }
            )
            print("File status updated successfully.")
        except Exception as e:
            # Because of threading just print error
            print(f"Error creating course: {e}")

    def save_document_summary(self, file_id, summary):
        try:
            self.db.course_material_metadata.update_one(
                {'_id': file_id},
                {'$set': {'summary': summary}}
            )
            print("File status updated successfully.")
            return True
        except Exception as e:
            # Because of threading just print error
            print(f"Error creating course: {e}")
            return False

    # function to save file and their extracted text to db
    def save_file(self, file_content, course_id):
        try:
            course_material_metadata = {
                'course_id': course_id,
                'file_name': file_content.name,
                'actual_file': Binary(file_content.getvalue()),
                'extracted_text': '',
                'status': 'Processing',
                'available': False,
                'summary': 'None',
                'is_homework': False
            }
            self.db.course_material_metadata.insert_one(course_material_metadata)
            print("File uploaded successfully.")
            return course_material_metadata['_id']
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
            course = self.db.courses.find_one({'course_id': course_id})
            if course:
                print("Course already exists.")
                raise Exception(f"Course already exist by: {course['professor_name']}, please use different course Id.")
            course = {
                'course_id': course_id,
                'course_name': course_name,
                'professor_name': professor_name,
                'description': description,
                'professor_id': professor_id,
                'course_summary': ''
            }
            self.db.courses.insert_one(course)
            print("Course created successfully.")
            return course['course_id']
        except Exception as e:
            raise Exception(f"Error creating course: {e}")
    
    def set_course_summary(self, course_id, course_summary):
        try:
            self.db.courses.update_one(
                {'course_id': course_id},
                {'$set': {'course_summary': course_summary}}
            )

            print("Course summary updated successfully.")
            return True
        except Exception as e:
            print(f"Error creating course: {e}")
            return False

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

    def create_student_course(self, student_id, course_id):
        try:
            student_course = self.db.student_courses.find_one({'student_id': student_id})
            if student_course:
                existing_course_ids = student_course['course_id'].split(',')
                existing_course_ids.append(course_id)
                self.db.student_courses.update_one(
                    {'student_id': student_id},
                    {'$set': {'course_id': ','.join(existing_course_ids)}}
                )
                print("Course ID appended to existing student record.")
            else:
                new_student_course = {
                    'student_id': student_id,
                    'course_id': course_id
                }
                self.db.student_courses.insert_one(new_student_course)
                print("New student course record created successfully.")
        except Exception as e:
            raise Exception(f"Error creating student course: {e}")

    def get_courses(self, professor_id):
        try:
            courses = self.db.courses.find({'professor_id': professor_id})
            print("Retrieved courses successfully.")
            return courses
        except Exception as e:
            raise Exception(f"Error retrieving courses: {e}")

    def get_all_courses(self):
        try:
            courses = self.db.courses.find()
            print("Retrieved courses successfully.")
            return courses
        except Exception as e:
            raise Exception(f"Error retrieving courses: {e}")
        
    def get_student_courses(self, student_id):
        try:
            student_courses = self.db.student_courses.find({'student_id': student_id})
            all_course_ids = []
            for student_course in student_courses:
                course_ids = student_course['course_id'].split(',')
                all_course_ids.extend(course_ids)
                
            courses = self.db.courses.find({'course_id': {'$in': all_course_ids}})
            print("Fetched all course details successfully.")
            return courses

        except Exception as e:
            raise Exception(f"Error fetching course details: {e}")
    
    # function to save conversation to db
    def save_conversation(self, conversation_data):
        try:
            for conversation in conversation_data:
                # Remove 'status' before saving to the database
                conversation_to_save = {key: value for key, value in conversation.items() if key != "status"}

                if "conversation_id" not in conversation_to_save or not conversation_to_save.get("conversation_id"):
                    conversation_to_save["conversation_id"] = str(ObjectId())

                if conversation.get("status") == "New":
                    try:
                        # Insert new conversation
                        conversation_id = self.db.conversations.insert_one(conversation_to_save).inserted_id
                        print(f"New conversation inserted with ID: {conversation_id}")
                    except DuplicateKeyError:
                        print("Duplicate key error. Updating instead.")
                        self.db.conversations.update_one(
                            {"conversation_id": conversation_to_save["conversation_id"]},
                            {"$set": conversation_to_save}
                        )

                elif conversation.get("status") == "Updated":
                    # Update existing conversation based on conversation_id
                    if "_id" in conversation:
                        conversation_id = ObjectId(conversation["_id"])
                        result = self.db.conversations.update_one(
                            {"_id": conversation_id},
                            {"$set": conversation_to_save}
                        )
                        if result.matched_count > 0:
                            print(f"Conversation with ID {conversation_id} updated successfully.")
                        else:
                            print(f"Conversation with ID {conversation_id} not found for update.")
                    else:
                        raise ValueError("conversation_id is required for updating a conversation.")
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

    def get_conversation(self, course_id, user_id):
        try:
            conversation = self.db.conversations.find({'course_id': course_id, 'user_id': user_id})
            if conversation:
                print("Conversation retrieved successfully.")
                return conversation
            else:
                print("Conversation not found.")
                return None
        except Exception as e:
            raise Exception(f"Error retrieving conversation: {e}")

    def remove_course(self, course_id):
        try:
            # Delete course
            course_result = self.db.courses.delete_one({'course_id': course_id})
            if (course_result.deleted_count == 0):
                print("Course not found.")
                return False

            # Delete course material metadata
            metadata_result = self.db.course_material_metadata.delete_many({'course_id': course_id})
            print(f"Deleted {metadata_result.deleted_count} course material metadata documents.")

            # Delete files from GridFS
            files = self.db.course_material_metadata.find({'course_id': course_id})
            for file in files:
                self.fs.delete(file['_id'])
            print("Deleted associated files from GridFS.")

            # Delete conversations related to the course
            conversation_result = self.db.conversations.delete_many({'course_id': course_id})
            print(f"Deleted {conversation_result.deleted_count} conversations related to the course.")

            # Remove course_id from student_courses
            student_courses = self.db.student_courses.find({'course_id': {'$regex': f'.*{course_id}.*'}})
            for student_course in student_courses:
                course_ids = student_course['course_id'].split(',')
                if course_id in course_ids:
                    course_ids.remove(course_id)
                    self.db.student_courses.update_one(
                        {'student_id': student_course['student_id']},
                        {'$set': {'course_id': ','.join(course_ids)}}
                    )
            print("Removed course_id from student_courses.")

            print("Course removed successfully.")
            return True
        except Exception as e:
            raise Exception(f"Error removing course: {e}")

    def set_assistant_available(self, course_id, course_summary, file_id, document_summary, value):
        try:
            # Update the availability status for the given file_id
            result = self.db.course_material_metadata.update_one(
                {'_id': file_id},
                {'$set': {'available': value}}
            )
            
            if result.matched_count == 0:
                print("File not found.")
                return False

            if value:  # Add document summary
                updated_summary = course_summary + "\n" + document_summary
            else:  # Remove document summary
                updated_summary = course_summary.replace(document_summary, "").strip()

            # Save the updated course summary
            self.set_course_summary(course_id, updated_summary)

            print("Availability status updated successfully.")
            return True
        except Exception as e:
            raise Exception(f"Error updating availability status: {e}")

    def remove_file(self, file_id):
        try:
            # Find the file in the course_material_metadata collection
            file = self.db.course_material_metadata.find_one({'_id': file_id})
            if not file:
                print("File not found.")
                return False
    
            # Delete the file from GridFS
            self.fs.delete(file_id)
            print("File deleted from GridFS.")
    
            # Remove the file metadata from the course_material_metadata collection
            result = self.db.course_material_metadata.delete_one({'_id': file_id})
            if result.deleted_count == 0:
                print("File metadata not found.")
                return False
    
            print("File metadata removed successfully.")
            return True
        except Exception as e:
            raise Exception(f"Error removing file: {e}")
        
    def classify_homework_file(self, extracted_text):
        try:
            print("Starting classification process...")
            homework_keywords = ["assignment", "homework", "due date", "submit", "quiz"]
            
            # Combine list of strings into one string if extracted_text is a list
            if isinstance(extracted_text, list):
                print("Extracted text is a list. Joining all items into a single string...")
                extracted_text = " ".join(extracted_text)

            # Convert extracted text to lowercase for case-insensitive matching
            print(f"Extracted text: {extracted_text}")
            extracted_text_lower = extracted_text.lower()

            # Use regular expressions to match exact keywords
            is_homework = any(
                re.search(rf'\b{keyword}\b', extracted_text_lower) for keyword in homework_keywords
            )
            if is_homework:
                print("The file is classified as Homework/Assignment.")
            else:
                print("The file does not contain homework-related keywords and is classified as Study Material.")

            return is_homework
        except Exception as e:
            print(f"Error during classification: {e}")
            return False
    
    def get_homework_file_ids(self, course_id):
        try:
            # Query the database for homework files and return only the '_id' field
            homework_file_ids = self.db.course_material_metadata.find(
                {'course_id': course_id, 'is_homework': True},
                {'_id': 1}
            )
            
            # Convert cursor to a list of _id values as strings
            homework_ids = [str(file['_id']) for file in homework_file_ids]
            
            print(f"Retrieved homework file IDs successfully: {homework_ids}")
            return homework_ids
        except Exception as e:
            raise Exception(f"Error retrieving homework files: {e}")