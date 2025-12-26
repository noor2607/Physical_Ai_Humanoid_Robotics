import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.content_extractor import content_extractor

async def test_content_extraction():
    print("Testing content extraction...")

    # Test with one of the URLs from the sitemap
    url = "https://physical-ai-humanoid-robotics-tan-ten.vercel.app/docs/introduction"
    print(f"Extracting content from: {url}")

    extracted = content_extractor.extract_content(url)

    if extracted:
        print(f"Success! Extracted content:")
        print(f"  URL: {extracted.url}")
        print(f"  Title: {extracted.title}")
        print(f"  Content length: {len(extracted.content)} characters")
        print(f"  Source hash: {extracted.source_hash[:16]}...")

        # Show first 200 characters of content
        print(f"  Content preview: {extracted.content[:200]}...")
    else:
        print("Failed to extract content!")

    return extracted

if __name__ == "__main__":
    extracted = asyncio.run(test_content_extraction())