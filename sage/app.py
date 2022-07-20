from typing import List, Optional,  Union
from textual.app import App
from textual.reactive import Reactive
from textual.widgets import  ScrollView, Footer

from .schemas import SearchResult
from .widgets import SearchPrompt, SearchResults, Footer
from .search import Search
from .enums import Mode


class Sage(App):
    mode: Reactive[str] = Reactive(Mode.NORMAL)
    selected: Optional[Union[str, tuple]] = None
    results: List[SearchResult] = []

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.search_prompt_widget = SearchPrompt(placeholder="")
        self.search = Search()

    async def on_load(self) -> None:
        # setup basic key bindings
        await self.bind("/", "search", "Search")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        self.body = SearchResults()
        self.footer = Footer()

        await self.view.dock( self.search_prompt_widget, edge="bottom")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.body, edge="top")
        await self.body.focus()

    async def action_search(self) -> None:
        self.mode = Mode.SEARCH

    async def watch_mode(self, mode: str) -> None:
        if mode == Mode.NORMAL:
            await self.body.focus()
        elif mode == Mode.SEARCH:
            await self.search_prompt_widget.focus()
        elif mode == Mode.LOADING:
            await self.do_search(self.search_prompt_widget.placeholder)
            self.mode = Mode.NORMAL
            await self.body.focus()
        self.footer.refresh(True)

    async def do_search(self, message: str):
        results = await self.search.query(message)
        self.results = []
        if results:
            for item in results:
                self.results.append((item.title, item.link, item.description))
            self.body.refresh(True)
