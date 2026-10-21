import os

from search import vetorial_search_prompt, llm_interaction
from ingest import PDF_PATH, ingest_pdf,reingest_pdf, total_documents
from embeding_model import get_embedding_model
from vector_store import get_store
from loader import load_document, split_document
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def main():
    embeddings = get_embedding_model()
    store = get_store(embeddings)
    docs = load_document(PDF_PATH)
    splitted_docs = split_document(docs)
    source = str("./document.pdf")
    totalDocuments = total_documents(source, engine)

    if (totalDocuments == 0):
        print("Nenhum documento encontrado. Executando a ingestão...")
        ingest_pdf(store)
        totalDocuments = total_documents(source, engine)

    print(totalDocuments, "documentos encontrados no banco de dados.")
    print(len(splitted_docs), "documentos carregados do PDF.")

    if (totalDocuments != len(splitted_docs)):
        print("Vetor desatualizado. Re-executando a ingestão...")
        reingest_pdf(store)
    else:
        print(f"Vetor atualizado com {totalDocuments} documentos de {len(splitted_docs)} carregados do pdf. Nenhuma ação necessária.")

    userQuestion = ""
    
    while userQuestion.lower() != "sair":
        userQuestion = input("\nQual informação gostaria de saber? Digite 'sair' para encerrar:\n ")
        if userQuestion.lower() == "sair":
            print("Encerrando o programa.")
            break

        results = vetorial_search_prompt(userQuestion)

        llmAnswer = llm_interaction(contexto=results, pergunta=userQuestion)

        print("Resposta do modelo:")
        print(llmAnswer.content[0].get('text', ''))
  
if __name__ == "__main__":
    main()