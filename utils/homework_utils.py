from sentence_transformers import CrossEncoder  
from data.mongodb_handler import MongoDBHandler
from data.embedding_handler import ChromaDBManager

class HomeworkUtils:
    def __init__(self, course_id, homework_files_ids):
        """
        Initialize the HomeworkUtils class with necessary dependencies.
        
        :param course_id: The ID of the course
        :param chroma_db_manager: An instance of ChromaDBManager for vector search
        :param mongodb: An instance of MongoDB handler for accessing homework file IDs
        """
        self.course_id = course_id
        self.chroma_db_manager = ChromaDBManager()
        self.mongodb = MongoDBHandler()
        self.homework_files_ids = homework_files_ids
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-TinyBERT-L-6")

    def cross_encoder_similarity_batch(self, user_query, chunks):
        """
        Perform batch similarity comparison using a cross-encoder model.

        :param user_query: The user's query
        :param chunks: A list of chunks to compare against the query
        :return: True if any chunk is highly relevant, False otherwise
        """
        pairs = [(user_query, chunk) for chunk in chunks]
        scores = self.cross_encoder.predict(pairs)  # Batch processing
        percentage_scores = [round(score * 100, 2) for score in scores]
        print("Relevance Scores in %:", percentage_scores)
        
        for i, score in enumerate(percentage_scores):
            if score > 50:
                return True
        return False

    def is_homework_query(self, user_query):
        """
        Check if the user query is related to homework or not.
        
        :param user_query: The user's query to check
        :return: True if the query is related to homework, False otherwise
        """
        search_results = self.search_vector_homework(user_query, top_k=10)
        chunks = [result.page_content for result in search_results]
        return self.cross_encoder_similarity_batch(user_query, chunks)

    def search_vector_homework(self, query_text, top_k=5):
        """
        Searches for similar vectors in the ChromaDB vector store based on the query.
        
        :param query_text: The query text to search for
        :param top_k: The number of top results to retrieve
        :return: A list of search results
        """
        homework_files_ids = self.homework_files_ids
        return self.chroma_db_manager.search_vector_by_document_id(
            course_id=self.course_id,
            query_text=query_text,
            k=top_k,
            document_ids=homework_files_ids
        )

    def search_vector_homework_with_scores(self, query_text, top_k=5):
        """
        Executes a similarity search with scores on the ChromaDB vector store.

        :param query_text: The query text to search for
        :param top_k: The number of top results to retrieve
        :return: A list of tuples with results and their similarity scores
        """
        homework_files_ids = self.homework_files_ids
        results = self.chroma_db_manager.similarity_search_with_score(
            query_text,
            k=top_k,
            filter={"document_id": {"$in": homework_files_ids}}
        )
        print("Similarity Search Results with Scores:")
        for res, score in results:
            print(f"* [SIM={score:.3f}] {res.page_content} [{res.metadata}]")
        return False
