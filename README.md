# RAG Content Ingestion Pipeline

This project implements a content ingestion pipeline for the Physical AI & Humanoid Robotics Course Book website. It automatically discovers book-related URLs, extracts clean textual content using trafilatura, applies deterministic chunking with overlap, generates embeddings via Cohere API, and persists vectors with rich metadata in Qdrant Cloud.

## Features

- **Automatic URL Discovery**: Parses sitemap to collect all book-related URLs
- **Content Extraction**: Uses trafilatura to extract clean text from web pages
- **Smart Chunking**: Applies deterministic chunking with overlap to preserve context
- **Embedding Generation**: Uses Cohere API to generate high-quality embeddings
- **Vector Storage**: Stores vectors with rich metadata in Qdrant Cloud
- **Duplicate Prevention**: Uses content hashing to prevent duplicate ingestion
- **Comprehensive Logging**: Tracks ingestion success/failure with detailed information
- **Error Handling**: Gracefully handles failures and continues processing
- **Configuration Management**: Securely manages API keys and settings via environment variables

## Prerequisites

- Python 3.11+
- Cohere API key
- Qdrant Cloud account and API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_URL=your_qdrant_cluster_url_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   ```

## Usage

### Basic Ingestion

Run the ingestion pipeline with default settings:

```bash
python -m scripts.embeding.main
```

### Custom Configuration

Run with specific sitemap URL and collection name:

```bash
python -m scripts.embeding.main --sitemap-url "https://yoursite.com/sitemap.xml" --collection-name "my_collection"
```

### Advanced Options

```bash
# Run with custom chunk size and overlap
python -m scripts.embeding.main --chunk-size 1000 --chunk-overlap 200

# Resume from a specific URL if the process was interrupted
python -m scripts.embeding.main --resume-from "https://example.com/page"

# Process only a subset of URLs (for testing)
python -m scripts.embeding.main --max-urls 10
```

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `COHERE_API_KEY` | Cohere API key for embeddings | Required |
| `QDRANT_URL` | Qdrant Cloud cluster URL | Required |
| `QDRANT_API_KEY` | Qdrant API key | Required |
| `SITEMAP_URL` | URL of the sitemap to process | Physical AI course sitemap |
| `QDRANT_COLLECTION_NAME` | Name of the collection in Qdrant | `course_content` |
| `CHUNK_SIZE` | Size of text chunks in characters | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks in characters | 200 |
| `RATE_LIMIT_DELAY` | Delay between requests in seconds | 1.0 |

## Architecture

The system is organized into the following modules:

- `main.py`: Main entry point and pipeline orchestrator
- `config.py`: Configuration loading and validation
- `url_collector.py`: Sitemap parsing and URL collection
- `content_extractor.py`: Content extraction using trafilatura
- `chunker.py`: Text chunking with overlap logic
- `embedder.py`: Cohere API integration for embeddings
- `vector_store.py`: Qdrant Cloud integration
- `logger.py`: Comprehensive logging system
- `utils.py`: Utility functions for hashing, validation, etc.

## Testing

Run the unit tests:

```bash
pytest tests/unit/
```

Run all tests:

```bash
pytest
```

## Project Structure

```
scripts/
└── embeding/
    ├── __init__.py
    ├── main.py              # Main entry point for the ingestion pipeline
    ├── config.py            # Configuration loading and validation
    ├── url_collector.py     # URL discovery and collection from sitemap
    ├── content_extractor.py # Content extraction using trafilatura
    ├── chunker.py           # Text chunking with overlap logic
    ├── embedder.py          # Cohere API integration for embeddings
    ├── vector_store.py      # Qdrant Cloud integration
    ├── logger.py            # Comprehensive logging system
    └── utils.py             # Utility functions for hashing, validation, etc.

tests/
├── unit/
├── integration/
└── contract/

.env.example             # Example environment file
requirements.txt         # Python dependencies
README.md               # Project documentation
```

## Troubleshooting

- **API Rate Limits**: The system includes built-in delays to respect rate limits, but you may need to adjust `RATE_LIMIT_DELAY` if you encounter issues
- **Content Extraction Failures**: Check the logs for specific URLs that failed to extract content
- **Qdrant Connection Issues**: Verify that your Qdrant URL and API key are correct
- **Memory Issues**: For large sites, consider running with `--max-urls` to process in batches

## License

[Add your license information here]