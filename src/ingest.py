import os
from dotenv import load_dotenv
from loader import load_document
from loader import split_document
from sqlalchemy import text
from langchain_core.documents import Document

import time

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")

def ingest_pdf(store):
    docs = load_document(PDF_PATH)

    splitted_docs = split_document(docs)

    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in splitted_docs
    ]    

    ids = [f"doc-{i}" for i in range(len(enriched))]

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

def reingest_pdf(store):
   ingest_pdf(store)

def total_documents(source: str, engine=None) -> int:
    """Verifica se as tabelas existem e retorna a quantidade de documentos."""

    with engine.connect() as conn:
        # Verifica se as tabelas do PGVector existem no schema public
        tables_exists = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name IN (
                      'langchain_pg_embedding',
                      'langchain_pg_collection'
                  )
            """)
        ).scalar_one()

        if tables_exists != 2:
            print("Tabelas do PGVector ainda não existem.")
            return 0

        # Verifica quantos chunks pertencem ao documento
        quantity = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM public.langchain_pg_embedding e
                JOIN public.langchain_pg_collection c
                  ON c.uuid = e.collection_id
                WHERE c.name = :collection
                  AND e.cmetadata ->> 'source' = :source
            """),
            {
                "collection": COLLECTION_NAME,
                "source": source,
            },
        ).scalar_one()

        return quantity

def delete_documents(source: str, engine=None) -> int:
    """Exclui somente os chunks do documento informado."""

    query = text("""
        DELETE FROM langchain_pg_embedding e
        USING langchain_pg_collection c
        WHERE c.uuid = e.collection_id
          AND c.name = :collection
          AND e.cmetadata ->> 'source' = :source
    """)

    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "collection": COLLECTION_NAME,
                "source": source,
            },
        )

        return result.rowcount

if __name__ == "__main__":
    ingest_pdf()