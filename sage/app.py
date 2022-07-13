from textual.app import App
from textual.reactive import Reactive
from textual.widgets import  ScrollView, Footer
from .renderables.list import List
from .widgets import SearchPrompt
from .search import Search


class Sage(App):
    mode: Reactive[str] = Reactive("NORMAL")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.search_prompt_widget = SearchPrompt(placeholder="")
        self.search = Search()

    async def on_load(self) -> None:
        # setup basic key bindings
        await self.bind("/", "search", "Search")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        self.body = ScrollView()
        await self.view.dock(self.search_prompt_widget, edge="bottom")
        await self.view.dock(self.body, edge="top")

    async def action_search(self) -> None:
        self.mode = "SEARCH"

    async def watch_mode(self, mode: str) -> None:
        if mode == "NORMAL":
            await self.body.focus()
        elif mode == "SEARCH":
            await self.search_prompt_widget.focus()
        elif mode == "LOADING":
            await self.do_search(self.search_prompt_widget.placeholder)
            self.mode = "NORMAL"

    async def do_search(self, message: str):
        results = await self.search.query(message)
        result_list = []
        if results:
            for item in results:
                result_list.append((item.title, item.link, item.description))
        await self.body.update(List(result_list))
