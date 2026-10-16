import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

def get_chat_model():
    chatModel = init_chat_model(model=os.getenv("GOOGLE_LLM_MODEL","gemini-3.6-flash"), model_provider="google_genai")

    return chatModel