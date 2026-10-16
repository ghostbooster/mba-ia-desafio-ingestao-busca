import os
from embeding_model import get_embedding_model
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):
    embeddings = get_embedding_model()

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    results = store.similarity_search_with_score(question, k=10)

    for i, (doc, score) in enumerate(results, start=1):
      print("="*50)
      print(f"Resultado {i} (score: {score:.2f}):")
      print("="*50)

      print("\nTexto:\n")
      print(doc.page_content.strip())

      print("\nMetadados:\n")
      for k, v in doc.metadata.items():
          print(f"{k}: {v}")

promptTemplate = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

prompt = promptTemplate.format(
    contexto="Wesley", pergunta="Qual é a capital da França?"
)

print(prompt)

#search_prompt(prompt)