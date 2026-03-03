from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash")
embeddingModel = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
def email(query):
    query = query
    search_results = QdrantVectorStore.from_existing_collection(
            url=os.getenv("QDRANTDB_URI"),
        collection_name="email_context",
        embedding=embeddingModel,
    ).similarity_search(
        query=query
        )
    contexts = []

    for result in search_results:
        contexts.append(
        f"""
    Page Content:
    {result.page_content}

    Page Number: {result.metadata.get('page_label')}
    Source File: {result.metadata.get('source')}
    """
        )
    context = "\n\n---\n\n".join(contexts)
    SYSTEMPROMPT = f"""
    You are an Email Agent which sends nd drafts email being context aware.

    STRICT RULES:
    - You MUST answer ONLY from the provided context.
    - If the answer is not present, say: "The information is not available in the provided document."
    - Dont mention page numbers in answers
    - Do NOT use external knowledge.
    - Do NOT hallucinate.
    - Your respose will be sent to an email agent so you have to reply in a form of query to an email agent.
    - Give proper structred Response, the best and professionalism should be maintained

    Context:
    {context}

    EXAMPLE:
    user query: send an email to example@example.com offering a list of our products, do you have any requirement?
    Your reply: send an email to example@example.com with Context: {context}, do u have any requiremnt.
    Note that human can ask u to do any of the follwing thing, u have to reply with that thing back only
    1. send email
    2. draft email
    """
    reply = llm.invoke([
        SystemMessage(SYSTEMPROMPT),
        HumanMessage(query)
    ])
    return reply.content

