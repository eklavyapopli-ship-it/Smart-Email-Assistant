from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
load_dotenv()
pdf_path = "/Users/eklavyapopli/smart email assistant/rag/companyData.pdf"
loader = PyPDFLoader(pdf_path)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=30)

chunks = text_splitter.split_documents(documents=docs)

embeddingModel = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")


vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    url="http://localhost:6333",
    collection_name="email_context",
    embedding=embeddingModel,
)

