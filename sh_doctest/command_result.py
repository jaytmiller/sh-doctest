from typing import Any
import subprocess

from .numbered_line import NumberedLine
from .line_block import LineBlock


class CommandResult:
    """The result of a single command,  including the exit code,  stdout,  and stderr."""

    def __init__(
        self,
        exit_code: NumberedLine | None = None,
        stdout: list[NumberedLine] | list[str] | None = None,
        stderr: list[NumberedLine] | list[str] | None = None,
    ) -> None:
        self.exit_code: NumberedLine = exit_code or NumberedLine("0")
        self.stdout: LineBlock = LineBlock(stdout) or LineBlock()
        self.stderr: LineBlock = LineBlock(stderr) or LineBlock()

    def __bool__(self) -> bool:
        """Return True if this is not a default empty result."""
        return (
            self.exit_code != NumberedLine("0")
            or self.stdout != LineBlock()
            or self.stderr != LineBlock()
        )

    def to_simpl(self) -> list[dict[str, Any]]:
        return (
            [
                {"exit_code": self.exit_code.to_simpl()},
                {"stdout": self.stdout.to_simpl()},
                {"stderr": self.stderr.to_simpl()},
            ]
            if self
            else []
        )

    @classmethod
    def from_completed_process(cls, result: subprocess.CompletedProcess):
        stdout_block = LineBlock.from_text(result.stdout)
        stderr_block = LineBlock.from_text(result.stderr)
        return cls(
            NumberedLine(str(result.returncode)), stdout_block.lines, stderr_block.lines
        )
