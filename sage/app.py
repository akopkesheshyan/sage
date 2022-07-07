from typing import Optional, Type

from textual.app import App
from textual.driver import Driver
from textual.reactive import Reactive
from textual.widgets import  ScrollView
from .renderables.list import List
from .widgets import Footer, SearchPrompt


class Sage(App):
    """Main application interface"""
    search_prompt = Reactive(False)

    def __init__(
        self,
        screen: bool = True,
        driver_class: Optional[Type[Driver]] = None,
        log_verbosity: int = 1,
        **kwargs
    ) -> None:
        super().__init__(
           screen=screen,
           driver_class=driver_class,
           log_verbosity=log_verbosity,
           **kwargs
        )

        self.topic = []
        for i in range(1000):
           self.topic.append((f"Element {i}","http://google.com", "some short desc comes here"))

        self.footer_widget = Footer()
        self.search_prompt_widget = SearchPrompt()


    async def on_load(self) -> None:
        """Sent before going in to application mode."""
        # setup basic key bindings
        await self.bind("/", "toggle_search_prompt", "Search")
        await self.bind("q", "quit", "Quit")


    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""
        self.search_prompt_widget.visible = False

        # Create our widgets
        # In this a scroll view for the code and a directory tree
        self.body = ScrollView()
        # Dock our widgets
        await self.view.dock(self.search_prompt_widget, edge="bottom")
        await self.view.dock(self.footer_widget, edge="bottom")
        # Note the directory is also in a scroll view
        await self.view.dock(
            ScrollView(List(self.topic, pointer=1)), edge="left",  name="sidebar"
        )
        await self.view.dock(self.body, edge="top")


    async def action_toggle_search_prompt(self) -> None:
        self.search_prompt = not self.search_prompt

    async def watch_search_prompt(self, show: bool) -> None:
        self.search_prompt_widget.visible = show
        await self.search_prompt_widget.focus()
