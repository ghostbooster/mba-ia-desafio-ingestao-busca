from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_document(path):
    loader = PyPDFLoader(path)
    docs = loader.load()
    return docs

def split_document(docs,chunk_size=1000, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks = splitter.split_documents(docs)
    return chunks

docs = load_document("./document.pdf")

print(split_document(docs)[0])