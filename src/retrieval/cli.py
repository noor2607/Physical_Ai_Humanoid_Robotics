import argparse
import sys
import os
from typing import Dict, Any
from .validator import RetrievalValidator
from ..config.logging_config import setup_logging, get_logger
from ..config.settings import settings


def create_cli() -> argparse.ArgumentParser:
    """
    Create the command-line interface for the Qdrant retrieval validation tool.
    """
    parser = argparse.ArgumentParser(
        description="Qdrant Retrieval Pipeline Validation Tool"
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="The query text to validate retrieval for"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=settings.top_k,
        help=f"Number of top results to retrieve (default: {settings.top_k})"
    )
    parser.add_argument(
        "--filter-field",
        type=str,
        help="Metadata field name for filtering"
    )
    parser.add_argument(
        "--filter-value",
        type=str,
        help="Metadata field value for filtering"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser


def main():
    """
    Main entry point for the CLI interface.
    """
    # Set up logging
    log_level = "DEBUG" if "--verbose" in sys.argv else "INFO"
    setup_logging(log_level)
    logger = get_logger(__name__)

    # Create and parse arguments
    parser = create_cli()
    args = parser.parse_args()

    # Prepare filters if provided
    filters = {}
    if args.filter_field and args.filter_value:
        filters[args.filter_field] = args.filter_value

    try:
        # Initialize the validator
        validator = RetrievalValidator()

        # Validate the query
        logger.info(f"Validating query: '{args.query[:50]}{'...' if len(args.query) > 50 else ''}'")
        result = validator.validate_query(
            query_text=args.query,
            filters=filters if filters else None,
            top_k=args.top_k
        )

        # Print results
        print(f"\nQuery: {args.query}")
        print(f"Retrieved {len(result.retrieved_chunks)} chunks")
        print(f"Relevance Score: {result.relevance_score:.3f}")
        print(f"Ordering Accuracy: {result.ordering_accuracy:.3f}")
        print(f"Metadata Completeness: {result.metadata_completeness:.3f}")
        print(f"Execution Time: {result.execution_time:.3f}s")
        print(f"Confidence Threshold Met: {result.confidence_threshold_met}")

        # Print top 3 chunks as examples
        print(f"\nTop {min(3, len(result.retrieved_chunks))} retrieved chunks:")
        for i, chunk in enumerate(result.retrieved_chunks[:3]):
            print(f"  {i+1}. Score: {chunk.score:.3f}")
            print(f"     Content: {chunk.content[:100]}...")
            print(f"     Metadata: {dict(list(chunk.metadata.items())[:3])}...")
            print()

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()