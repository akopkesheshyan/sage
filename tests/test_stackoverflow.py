
import pytest
from sage.search import Search

@pytest.mark.asyncio
async def test_search():
    s = Search()
    result = await s.query("some text")
