# Quickstart Guide: RAG Content Ingestion

## Overview

This guide provides a step-by-step process to set up and run the RAG content ingestion pipeline for the Physical AI & Humanoid Robotics Course Book website.

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for cloning the repository)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file by copying the example:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required: Cohere API key for generating embeddings
COHERE_API_KEY=your_cohere_api_key_here

# Required: Qdrant Cloud cluster URL
QDRANT_URL=your_qdrant_cluster_url_here

# Required: Qdrant API key
QDRANT_API_KEY=your_qdrant_api_key_here
```

## Basic Usage

### Run with Default Settings

The pipeline will process the default sitemap for the Physical AI course:

```bash
python -m backend.main
```

### Custom Sitemap URL

To process a different website:

```bash
python -m backend.main --sitemap-url "https://yoursite.com/sitemap.xml"
```

### Custom Collection Name

To use a specific Qdrant collection:

```bash
python -m backend.main --collection-name "my_custom_collection"
```

### Process Subset of URLs (for Testing)

To process only the first 10 URLs:

```bash
python -m backend.main --max-urls 10
```

## Advanced Options

### Custom Chunking Parameters

Adjust chunk size and overlap:

```bash
python -m backend.main --chunk-size 1500 --chunk-overlap 300
```

### Retry Configuration

Set maximum retry attempts for failed URLs:

```bash
python -m backend.main --max-retries 5
```

### Resumable Processing

Resume from where you left off (the system automatically tracks progress):

```bash
python -m backend.main --state-file "my_session.json"
```

To reset the processing state and start over:

```bash
python -m backend.main --reset-state
```

### Resume from Specific URL

Start processing from a specific URL:

```bash
python -m backend.main --resume-from "https://example.com/specific-page"
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--sitemap-url` | Physical AI course sitemap | URL of the sitemap to process |
| `--collection-name` | `course_content` | Name of the Qdrant collection |
| `--chunk-size` | 1000 | Size of text chunks in characters |
| `--chunk-overlap` | 200 | Overlap between chunks in characters |
| `--max-urls` | All URLs | Maximum number of URLs to process |
| `--max-retries` | 3 | Maximum retry attempts for failed URLs |
| `--state-file` | `processing_state.json` | File to store processing state |
| `--reset-state` | N/A | Reset processing state before starting |

## Expected Output

When running the pipeline, you'll see:

1. **Progress indicators** showing URL processing progress
2. **Success/Failure logs** for each URL processed
3. **Performance metrics** including processing times
4. **Final summary** with total processed/failed counts

## Troubleshooting

### Common Issues

1. **API Rate Limits**: The system includes built-in delays. If you still encounter rate limits, increase the `RATE_LIMIT_DELAY` in your `.env` file.

2. **Memory Issues**: For large sites, use `--max-urls` to process in batches.

3. **Processing State**: If the process is interrupted, simply run the command again to resume from where it left off.

### Logging

- All logs are written to console and to timestamped log files
- Check log files in the format `ingestion_YYYYMMDD_HHMMSS.log`
- Failed URLs are tracked in the processing state file

## Next Steps

After successful ingestion:

1. **Verify data** in your Qdrant collection
2. **Test retrieval** using the Qdrant search functionality
3. **Integrate** with your RAG application
4. **Monitor** the ingestion logs for any issues

## Support

For questions or issues, refer to the main README.md or contact the development team.