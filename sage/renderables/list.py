from typing import Generic, List, Optional, TypeVar, Union

from rich.text import Text

T = TypeVar("T")


class List(Generic[T]):
    __pointer: int = -1

    def __init__(
        self,
        wrapped: List[Union[str, tuple]],
        max_len: int = -1,
        pointer: int = -1,
        selected: Optional[Union[str, tuple]] = None,
    ) -> None:
        self.list = wrapped if wrapped else []
        self.max_len = (
            len(self.list) if max_len < 0 or max_len > len(self.list) else max_len
        )
        self.start_rendering = 0
        self.end_rendering = self.max_len
        if 0 <= pointer < len(self.list):
            self.pointer = pointer

        if selected is not None:
            self.selected = selected

    def __rich__(self) -> Text:
        content = Text(overflow="ellipsis", no_wrap=True)
        for index in range(self.start_rendering, self.end_rendering):
            pointer = " "
            color = "bold"
            if self.selected == self.list[index]:
                pointer = ">"
                color += " red"
            item = self.list[index] if isinstance(self.list[index], tuple) else [self.list[index], None, None]
            title, subtitle, body = item
            content.append(pointer, color)
            content.append(" ")
            content.append(title, color)
            content.append("\n")
            if subtitle:
                content.append("  ")
                content.append(subtitle, "green")
                content.append("\n")
            if body:
                content.append("  ")
                content.append(body, "grey70")
                content.append("\n\n")
        return content

    @property
    def selected(self) -> Optional[Union[str, tuple]]:
        if self.pointer < 0 or self.pointer >= len(self.list):
            return None
        return self.list[self.pointer]

    @selected.setter
    def selected(self, selected: Optional[Union[str, tuple]]) -> None:
        if selected is None:
            self.reset()
            return

        if selected in self.list:
            self.pointer = self.list.index(selected)
        else:
            self.reset()

    # def __str__(self) -> str:
    #     return str(self.renderables())
    #
    def renderables(self):
        return self.list[self.start_rendering : self.end_rendering]

    def reset(self) -> None:
        self.__pointer = -1
        self.start_rendering = 0
        self.end_rendering = self.max_len

    @property
    def pointer(self) -> int:
        return self.__pointer

    @pointer.setter
    def pointer(self, pointer: int) -> None:
        if pointer < 0:
            self.__pointer = len(self.list) - 1
            self.end_rendering = len(self.list)
            self.start_rendering = self.end_rendering - self.max_len
        elif pointer >= len(self.list):
            self.__pointer = 0
            self.start_rendering = 0
            self.end_rendering = self.max_len
        elif pointer < self.start_rendering:
            self.__pointer = pointer
            self.start_rendering = pointer
            self.end_rendering = pointer + self.max_len
        elif pointer >= self.end_rendering:
            self.__pointer = pointer
            self.start_rendering = pointer - self.max_len + 1
            self.end_rendering = pointer + 1
        else:
            self.__pointer = pointer

    def previous(self) -> Optional[Union[str, tuple]]:
        self.pointer -= 1
        return self.selected

    def next(self) -> Optional[Union[str, tuple]]:
        self.pointer += 1
        return self.selected

