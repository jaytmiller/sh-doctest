from typing import Any
import difflib
import subprocess
import re

import yaml

from .log import log
from .numbered_line import NumberedLine
from .line_block import LineBlock
from .command_result import CommandResult
from . import shell


class Case:
    """A single test case,  consisting of a narrative,  a list of commands,  and the
    expected exit code, standard output, and standard error.
    """

    def __init__(self) -> None:
        self.narrative = LineBlock()
        self.name = NumberedLine("", -1)
        self.run_as = NumberedLine("", -1)
        self.commands = LineBlock()
        self.expected = CommandResult()
        self.result = CommandResult()
        self.comparison: dict[str, str | None] = {}

    def to_simpl(self) -> list[dict[str, Any] | str]:
        """Convert the test case to a YAML string."""
        return [
            "-" * 80,
            dict(narrative=self.narrative.to_simpl()),
            dict(name=self.name.to_simpl()),
            dict(run_as=self.run_as.to_simpl()),
            dict(commands=self.commands.to_simpl()),
            dict(expected=self.expected.to_simpl()),
            dict(result=self.result.to_simpl()),
            dict(comparison=self.comparison),
        ]

    def is_interesting(self) -> bool:
        """Return True if the test case is interesting."""
        return any(value != "Passed" for value in self.comparison.values())

    def to_yaml(self) -> str:
        return yaml.dump(self.to_simpl())

    def run_and_check(self) -> bool:
        runner = CaseRunner(self)
        runner.run()
        checker = CaseChecker(self)
        if failed := checker.check():
            self.report_failure()
        return failed

    def report_failure(self):
        log.error(
            f"FAILED: '{self.name}' at line {self.name.lineno+1} running as {self.run_as}\n",
            "-" * 80,
            "\n",
            self.commands.to_text(),
            "\n",
            "-" * 80,
            sep="",
        )
        for part, value in self.comparison.items():
            if value != "Passed":
                print(part + ":")
                print(value)


class CaseParser:
    previous_name = NumberedLine("", -1)  # persists case-to-case for lightweight cases
    previous_run_as = NumberedLine("", -1)

    def __init__(self, lines: LineBlock) -> None:
        self.lines = lines

    @classmethod
    def from_file(cls, filepath: str) -> "CaseParser":
        with open(filepath, "r", encoding="utf-8") as spec_file:
            spec_text = spec_file.read()
        return cls(LineBlock.from_text(spec_text))

    def skip_empty(self):
        """Remove empty lines from the beginning and end of the list."""
        while self.lines and not self.lines[0].strip():
            self.lines = self.lines[1:]

    def reset_previous(self):
        self.previous_name = NumberedLine("", -1)
        self.previous_run_as = NumberedLine("", -1)

    def parse(self) -> Case:
        log.debug("." * 80)
        log.debug("Parsing case at line", self.lines[0])
        case = Case()
        # self.reset_previous()
        self.parse_narrative(case)
        self.parse_name(case)
        self.parse_run_as(case)
        self.parse_commands(case)
        self.parse_exit_code(case)
        self.parse_expected_stdout(case)
        self.parse_expected_stderr(case)
        return case

    def parse_narrative(self, case: Case):
        """Parse the narrative from the list of lines, adding it to the
        narrative and returning the list of remaining lines.
        """
        self.skip_empty()
        while self.lines and not self.lines[0].strip().startswith(
            ("name:", "run_as:", "$", "exit_code:", "!!")
        ):
            case.narrative.append(self.lines[0])
            log.debug("Narrative added:", case.narrative[-1])
            self.lines = self.lines[1:]
        while case.narrative and case.narrative[-1].strip() == "":
            log.debug("Removing empty line from narrative:", case.narrative[-1].lineno)
            case.narrative = case.narrative[:-1]

    def parse_inheritable(self, case: Case, field_name: str, prefix: str):
        """Parse a field that can be inherited from the previous case."""
        self.skip_empty()
        if self.lines and self.lines[0].startswith(prefix):
            setattr(case, field_name, self.lines[0][len(prefix) :].strip())
            log.debug(f"Setting {field_name}:", getattr(case, field_name))
            self.lines = self.lines[1:]
        elif not getattr(case, field_name):  # Inherit if field is not yet set
            previous_field = getattr(self, f"previous_{field_name}")
            setattr(case, field_name, previous_field.copy())
            getattr(case, field_name).lineno = (
                self.lines[0].lineno if self.lines else -1
            )
            log.debug(f"Inheriting prior {field_name}:", getattr(case, field_name))
        setattr(
            self, f"previous_{field_name}", getattr(case, field_name)
        )  # Update previous field

    def parse_name(self, case: Case):
        """Parse the name of the test case."""
        self.parse_inheritable(case, "name", "name:")

    def parse_run_as(self, case: Case):
        """Parse the run_as field."""
        self.parse_inheritable(case, "run_as", "run_as:")

    def parse_commands(self, case: Case):
        self.skip_empty()
        while self.lines and self.lines[0].startswith("$"):
            case.commands.append(self.lines[0][2:])
            log.debug("Command added:", case.commands[-1])
            self.lines = self.lines[1:]

    def parse_exit_code(self, case: Case):
        if not case.commands:
            return
        if self.lines:
            if self.lines[0].startswith("exit_code:"):
                case.expected.exit_code = self.lines[0][len("exit_code:") :].strip()
                log.debug("Setting exit_code:", case.expected.exit_code)
                self.lines = self.lines[1:]

    def parse_expected_stdout(self, case: Case):
        if not case.commands:  # or case.expected.exit_code.line in ["ignore_stdout"]:
            log.debug("No commands, skipping stdout")
            return
        while (
            self.lines
            and (line := self.lines[0].strip())
            and not line.startswith(("!!", "$ ", "name:", "run_as:", "exit_code:"))
        ):
            if line.startswith(("|", "<BLANKLINE>")):
                line = NumberedLine("", -1)
            case.expected.stdout.append(line)
            log.debug("Stdout added:", case.expected.stdout[-1])
            self.lines = self.lines[1:]

    def parse_expected_stderr(self, case: Case):
        if self.lines and self.lines[0].startswith("!!"):
            # assume exit_code:fail if !! and default ok
            if case.expected.exit_code == NumberedLine("0"):
                log.debug("Assuming exit_code:fail based on stderr !!")
                case.expected.exit_code = NumberedLine("fail", self.lines[0].lineno)
            self.lines = self.lines[1:]  # skip !!
        if not case.commands or case.expected.exit_code.line in ["ignore_stderr"]:
            log.debug("No commands or ignore_stderr, etc, skipping stderr")
            return
        while (
            self.lines
            and (line := self.lines[0].strip())
            and not line.startswith(("$", "name:", "run_as:", "exit_code:"))
        ):
            if line.startswith(("|", "<BLANKLINE>")):
                log.debug("Trimming stderr line:", line)
                line = NumberedLine("", -1)
            case.expected.stderr.append(line)
            log.debug("Stderr added:", case.expected.stderr[-1])
            self.lines = self.lines[1:]


