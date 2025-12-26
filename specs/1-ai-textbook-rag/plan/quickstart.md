# Quickstart Guide: AI Textbook RAG Chatbot

**Feature**: 1-ai-textbook-rag
**Created**: 2025-12-25
**Status**: Complete

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git
- Docker (for Qdrant vector database)
- Google API key for Gemini embedding model
- OpenAI API key (for agent functionality)

## Environment Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn qdrant-client openai google-generativeai beautifulsoup4 requests python-dotenv pydantic
   ```

4. **Set up environment variables**:
   Create a `.env` file in the backend directory with the following:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   SITEMAP_URL=https://physical-ai-humanoid-robotics-tan-ten.vercel.app/sitemap.xml
   ```

## Starting Services

1. **Start Qdrant vector database** (using Docker):
   ```bash
   docker run -d --name qdrant-container -p 6333:6333 qdrant/qdrant
   ```

2. **Start the backend API**:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Running the Ingestion Pipeline

1. **Trigger initial ingestion**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest \
     -H "Content-Type: application/json" \
     -d '{"sitemap_url": "https://physical-ai-humanoid-robotics-tan-ten.vercel.app/sitemap.xml"}'
   ```

2. **Monitor ingestion status**:
   ```bash
   curl http://localhost:8000/api/v1/status
   ```

## Testing the Query System

1. **Submit a test query**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is ROS 2?", "session_id": "test-session-1"}'
   ```

2. **Expected response format**:
   ```json
   {
     "query_id": "query-123",
     "answer": "ROS 2 is a flexible framework for writing robot applications...",
     "sources": [
       {
         "url": "https://example.com/ros2-intro",
         "title": "Introduction to ROS 2",
         "relevance_score": 0.87
       }
     ],
     "confidence": 0.92
   }
   ```

## Directory Structure

The backend implementation should follow this structure:

```
backend/
├── main.py                 # FastAPI application entry point
├── config/                 # Configuration files
│   ├── __init__.py
│   └── settings.py
├── models/                 # Data models and schemas
│   ├── __init__.py
│   ├── document.py
│   └── query.py
├── services/               # Business logic
│   ├── __init__.py
│   ├── ingestion.py        # Sitemap parsing and content extraction
│   ├── embedding.py        # Embedding generation
│   ├── vector_store.py     # Qdrant integration
│   ├── retrieval.py        # Document retrieval
│   └── agent.py            # OpenAI Agent integration
├── api/                    # API routes
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── ingestion.py
│   │   └── query.py
├── tools/                  # MCP server and tools
│   ├── __init__.py
│   └── rag_tools.py
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── text_processing.py
│   └── validators.py
└── requirements.txt        # Python dependencies
```

## Key Implementation Steps

1. **Implement the ingestion pipeline** (`services/ingestion.py`):
   - Parse sitemap.xml and extract URLs
   - Fetch and extract text content from each page
   - Clean and preprocess the content
   - Generate embeddings using Gemini model
   - Store documents in Qdrant with embeddings

2. **Build the retrieval system** (`services/retrieval.py`):
   - Implement semantic search using Qdrant
   - Create query embedding generation
   - Rank and format results for the agent

3. **Integrate the OpenAI Agent** (`services/agent.py`):
   - Set up the agent with appropriate tools
   - Implement conversation memory
   - Format retrieved context for the agent

4. **Create API endpoints** (`api/v1/`):
   - Ingestion endpoint for triggering document processing
   - Query endpoint for user questions
   - Status endpoint for system health

## Testing Your Implementation

1. **Unit tests**:
   ```bash
   python -m pytest tests/unit/
   ```

2. **Integration tests**:
   ```bash
   python -m pytest tests/integration/
   ```

3. **Manual testing**:
   - Test ingestion with the target sitemap
   - Verify query responses are relevant
   - Check API endpoints return expected formats

## Common Issues and Solutions

- **API rate limits**: Implement caching and request batching
- **Large document processing**: Implement chunking and asynchronous processing
- **Qdrant connection issues**: Verify Docker container is running and accessible
- **Embedding generation failures**: Check API key validity and quota limits

## Next Steps

1. Complete the basic ingestion pipeline
2. Implement the retrieval system
3. Integrate the OpenAI Agent
4. Add MCP server functionality
5. Test with real documentation queries
6. Optimize performance and add monitoring