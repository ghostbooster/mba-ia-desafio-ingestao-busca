import os
from dotenv import load_dotenv
from langchain_postgres import PGVector

load_dotenv()

def get_store(embeddings):
    return PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )