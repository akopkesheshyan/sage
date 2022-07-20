from typing import Optional, Union

from rich.align import Align
from rich.text import Text
from textual import events
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widget import Widget

from sage.renderables.list import List
from sage.schemas import SearchResult


class SearchResults(Widget):
    has_focus: Reactive = Reactive(False)
    scrollable_list: Optional[List[SearchResult]] = None

    def max_renderables_len(self) -> int:
        height: int = self.size.height
        return height - 2

    def render(self) -> Union[Align, List[SearchResult]]:

        if not self.app.results:
            return Align.center(
                "We couldn't find anything for your request", vertical="middle"
            )
        self.scrollable_list = List(
            self.app.results,
            max_len=self.max_renderables_len(),
            selected=self.app.selected
        )
        return self.scrollable_list

    def next(self) -> None:
        if self.scrollable_list:
            self.app.selected = self.scrollable_list.next()
            self.refresh(True)


    def previous(self) -> None:
        if self.scrollable_list:
            self.app.selected = self.scrollable_list.previous()
            self.refresh(True)


    async def on_focus(self) -> None:
        self.has_focus = True
        self.refresh(True)

    async def on_blur(self) -> None:
        self.has_focus = False

    async def on_key(self, event: events.Key) -> None:
        if event.key == "k":
            self.previous()
        elif event.key == "j":
            self.next()
        elif event.key == Keys.Enter:
            raise Exception(self.app.selected[0])

