import httpx
from typing import Optional, Dict, Any
from .config import settings


class ApiClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.backend_url
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def close(self):
        await self.client.aclose()

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        response = await self.client.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        response = await self.client.post(endpoint, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
        response = await self.client.put(endpoint, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None):
        response = await self.client.delete(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()


# Global API client instance
api_client = ApiClient()