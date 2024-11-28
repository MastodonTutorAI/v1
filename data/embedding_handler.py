from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv

load_dotenv()

class ChromaDBManager:
    def __init__(self, base_dir=None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db'))
        self.chroma_base_dir = base_dir
        self.embeddings_model = OpenAIEmbeddings()
        self.course_db_map = {}
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
        course_db_name = f'chroma_course_{course_id}'
        course_db = self.course_db_map.get(course_db_name)
        if course_db is None:
            raise ValueError(f"Chroma DB for course ID {course_id} not found.")
        return course_db

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
        except Exception as e:
            raise RuntimeError(e)
        
    def change_availability(self, course_id, document_id, available):
        """Change the availability of a document in the Chroma database."""
        try:
            course_db = self.get_course_db(course_id)
            results = course_db.get(where={"document_id": document_id})

            if not results or not results['ids']:
                print(f"Document ID {document_id} not found in Chroma DB for course ID {course_id}.")
                return
            
            updated_metadata = [{"available": available, **metadata} for metadata in results['metadatas']] 

            ids_to_delete = results['ids']
            course_db.delete(ids=ids_to_delete)

            course_db.add_texts(texts=results['documents'], metadatas=updated_metadata, embeddings=results['embeddings'], ids=ids_to_delete)
            print(f"Availability of document ID Changed Successfully: {document_id}")
        except Exception as e:
            raise RuntimeError(f"Error changing availability: {e}")

    def search_vector(self, course_id, query_text, k=3,filters={"available": True}):
        """Search for similar vectors in the Chroma database based on the query text."""
        try:
            query_text = str(query_text)
            course_db = self.get_course_db(course_id)
            return course_db.similarity_search(query_text, k,filter=filters)
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


# db = ChromaDBManager()
# extracted_text = "The quick brown fox jumps over the lazy dog."
# #db.create_course_db(2)
# db.store_vector(2, 1, extracted_text)
# db.change_availability(2, 1, False)
# result = db.search_vector(2, "quick", k=3,filters={"available": True})
# for i, item in enumerate(result, start=1):
#      print(f"Result {i}:")
#      print(f"Document ID: {item.metadata.get('document_id')}")
#      print(f"Available: {item.metadata.get('available')}")
#      print(f"Content Snippet:\n{item.page_content}\n")
# #db.remove_vector(2, 1)
