# Context-Aware Email Agent

A scalable, context-aware email assistant built using LangChain,
Streamlit, Gmail API, Gemini API, RQ workers, Valkey, Qdrant, and Docker
Compose.

This system processes emails, retrieves contextual knowledge using
vector search (RAG), and generates intelligent responses asynchronously
using background workers.

------------------------------------------------------------------------

## Features
-   Context-aware email reply generation
-   Retrieval-Augmented Generation (RAG)
-   Gmail API integration for reading and sending emails
-   Gemini LLM integration for response generation
-   Background task processing using RQ workers
-   Valkey-based distributed queue system
-   Qdrant vector database for semantic search
-   Dockerized and horizontally scalable architecture
-   Streamlit dashboard for interaction and monitoring

------------------------------------------------------------------------

## System Architecture

User → Streamlit UI\
↓\
FastAPI Backend\
↓\
RQ Queue (Valkey)\
↓\
Worker Process\
↓\
LangChain Pipeline\
↓\
Qdrant Vector Search\
↓\
Gemini LLM\
↓\
Generated Response → Gmail API

------------------------------------------------------------------------

## Tech Stack

Frontend: Streamlit\
Backend: FastAPI\
LLM Framework: LangChain\
LLM Provider: Gemini API\
Email Integration: Gmail API\
Vector Database: Qdrant\
Embeddings: Gemini Embeddings\
Queue System: RQ\
Queue Storage: Valkey\
Containerization: Docker Compose

------------------------------------------------------------------------

## Project Structure

email-agent/

├── app.py \# Streamlit frontend\
├── main.py \# FastAPI backend\
├── email_agent.py \# LangChain email logic\
├── rag_pipeline.py \# RAG implementation\
├── rq_client.py \# Queue configuration\
├── worker.py \# Background worker\
├── docker-compose.yml \# Qdrant & Valkey setup\
├── requirements.txt\
└── .env

------------------------------------------------------------------------

## Installation

### 1. Clone Repository

git clone https://github.com/eklavyapopli-ship-it/Smart-Email-Assistant
cd context-aware-email-agent

### 2. Setup Environment Variables

Create a `.env` file:

GEMINI_API_KEY=your_gemini_api_key\
GMAIL_CLIENT_ID=your_client_id\
GMAIL_CLIENT_SECRET=your_client_secret\
GMAIL_REFRESH_TOKEN=your_refresh_token\
VALKEY_HOST=localhost\
VALKEY_PORT=6379\
QDRANT_HOST=localhost\
QDRANT_PORT=6333

### 3. Start Vector DB and Queue Services

docker-compose up -d

This starts: - Qdrant - Valkey

### 4. Run RQ Worker

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES 
python3 -m rq.cli worker

### 5. Start Backend

uvicorn main:app --reload

### 6. Start Frontend

streamlit run app.py

------------------------------------------------------------------------

## How It Works

1.  Email Processing\
    Unread emails are fetched using Gmail API. Subject, body, and
    metadata are extracted.

2.  Context Retrieval (RAG)\
    Email content is embedded and stored. Qdrant performs vector
    similarity search to retrieve relevant context.

3.  Response Generation\
    Retrieved context and email content are passed to Gemini for
    intelligent reply generation.

4.  Asynchronous Execution\
    Tasks are pushed to the Valkey queue and processed by RQ workers in
    the background to ensure scalability and non-blocking UI.

------------------------------------------------------------------------

## Scalability Design

-   Horizontal scaling via multiple RQ workers
-   Stateless FastAPI backend
-   Containerized vector and queue services
-   Independent compute layers (Web, Worker, LLM, Database)
-   Ready for deployment on AWS ECS, GCP Cloud Run, Kubernetes, Render,
    or Railway

------------------------------------------------------------------------

## Security Considerations

-   OAuth2-based Gmail authentication
-   Environment-based secret management
-   Queue isolation
-   Docker network isolation
-   Optional API rate limiting

------------------------------------------------------------------------

## Future Improvements

-   Multi-account email support
-   Automatic priority classification
-   Smart follow-up scheduling
-   Thread-level memory persistence
-   Admin analytics dashboard
-   Slack and WhatsApp integrations

------------------------------------------------------------------------

## License

MIT License
