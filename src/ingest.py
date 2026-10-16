import os
from dotenv import load_dotenv
from loader import load_document
from loader import split_document
from langchain_postgres import PGVector
from langchain_core.documents import Document
from embeding_model import get_embedding_model
import time

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")

def ingest_pdf():
    docs = load_document(PDF_PATH)

    splitted_docs = split_document(docs)

    embeddings = get_embedding_model()

    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in splitted_docs
    ]    

    ids = [f"doc-{i}" for i in range(len(enriched))]

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    batch_size = 5

    for i in range(0, len(enriched), batch_size):
        batch_docs = enriched[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        
        try:
            print(f"Processando lote de {i} até {i + len(batch_docs)}...")
            
            # Envia um pedaço pequeno para o PGVector (que chama a API do Gemini controladamente)
            store.add_documents(documents=batch_docs, ids=batch_ids)
            
            # Pausa de 3 segundos entre os lotes para respeitar a cota gratuita da API
            time.sleep(3)
            
        except Exception as e:
            print(f"Erro no lote {i}: {e}")
            print("Aguardando 15 segundos para tentar novamente...")
            time.sleep(15)
            # Tenta reenviar o lote caso tenha sido bloqueio temporário
            store.add_documents(documents=batch_docs, ids=batch_ids)

if __name__ == "__main__":
    ingest_pdf()