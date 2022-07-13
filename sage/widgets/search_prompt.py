from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

import rich.box
from rich.align import Align
from rich.padding import Padding
from rich.columns import Columns
from rich.console import Console
from rich.style import Style
from rich.text import Text
from textual import events
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widget import Widget
from textual.layouts.grid import GridLayout

CONSOLE = Console()


def conceal_text(segment: str) -> str:
    """Produce the segment concealed like a password."""
    return "•" * len(segment)

class SearchPrompt(Widget):
    has_focus = False
    value: Reactive[str] = Reactive("")
    cursor: Tuple[str, Style] = (
        "│",
        Style(
            color="white",
            blink=True,
            bold=True,
        ),
    )
    """Character and style of the cursor."""
    _cursor_position: Reactive[int] = Reactive(0)

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        value: str = "",
        placeholder: str = "",
        syntax: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name)
        self.value = value
        """The value of the text field"""
        self.placeholder = placeholder
        """
        Text that appears in the widget when value is "" and the widget
        is not focused.
        """
        """True if the text field masks the input."""
        self.syntax = syntax
        """The name of the language for syntax highlighting."""
        self._cursor_position = len(self.value)
        self._text_offset = 0

    def __rich_repr__(self):
        yield "name", self.name
        value = self.value
        yield "value", value

    def on_mount(self) -> None:
        self.layout_size = 1

    def render(self) -> Columns:
        """
        Produce a Panel object containing placeholder text or value
        and cursor.
        """
        prefix = ""
        if self.has_focus:
            segments = self._render_text_with_cursor()
            prefix = "/"
        else:
            if len(self.value) == 0:
                segments = [self.placeholder]
            else:
                segments = [self.value]

        text = Text.assemble(prefix, *segments)
        mode = Align.left(
            Padding(
                "[bold]{}[/]".format(self.app.mode),
                pad=(0, 1, 0, 1),
                style="black on blue",
                expand=False,
            )
        )

        help = self.make_key_text()
        return Columns([mode, text, help], expand=False)

    @property
    def _visible_width(self):
        """Width in characters of the inside of the input"""
        # remove 2, 1 for each of the border's edges
        # remove 1 more for the cursor
        # remove 2 for the padding either side of the input
        width, _ = self.size
        if self.border:
            width -= 2
        if self.has_focus:
            width -= 1
        width -= 2
        return width

    def _text_offset_window(self):
        """
        Produce the start and end indices of the visible portions of the
        text value.
        """
        return self._text_offset, self._text_offset + self._visible_width

    def _render_text_with_cursor(self) -> List[Union[str, Text, Tuple[str, Style]]]:
        """Produces the renderable Text object combining value and cursor"""
        text = self.value

        # trim the string to fit within the widgets dimensions
        left, right = self._text_offset_window()
        text = text[left:right]

        # convert the cursor to be relative to this view
        cursor_relative_position = self._cursor_position - self._text_offset
        return [
            text[:cursor_relative_position],
            self.cursor,
            text[cursor_relative_position:],
        ]

    async def on_focus(self, event: events.Focus) -> None:
        """Handle Focus events

        Args:
            event (events.Focus): A Textual Focus event
        """
        self.has_focus = True
        self.refresh(True)

    async def on_blur(self, event: events.Blur) -> None:
        """Handle Blur events

        Args:
            event (events.Blur): A Textual Blur event
        """
        self.has_focus = False

    async def on_key(self, event: events.Key) -> None:
        """Handle key events

        Args:
            event (events.Key): A Textual Key event
        """
        if event.key == "left":
            self._cursor_left()
        elif event.key == "right":
            self._cursor_right()
        elif event.key == "home":
            self._cursor_home()
        elif event.key == "end":
            self._cursor_end()
        elif event.key == "ctrl+h":
            self._key_backspace()
            event.stop()
        elif event.key == "delete":
            self._key_delete()
            event.stop()
        elif event.key == "escape":
            self.reset()
        elif event.key == "enter":
            self.search()
            event.stop()
        elif len(event.key) == 1 and event.key.isprintable():
            self._key_printable(event)

    def search(self):
        self.placeholder = self.value
        self.reset()
        self.app.mode = "LOADING"

    def reset(self):
        self.app.mode = "NORMAL"
        self.value = ""
        self.has_focus = False
        self._cursor_position = 0
        self._text_offset = 0
        self.refresh(True)

    def _update_offset_left(self):
        """
        Decrease the text offset if the cursor moves less than 3 characters
        from the left edge. This will shift the text to the right and keep
        the cursor 3 characters from the left edge. If the text offset is 0
        then the cursor may continue to move until it reaches the left edge.
        """
        visibility_left = 3
        if self._cursor_position < self._text_offset + visibility_left:
            self._text_offset = max(0, self._cursor_position - visibility_left)

    def _update_offset_right(self):
        """
        Increase the text offset if the cursor moves beyond the right
        edge of the widget. This will shift the text left and make the
        cursor visible at the right edge of the widget.
        """
        _, right = self._text_offset_window()
        if self._cursor_position > right:
            self._text_offset = self._cursor_position - self._visible_width

    def _cursor_left(self):
        """Handle key press Left"""
        if self._cursor_position > 0:
            self._cursor_position -= 1
            self._update_offset_left()

    def _cursor_right(self):
        """Handle key press Right"""
        if self._cursor_position < len(self.value):
            self._cursor_position = self._cursor_position + 1
            self._update_offset_right()

    def _cursor_home(self):
        """Handle key press Home"""
        self._cursor_position = 0
        self._update_offset_left()

    def _cursor_end(self):
        """Handle key press End"""
        self._cursor_position = len(self.value)
        self._update_offset_right()

    def _key_backspace(self):
        """Handle key press Backspace"""
        if self._cursor_position > 0:
            self.value = (
                self.value[: self._cursor_position - 1]
                + self.value[self._cursor_position :]
            )
            self._cursor_position -= 1
            self._update_offset_left()

    def _key_delete(self):
        """Handle key press Delete"""
        if self._cursor_position < len(self.value):
            self.value = (
                self.value[: self._cursor_position]
                + self.value[self._cursor_position + 1 :]
            )

    def _key_printable(self, event: events.Key):
        """Handle all printable keys"""
        self.value = (
            self.value[: self._cursor_position]
            + event.key
            + self.value[self._cursor_position :]
        )

        if not self._cursor_position > len(self.value):
            self._cursor_position += 1
            self._update_offset_right()



    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        text = Text(
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
            text.append_text(key_text)
        return text
