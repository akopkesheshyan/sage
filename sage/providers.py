import aiohttp
from typing import List

from .schemas import SearchResult

class Stackoverflow():
    domain = "https://api.stackexchange.com/2.3"
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.client = session

    async def query(self, message: str) -> List[SearchResult]:
        async with self.client.get(f"{self.domain}/search/advanced?q={message}&site=stackoverflow") as response:
            data = await response.json()
            return [SearchResult(title=r["title"], link=r["link"]) for r in data['items']]
