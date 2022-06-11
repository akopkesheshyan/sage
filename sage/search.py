from typing import List
import aiohttp
import asyncio
import importlib

from .schemas import SearchResult

class Search():
    def __init__(self) -> None:
        self.providers = [
            "stackoverflow"
        ]

    async def get_providers(self, session) -> List:
        providers = []
        for name in self.providers:
            module = importlib.import_module(f"sage.providers")
            provider = getattr(module, name.capitalize())
            providers.append(provider(session))
        return providers

    async def query(self, message: str) -> List[SearchResult]:
        async with aiohttp.ClientSession() as session:
            results = []
            providers = await self.get_providers(session)
            for provider in providers:
                results.append(provider.query(message))
            data = await asyncio.gather(*results)
            return data
