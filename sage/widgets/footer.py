from __future__ import annotations

from rich.columns import Columns
from rich.padding import Padding
from rich.text import Text
from textual.widget import Widget
from sage.enums import Mode

class Footer(Widget):
    def on_mount(self) -> None:
        self.layout_size = 1

    def get_status(self) -> Padding:
        statuses = {
            Mode.NORMAL: ("Normal", "blue",),
            Mode.SEARCH: ("Search", "red",),
            Mode.LOADING: ("Loading", "green",)
        }

        return Padding(
                "[bold]{}[/]".format(statuses[self.app.mode][0].upper()),
                pad=(0, 1, 0, 1),
                style=f"black on {statuses[self.app.mode][1]}",
                expand=False,
            )


    def get_help(self) -> Text:
        help = Text(
            style="grey50 on default",
            no_wrap=True,
            overflow="ellipsis",
            justify="right",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            key_text = Text.assemble(
                (f" {key_display} ", "grey50 on default"),
                f" {binding.description} ",
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            help.append_text(key_text)
        return help


    def render(self) -> Columns:
        return Columns([
            self.get_status(),
            self.get_help()
        ], expand=True)
