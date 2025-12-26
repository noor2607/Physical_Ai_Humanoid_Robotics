import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
import logging
from config.settings import settings
import time
import asyncio
from functools import wraps
import hashlib
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExtractedContent:
    """
    Data class to hold extracted content information
    """
    url: str
    title: str
    content: str
    source_hash: str

class ContentExtractor:
    """
    Service for extracting text content from web pages
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Textbook-RAG-Bot/1.0'
        })

    def _rate_limit(func):
        """
        Decorator to implement rate limiting for requests
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Simple rate limiting - wait between requests
            time.sleep(0.1)  # 100ms delay between requests
            return func(self, *args, **kwargs)
        return wrapper

    def _fetch_page_content(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of a web page

        Args:
            url: URL of the page to fetch

        Returns:
            HTML content of the page, or None if failed
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Handle different encodings
            if response.encoding:
                return response.text
            else:
                # If no encoding is specified, try to detect it
                return response.content.decode('utf-8')

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page from {url}: {str(e)}")
            return None
        except UnicodeDecodeError as e:
            logger.error(f"Error decoding content from {url}: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract the title from the HTML soup

        Args:
            soup: BeautifulSoup object of the HTML content

        Returns:
            Title of the page
        """
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()

        # If no title tag, try og:title meta tag
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()

        # If still no title, try h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()

        return "Untitled Page"

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from the HTML soup, filtering out navigation, ads, etc.

        Args:
            soup: BeautifulSoup object of the HTML content

        Returns:
            Main text content of the page
        """
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement', 'ads']):
            tag.decompose()

        # Look for main content containers in order of preference
        content_selectors = [
            'main',
            'article',
            '.content',
            '#content',
            '.post',
            '.article',
            '.main-content',
            '.entry-content',
            '[role="main"]',
            'body'
        ]

        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.find('body')

        if main_content:
            # Extract text and clean it up
            text = main_content.get_text(separator=' ')
            return self._clean_text(text)
        else:
            # If no main content container found, extract all text from body
            body = soup.find('body')
            if body:
                text = body.get_text(separator=' ')
                return self._clean_text(text)
            else:
                # Fallback: get all text from the entire document
                text = soup.get_text(separator=' ')
                return self._clean_text(text)

    def _clean_text(self, text: str) -> str:
        """
        Clean up extracted text by removing extra whitespace and normalizing

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        import re
        # Replace multiple whitespace characters with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove excessive newlines (more than 2)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        return text

    def _generate_source_hash(self, content: str) -> str:
        """
        Generate a hash of the content to detect changes

        Args:
            content: Content to hash

        Returns:
            SHA-256 hash of the content
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _validate_content(self, content: str) -> bool:
        """
        Validate that the extracted content meets quality requirements

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise
        """
        if not content or len(content.strip()) < 50:  # At least 50 characters
            return False

        # Check if content is mostly whitespace or special characters
        clean_content = content.strip()
        if len(clean_content) < 50:
            return False

        return True

    def extract_content(self, url: str) -> Optional[ExtractedContent]:
        """
        Extract content from a web page

        Args:
            url: URL of the page to extract content from

        Returns:
            ExtractedContent object with URL, title, content, and hash, or None if failed
        """
        logger.info(f"Extracting content from: {url}")

        # Fetch the page content
        html_content = self._fetch_page_content(url)
        if not html_content:
            logger.error(f"Failed to fetch content from {url}")
            return None

        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title
            title = self._extract_title(soup)

            # Extract main content
            content = self._extract_main_content(soup)

            # Validate content quality
            if not self._validate_content(content):
                logger.warning(f"Content from {url} does not meet quality requirements")
                return None

            # Generate hash of the content
            source_hash = self._generate_source_hash(content)

            logger.info(f"Successfully extracted content from {url}: {len(content)} characters")

            return ExtractedContent(
                url=url,
                title=title,
                content=content,
                source_hash=source_hash
            )

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None

    def chunk_document(self, content: str, chunk_size: int = None, overlap: int = None) -> List[Dict[str, str]]:
        """
        Split a document into chunks for processing

        Args:
            content: Content to chunk
            chunk_size: Size of each chunk (defaults to settings)
            overlap: Overlap between chunks (defaults to settings)

        Returns:
            List of dictionaries containing chunk information
        """
        if chunk_size is None:
            chunk_size = settings.chunk_size
        if overlap is None:
            overlap = settings.chunk_overlap

        if len(content) <= chunk_size:
            return [{"text": content, "index": 0}]

        chunks = []
        start = 0
        index = 0

        while start < len(content):
            # Determine the end position for this chunk
            end = start + chunk_size

            # If this is not the last chunk, try to end at a sentence boundary
            if end < len(content):
                # Look for a sentence boundary near the end
                snippet = content[start:end]
                last_sentence_pos = snippet.rfind('. ')

                if last_sentence_pos != -1 and last_sentence_pos > len(snippet) // 2:
                    # Found a good sentence boundary
                    end = start + last_sentence_pos + 2
                else:
                    # Look for a paragraph boundary
                    last_para_pos = snippet.rfind('\n\n')
                    if last_para_pos != -1 and last_para_pos > len(snippet) // 2:
                        end = start + last_para_pos + 2
                    else:
                        # Look for a word boundary
                        last_space_pos = snippet.rfind(' ')
                        if last_space_pos != -1 and last_space_pos > len(snippet) // 2:
                            end = start + last_space_pos

            # Extract the chunk
            chunk_text = content[start:end].strip()

            if chunk_text:  # Only add non-empty chunks
                chunks.append({
                    "text": chunk_text,
                    "index": index
                })

            # Move to the next position, accounting for overlap
            start = end - overlap
            index += 1

        logger.info(f"Document chunked into {len(chunks)} pieces")
        return chunks

    async def extract_content_async(self, url: str) -> Optional[ExtractedContent]:
        """
        Async version of extract_content for better performance

        Args:
            url: URL of the page to extract content from

        Returns:
            ExtractedContent object with URL, title, content, and hash, or None if failed
        """
        return self.extract_content(url)

# Global instance of the content extractor
content_extractor = ContentExtractor()