from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH")
MODEL_PATH = os.getenv("MODEL_PATH")
