import functools

from .numbered_line import NumberedLine


@functools.total_ordering
class LineBlock:
    """A block of lines,  each with a line number."""

    def __init__(self, lines: list[str] | list[NumberedLine] | None = None) -> None:
        self.lines: list[NumberedLine] = self._to_numbered(
            [] if lines is None else lines
        )

    def _to_numbered(self, lines: list[str] | list[NumberedLine]) -> list[NumberedLine]:
        return [
            NumberedLine(line)
            if isinstance(line, NumberedLine)
            else NumberedLine(line, lineno)
            for lineno, line in enumerate(lines)
        ]

    def __repr__(self) -> str:
        return f"LineBlock({repr(self.lines)})"

    def __str__(self) -> str:
        return "\n".join(str(line) for line in self.lines)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.lines == other.lines
        else:
            return self.lines == other

    def __lt__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.lines < other.lines
        else:
            return self.lines < other

    def to_simpl(self) -> list[list[int | str] | str]:
        return [line.to_simpl() for line in self.lines]

    @classmethod
    def from_text(cls, text: str) -> "LineBlock":
        return cls(
            [
                NumberedLine(line, lineno)
                for lineno, line in enumerate(text.strip().splitlines())
            ]
        )

    def to_text(self) -> str:
        return "\n".join(str(line) for line in self.lines)

    @classmethod
    def from_file(cls, filepath: str) -> "LineBlock":
        with open(filepath, "r", encoding="utf-8") as spec_file:
            spec_text = spec_file.read()
        return cls.from_text(spec_text)

    def __getitem__(self, key):  # -> "NumberedLine" | "LineBlock":
        if isinstance(key, slice):
            return LineBlock(self.lines[key])
        elif isinstance(key, int):
            return self.lines[key]
        else:
            raise KeyError(f"Invalid key {key}.")

    def __len__(self) -> int:
        return len(self.lines)

    def __bool__(self) -> bool:
        return bool(len(self.lines))

    def append(self, line: NumberedLine) -> None:
        self.lines.append(line)

    def pop(self, index: int = -1) -> NumberedLine:
        line = self.lines[index]
        del self.lines[index]
        return line

    def str_list(self) -> list[str]:
        return [str(line) for line in self.lines]
