from dataclasses import dataclass
from datetime import datetime

@dataclass
class SearchResult(object):
    title: str
    link: str
    description: str = ""
    date: datetime = datetime.now()
