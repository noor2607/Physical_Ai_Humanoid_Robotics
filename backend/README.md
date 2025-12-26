# AI Textbook RAG Chatbot Backend

This is the backend implementation for the AI Textbook RAG Chatbot. The system ingests documentation from sitemaps, generates embeddings using the Gemini model, stores vectors in Qdrant, and provides a chat interface through OpenAI Agent SDK with MCP server integration.

## Features

- Documentation ingestion from sitemap.xml
- Text extraction and processing
- Embedding generation using Google's Gemini model
- Vector storage in Qdrant
- Semantic search and retrieval
- OpenAI Agent integration
- MCP server integration
- RESTful API endpoints

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Docker (for Qdrant vector database)
- Google API key for Gemini embedding model
- OpenAI API key (for agent functionality)

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

3. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   Copy the `.env` file and update with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Starting Services

1. **Start Qdrant vector database** (using Docker):
   ```bash
   docker run -d --name qdrant-container -p 6333:6333 qdrant/qdrant
   ```

2. **Start the backend API**:
   ```bash
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

## API Endpoints

- `POST /api/v1/ingest` - Trigger documentation ingestion from sitemap
- `POST /api/v1/query` - Submit a query to the RAG system
- `GET /api/v1/status` - Get system status
- `GET /api/v1/sessions/{session_id}` - Get session details
- `GET /health` - Health check endpoint

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config/                 # Configuration files
│   ├── settings.py         # Application settings
├── models/                 # Data models and schemas
├── services/               # Business logic
├── api/                    # API routes
│   └── v1/                 # Version 1 API routes
├── tools/                  # MCP server and tools
├── utils/                  # Utility functions
├── tests/                  # Test files
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## Development

To run tests:
```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run all tests
python -m pytest
```

## License

[License information will be added here]