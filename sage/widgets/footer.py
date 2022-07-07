from rich.align import Align
from rich.columns import Columns
from rich.padding import Padding
from textual.reactive import Reactive
from textual.widget import Widget


class Footer(Widget):
    mode = Reactive("NORMAL")

    def on_mount(self) -> None:
        self.layout_size = 1

    def render(self) -> Columns:
        mode_text = Align.left(
            Padding(
                "[bold]{}[/]".format(self.mode),
                pad=(0, 1, 0, 1),
                style="black on yellow",
                expand=False,
            )
        )
        return Columns([mode_text, "my search request"], expand=True)
