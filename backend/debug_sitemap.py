import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.sitemap_parser import sitemap_parser

async def test_sitemap_parsing():
    print("Testing sitemap parsing...")

    sitemap_url = "https://physical-ai-humanoid-robotics-tan-ten.vercel.app/sitemap.xml"
    print(f"Parsing sitemap: {sitemap_url}")

    urls = sitemap_parser.parse_sitemap(sitemap_url)

    print(f"Found {len(urls)} URLs:")
    for i, url in enumerate(urls[:10]):  # Print first 10 URLs
        print(f"  {i+1}. {url}")

    if len(urls) > 10:
        print(f"  ... and {len(urls) - 10} more URLs")

    return urls

if __name__ == "__main__":
    urls = asyncio.run(test_sitemap_parsing())
    print(f"\nTotal URLs found: {len(urls)}")