class CaseRunner:
    def __init__(self, case: Case) -> None:
        self.case: Case = case

    def run(self) -> None:
        """Run the test case."""
        command_text = str(self.case.commands)
        if command_text.strip():
            try:
                log.debug("." * 80)
                log.debug(
                    f"Running {self.case.name} as {self.case.run_as}:\n{command_text}\n"
                )
                result = shell.shell(command_text, run_as=self.case.run_as)
                self.case.result = CommandResult.from_completed_process(result)
                log.debug(
                    f"Result:\nExitCode:\n{result.returncode}\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
                )
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout.decode("utf-8") if exc.stdout else ""
                stderr = exc.stderr.decode("utf-8") if exc.stderr else ""
                log.error(
                    f"Timeout: {self.case.name}\n{command_text}\nstdout:\n{stdout}\nstderr:\n{stderr}\n"
                )
                self.case.result = CommandResult(
                    exit_code=NumberedLine("timeout", -1),
                    stdout=[],
                    stderr=[],
                )


class CaseChecker:
    def __init__(self, case: Case):
        self.case = case

    def check(self) -> bool:
        result = self._check()
        if "<invert-check>" in self.case.name:
            return not result
        else:
            return result

    def _check(self) -> bool:
        if not self.case.result:
            return False
        self.case.comparison = dict(
            stdout=self.check_stdout(),
            stderr=self.check_stderr(),
            exit_code=self.check_exit_code(),
        )
        for value in self.case.comparison.values():
            if value != "Passed":
                return True
        return False

    def check_exit_code(self) -> str:
        expected = str(self.case.expected.exit_code)
        result = str(self.case.result.exit_code)
        if expected == result:
            return "Passed"
        elif expected in ["0", "ok", "ignore_stdout"] and result in ["0", "ok"]:
            return "Passed"
        elif ((expected in ["fail", "ignore_stderr"] or
               (re.match(r"\d+", expected) and expected != "0"))
              and result not in ["0", "ok"]):
            return "Passed"
        else:
            return f"Expected exit code {expected},  got {result}."

    def check_stdout(self) -> str:
        return self.check_pattern(
            self.case.expected.exit_code,
            self.case.expected.stdout,
            self.case.result.stdout,
        )

    def check_stderr(self) -> str:
        return self.check_pattern(
            self.case.expected.exit_code,
            self.case.expected.stderr,
            self.case.result.stderr,
        )

    def check_pattern(
        self, exit_code: NumberedLine, expected: LineBlock, result: LineBlock
    ) -> str:
        if exit_code.line in ["ignore_stdout", "ignore_stderr"]:
            return "Passed"
        diffs = difflib.unified_diff(
            expected.str_list(), result.str_list(), fromfile="expected", tofile="result"
        )
        diffs_str = "\n".join(str(d) for d in diffs).strip()
        return diffs_str or "Passed"
