import spacy
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import sqlite3
from dotenv import load_dotenv
    
load_dotenv()
class ChromaDBManager:
    def __init__(self, base_dir=None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db'))
        self.chroma_base_dir = base_dir
        self.embeddings_model = OpenAIEmbeddings()
        self.course_db_map = {}
        self.nlp = spacy.load("en_core_web_sm")
        self._initialize_course_db_map()

    def _initialize_course_db_map(self):
        """Initialize the Chroma databases for each course in the base directory."""
        if not os.path.exists(self.chroma_base_dir):
            os.makedirs(self.chroma_base_dir)

        for course_dir in os.listdir(self.chroma_base_dir):
            course_path = os.path.join(self.chroma_base_dir, course_dir)
            if os.path.isdir(course_path):
                try:
                    chroma_instance = Chroma(embedding_function=self.embeddings_model, persist_directory=course_path)
                    self.course_db_map[course_dir] = chroma_instance
                except Exception as e:
                    raise RuntimeError(e) 

    def create_course_db(self, course_id):
        """Create a Chroma database for a new course."""
        try:
            course_dir = os.path.join(self.chroma_base_dir, f"chroma_course_{course_id}")
            if not os.path.exists(course_dir):
                os.makedirs(course_dir)
            
            chroma_store = Chroma(embedding_function=self.embeddings_model, persist_directory=course_dir)
            return chroma_store
        except Exception as e:
            raise RuntimeError(e) 

    def get_course_db(self, course_id):
        """Fetch the Chroma DB instance for a given course."""
        course_db_name = f"chroma_course_{course_id}"
        if course_db_name not in self.course_db_map:
            db_path = os.path.join("data", "chroma_db", course_db_name, "chroma.sqlite3")
            self.course_db_map[course_db_name] = sqlite3.connect(db_path)
        return self.course_db_map[course_db_name]

    def get_chunks(self, text, document_id, chunk_size=1000, chunk_overlap=128):
        """Split text into chunks and create metadata for each chunk."""
        text = str(text)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        try:
            chunks = text_splitter.split_text(text)
            metadata = [{"available": False, "document_id": document_id} for _ in chunks]
            return chunks, metadata
        except Exception as e:
            raise RuntimeError(e) 

    def create_embeddings(self, chunks, metadatas, course_db):
        """Generate embeddings and save them to the Chroma database."""
        try:
            embeddings = [self.embeddings_model.embed_query(chunk) for chunk in chunks]
            course_db.add_texts(texts=chunks, metadatas=metadatas, embeddings=embeddings)
        except Exception as e:
            raise RuntimeError(e)

    def store_vector(self, course_id, document_id, extracted_text):
        """Store extracted text as embeddings in the course-specific Chroma database."""
        try:
            course_db = self.get_course_db(course_id)
            chunks, metadata = self.get_chunks(extracted_text, document_id)
            self.create_embeddings(chunks, metadata, course_db)
            print("Embeddings are created successfully.")
        except Exception as e:
            raise RuntimeError(e)
        
    def change_availability(self, course_id, document_id, available):
        """
        Change the availability of a document in the Chroma database using langchain_chroma.
        
        Args:
            course_id (str): The ID of the course
            document_id (str): The ID of the document to update
            available (bool): The new availability status
        """
        try:
            course_db = self.get_course_db(course_id)
            # Get all entries matching the document_id
            results = course_db.get(where={"document_id": document_id})
            
            if not results or not results['ids']:
                print(f"Document ID {document_id} not found in Chroma DB for course ID {course_id}.")
                return
            
            # Delete existing entries
            course_db.delete(ids=results['ids'])
            
            # Recreate entries with updated metadata
            texts = results['documents']
            embeddings = results['embeddings']
            updated_metadata = [{
                "available": available,
                "document_id": document_id
            } for _ in texts]
            
            # Add texts back with updated metadata
            course_db.add_texts(
                texts=texts,
                metadatas=updated_metadata,
                embeddings=embeddings
            )
            
            print(f"Availability of document ID {document_id} changed successfully.")
        except Exception as e:
            raise RuntimeError(f"Error changing availability: {e}")

    def is_question_related(self, query_text, course_id, similarity_threshold=0.2):
        """
        Determine if a query is both a valid question and related to the course PPTs.

        Args:
            query_text (str): The user's query.
            course_id (str): The course ID to search in the Chroma DB.
            similarity_threshold (float): Threshold for determining relevance.

        Returns:
            bool: True if the query is valid and related, False otherwise.
        """
        try:
            # Step 1: Check if the query is a question
            question_words = {'who', 'what', 'why', 'where', 'when', 'how', 'which', 'whose', 'whom', 'explain', 'describe', 'define', 'list', 'solve', 'give', 'want', 'use'}
            doc = self.nlp(query_text)
            
            # Check for common question patterns
            is_question = any(token.text.lower() in question_words for token in doc) or query_text.endswith('?')

            if not is_question:
                return False  # Not a valid question

            # Step 2: Perform a semantic relevance check with Chroma DB
            course_db = self.get_course_db(course_id)
            results = course_db.similarity_search(query_text, k=1, filter={"available": True})

            if results and len(results) > 0:
                top_result = results[0]
                similarity_score = top_result.metadata.get("similarity_score", 1)
                if similarity_score >= similarity_threshold:
                    return True  # Question is related

            return False  # Question is not related
        except Exception as e:
            raise RuntimeError(f"Error in determining if query is valid and related: {e}")
        
    def search_vector(self, course_id, query_text, k=3, filters={"available": True}):
        """Search for similar vectors in the Chroma database based on the query text."""
        try:
            query_text = str(query_text)
            if not self.is_question_related(query_text,course_id):
                print("Unrelated question.")
                return "No Context"
            course_db = self.get_course_db(course_id)
            results = course_db.similarity_search(query_text, k, filter=filters)
            return [result.page_content.split('\n') for result in results]
        except Exception as e:
            raise RuntimeError(e)
        
    def remove_vector(self, course_id, document_id):
        """Remove a vector from the Chroma database and delete the course folder if no embeddings remain."""
        try:
            course_db = self.get_course_db(course_id)
            
            # Retrieve all embeddings associated with the specified document ID
            ids_to_delete = course_db.get(where={"document_id": document_id})
            if 'ids' in ids_to_delete:
                ids_to_delete = ids_to_delete['ids']
            else:
                ids_to_delete = []

            # Delete the embeddings if any IDs were found
            if ids_to_delete:
                course_db.delete(ids=ids_to_delete)
                print(f"Embeddings for document_id {document_id} removed from Chroma DB.")
                remaining_embeddings = course_db.get( where={"document_id": document_id})
                if 'ids' in remaining_embeddings and not remaining_embeddings['ids']:
                    print(f"Verified that all embeddings for document_id {document_id} have been removed for course_id {course_id}.")
                else:
                    print(f"Some embeddings for document_id {document_id} remain in Chroma DB of course_id {course_id}.")
            else:
                print(f"No embeddings found for document_id {document_id} in Chroma DB.")
        except Exception as e:
            raise RuntimeError(e)
    
    def search_vector_by_document_id(self, query_text, course_id, document_ids, k=5):
        """
        Search for similar vectors in the Chroma database based on the document_ids.
        
        Args:
            course_id (str): The course ID to search in the Chroma DB.
            document_ids (list): The document IDs to filter by.
            k (int): Number of top results to retrieve.

        Returns:
            list: relevant results based on the document_ids.
        """
        try:
            query_text = str(query_text)
            course_db = self.get_course_db(course_id)

            results = course_db.similarity_search(query_text, k=k, filter={"document_id": {"$in": document_ids}})
            return results
        except Exception as e:
            raise RuntimeError(f"Error searching vectors by document_id: {e}")

# db = ChromaDBManager()
# extracted_text = "The quick brown fox jumps over the lazy dog."
#db.create_course_db(3)
#db.store_vector(3, 1, extracted_text)
# db.change_availability(3, 1, True)
# result = db.search_vector(3, "over", k=5,filters={"available": True})
# for i, item in enumerate(result, start=1):
#      print(f"Result {i}:")
#      print(f"Content Snippet:\n{item}\n")
#db.remove_vector(3, 1)
