from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from pathlib import Path
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
load_dotenv()
def rag(pdf_path):
    pdf_path = Path(pdf_path)  

    if not pdf_path.exists():
        return f"File not found: {pdf_path}"

    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    chunks = text_splitter.split_documents(documents=docs)

    embeddingModel = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")


    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        url=os.getenv("QDRANTDB_URI"),
        collection_name="backend_test",
        embedding=embeddingModel,
    )
    return "completed"


