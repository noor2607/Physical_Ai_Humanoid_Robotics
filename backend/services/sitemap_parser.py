import requests
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
import logging
from config.settings import settings
import time
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class SitemapParser:
    """
    Service for parsing sitemap.xml files and extracting URLs
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

    def _fetch_sitemap(self, sitemap_url: str) -> Optional[str]:
        """
        Fetch the sitemap content from the given URL

        Args:
            sitemap_url: URL of the sitemap.xml file

        Returns:
            Content of the sitemap as a string, or None if failed
        """
        try:
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching sitemap from {sitemap_url}: {str(e)}")
            return None

    def _parse_sitemap_xml(self, sitemap_content: str) -> List[str]:
        """
        Parse the sitemap XML content and extract URLs

        Args:
            sitemap_content: XML content of the sitemap

        Returns:
            List of URLs extracted from the sitemap
        """
        urls = []
        try:
            root = ET.fromstring(sitemap_content)

            # Handle different sitemap formats
            # Regular sitemap
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    urls.append(loc_elem.text.strip())

            # Handle sitemap index files (sitemaps that contain other sitemaps)
            for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc_elem = sitemap_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    # For now, we'll just log that we found a sitemap reference
                    # In a complete implementation, we would recursively parse these
                    logger.info(f"Found nested sitemap reference: {loc_elem.text}")

            # Handle sitemap without namespace (common in some implementations)
            if not urls:
                for url_elem in root.findall('.//url'):
                    loc_elem = url_elem.find('loc')
                    if loc_elem is not None and loc_elem.text:
                        urls.append(loc_elem.text.strip())

        except ET.ParseError as e:
            logger.error(f"Error parsing sitemap XML: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing sitemap: {str(e)}")

        return urls

    def _validate_url(self, url: str, base_url: str) -> Optional[str]:
        """
        Validate and normalize a URL

        Args:
            url: URL to validate
            base_url: Base URL for resolving relative URLs

        Returns:
            Validated and normalized URL, or None if invalid
        """
        try:
            # Handle relative URLs
            if not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)

            # Parse the base URL to get the actual domain
            base_parsed = urlparse(base_url)
            original_domain = base_parsed.netloc

            # If the URL has a different domain than the base URL, replace it with the base domain
            # This handles cases where sitemaps have canonical URLs but we need to access via a different domain
            url_parsed = urlparse(url)
            if url_parsed.netloc != original_domain and original_domain:
                # Replace the domain in the URL with the base domain
                url = url.replace(url_parsed.netloc, original_domain, 1)
                logger.debug(f"Replaced domain in URL: {url}")

            # Parse the URL to validate it
            parsed = urlparse(url)

            # Check if it's a valid HTTP/HTTPS URL
            if parsed.scheme not in ['http', 'https']:
                logger.debug(f"Skipping non-HTTP/HTTPS URL: {url}")
                return None

            # Basic validation - check if it has a domain
            if not parsed.netloc:
                logger.debug(f"Skipping invalid URL (no domain): {url}")
                return None

            # Filter out non-HTML content (basic check)
            if any(ext in url.lower() for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.dmg']):
                logger.debug(f"Skipping non-HTML content: {url}")
                return None

            return url

        except Exception as e:
            logger.error(f"Error validating URL {url}: {str(e)}")
            return None

    def parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Parse a sitemap and return a list of valid URLs

        Args:
            sitemap_url: URL of the sitemap.xml file

        Returns:
            List of valid URLs extracted from the sitemap
        """
        logger.info(f"Starting sitemap parsing for: {sitemap_url}")

        # Fetch the sitemap content
        sitemap_content = self._fetch_sitemap(sitemap_url)
        if not sitemap_content:
            logger.error(f"Failed to fetch sitemap from {sitemap_url}")
            return []

        # Parse the XML content to extract URLs
        raw_urls = self._parse_sitemap_xml(sitemap_content)
        logger.info(f"Extracted {len(raw_urls)} URLs from sitemap")

        # Validate and normalize the URLs
        valid_urls = []
        for url in raw_urls:
            validated_url = self._validate_url(url, sitemap_url)
            if validated_url:
                # Avoid duplicates
                if validated_url not in valid_urls:
                    valid_urls.append(validated_url)

        logger.info(f"Validated {len(valid_urls)} valid URLs")
        return valid_urls

    async def parse_sitemap_async(self, sitemap_url: str) -> List[str]:
        """
        Async version of parse_sitemap for better performance

        Args:
            sitemap_url: URL of the sitemap.xml file

        Returns:
            List of valid URLs extracted from the sitemap
        """
        return self.parse_sitemap(sitemap_url)

# Global instance of the sitemap parser
sitemap_parser = SitemapParser()