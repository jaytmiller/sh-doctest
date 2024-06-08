import yaml

from .case import Case, CaseParser
from .log import log
from . import shell


class Spec:
    """A test specification is a list of test cases."""

    def __init__(
        self,
        spec_path: str,
        exit_first_failure: bool = False,
        drop_uninteresting: bool = False,
    ) -> None:
        self.spec_path: str = spec_path
        self.test_cases: list[Case] = []
        self.exit_first_failure: bool = exit_first_failure
        self.drop_uninteresting: bool = drop_uninteresting

    def __repr__(self) -> str:
        return f"Spec {self.spec_path} with {len(self.test_cases)} test cases."

    def __str__(self) -> str:
        return self.to_yaml()

    def to_yaml(self) -> str:
        return yaml.dump(self.to_simpl())

    def to_simpl(self) -> dict:
        return {
            "spec_path": self.spec_path,
            "test_cases": [
                case.to_simpl()
                for case in self.test_cases
                if not self.drop_uninteresting or case.is_interesting()
            ],
        }

    def writeto(self, path: str) -> None:
        """Write the test specification to a file."""
        if path == "-":
            print(self.to_yaml())
        else:
            log.debug("Writing spec to " + path)
            with open(path, "w+", encoding="utf-8") as spec_file:
                spec_file.write(self.to_yaml())

    def parse(self) -> None:
        """Parse a test specification into a list of Case objects."""
        self.test_cases = []
        parser = CaseParser.from_file(self.spec_path)
        while parser.lines:
            case = parser.parse()
            # Conveniently,  the shell persistence of header and trailer lines
            # is global,  so header and trailer persist between specs.
            if case.name == "header":
                shell.set_header(str(case.commands))
            elif case.name == "trailer":
                shell.set_trailer(str(case.commands))
            else:
                self.test_cases.append(case)

    def run_and_check(self) -> bool:
        """Run and check all the test cases."""
        failed = False
        failures = 0
        for test_case in self.test_cases:
            try:
                failed = test_case.run_and_check()
            except Exception:
                log.exception(f"On: {test_case.name} ::\n{test_case.commands}\n")
                failed = True
            if failed:
                failures += 1
                if self.exit_first_failure:
                    return 1
        return failures
