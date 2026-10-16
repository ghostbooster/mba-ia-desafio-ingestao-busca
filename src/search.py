import os
from embeding_model import get_embedding_model
from chat_model import get_chat_model
from langchain_core.prompts import ChatPromptTemplate
from vector_store import get_store
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

def vetorial_search_prompt(question=None):
    embeddings = get_embedding_model()

    store = get_store(embeddings)

    results = store.similarity_search_with_score(question, k=10)

    return results

def llm_interaction(contexto=None, pergunta=None):
    chatModel = get_chat_model()

    promptTemplate = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    prompt = promptTemplate.format(
        contexto=contexto, pergunta=pergunta
    )

    modelAnswer = chatModel.invoke(prompt)

    return modelAnswer
