from typing import Optional, Union

from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widget import Widget

from sage.renderables.list import List
from sage.schemas import SearchResult


class SearchResultList(Widget):
    has_focus: Reactive = Reactive(False)
    scrollable_list: Optional[List[SearchResult]] = None

    def max_renderables_len(self) -> int:
        height: int = self.size.height
        return height - 2

    def render(self) -> Panel:
        to_render: Union[Align, List[SearchResult]] = Align.center(
            "We couldn't find anything for your request", vertical="middle"
        )

        if self.app.topics:
            self.scrollable_list = List(
                self.app.topics,
                max_len=self.max_renderables_len(),
                selected=self.scrollable_list.selected
                if self.scrollable_list
                else None,
            )
            to_render = self.scrollable_list

        return Panel(
            to_render,
            # border_style=styles.BORDER_FOCUSED if self.has_focus else styles.BORDER,
            # box=styles.BOX,
            title_align="left",
        )

    def next(self) -> None:
        if self.scrollable_list is None:
            return

        self.scrollable_list.next()
        self.app.topic = self.scrollable_list.selected


    def previous(self) -> None:
        if self.scrollable_list is None:
            return

        self.scrollable_list.previous()
        self.app.topic = self.scrollable_list.selected

        self.app.enable_describer_mode()

    def on_focus(self) -> None:
        self.has_focus = True

    def on_blur(self) -> None:
        self.has_focus = False

    def on_key(self, event: events.Key) -> None:
        if event.key == Keys.Up:
            self.previous()
        elif event.key == Keys.Down:
            self.next()

        self.refresh()

    async def on_mouse_scroll_up(self) -> None:
        await self.app.set_focus(self)
        self.next()
        self.refresh()

    async def on_mouse_scroll_down(self) -> None:
        await self.app.set_focus(self)
        self.previous()
        self.refresh()

    async def on_click(self, event: events.Click) -> None:
        if self.scrollable_list is not None:
            self.scrollable_list.pointer = event.y - 1
            self.app.topic = self.scrollable_list.selected

        self.app.enable_describer_mode()

        self.refresh()
