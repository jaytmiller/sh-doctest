import functools
from typing import Any


@functools.total_ordering
class NumberedLine:
    """A line of text with a line number describing its position in a larger text."""

    def __init__(self, line: Any, lineno: int = -1) -> None:
        if isinstance(line, NumberedLine):
            self.line: str = line.line
            self.lineno: int = line.lineno if lineno == -1 else lineno
        else:
            assert isinstance(line, str)
            assert isinstance(lineno, int)
            self.line = line
            self.lineno = lineno

    def __repr__(self) -> str:
        return f"NumberedLine({str.__repr__(self.line)}, {self.lineno})"

    def __str__(self) -> str:
        return self.line

    def __len__(self) -> int:
        return len(self.line)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.line == other.line
        else:
            return self.line == other

    def __lt__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.line < other.line
        else:
            return self.line < other

    def __getitem__(self, key) -> "NumberedLine":
        return NumberedLine(self.line[key], self.lineno)

    def __bool__(self) -> bool:
        return self.line != ""

    def strip(self, chars: str = " ") -> "NumberedLine":
        return NumberedLine(self.line.strip(chars), self.lineno)

    def split(
        self, chars: str | None = None, max_splits: int = -1
    ) -> list["NumberedLine"]:
        return [NumberedLine(part, self.lineno) for part in self.line.split(chars)]

    def copy(self) -> "NumberedLine":
        return NumberedLine(self.line, self.lineno)

    def to_simpl(self) -> list[int | str] | str:
        return f"{self.lineno}: {self.line}"

    def startswith(self, prefix: str | tuple[str, ...]) -> bool:
        return self.line.startswith(prefix)

    def endswith(self, suffix: str | tuple[str, ...]) -> bool:
        return self.line.endswith(suffix)
