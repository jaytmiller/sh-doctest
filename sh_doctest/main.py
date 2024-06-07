"""This module defines the top level program and CLI interface for sh_doctest.
"""

import sys
import argparse
from pathlib import Path

from .templates import TemplatedDoc
from .spec import Spec
from .log import log

# -----------------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a set of shell script tests and verify expected results."
    )
    parser.add_argument(
        "test_specs",
        nargs="*",
        help="Filepath to test specification file.  Required.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Just expand and parse.  Do not run the test cases, collect results, or verify vs. expected results.",
    )
    parser.add_argument(
        "--exit-first-failure",
        action="store_true",
        help="Report the first failure and exit vs. running all cases.",
    )
    parser.add_argument(
        "--save-results",
        action="store_true",
        help="Write out the YAML representation of the spec,  with test results and comparisons if not a dry run.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=".",
        help="Output products to this directory.",
    )
    parser.add_argument(
        "--drop-uninteresting",
        action="store_true",
        help="Drop any test cases which succeeded completely or never ran at all.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        "--debug",
        action="store_true",
        help="Enable logging DEBUG messages.",
    )
    return parser.parse_args(argv)


class ShDoctest:
    def __init__(self, argv: list[str]) -> None:
        self.args = parse_args(argv)
        log.set_level("DEBUG" if self.args.verbose else "INFO")

    def main(self) -> int:
        failed = 0
        test_count = spec_count = template_count = expansion_count = 0
        for spec_path in self.args.test_specs:
            spec_count = spec_count + 1
            try:
                doc, expanded = self.expand_templates(spec_path)
            except Exception:
                log.exception("Failed to parse", spec_path)
                failed = 1
            template_count = template_count + len(doc.templates.keys())
            try:
                spec = self.parse_expanded_spec(expanded)
            except Exception:
                log.exception("Failed to parse expansion of", expanded)
                failed = 1
            expansion_count = expansion_count + len(doc.expansions)
            if not self.args.dry_run:
                try:
                    test_count = test_count + len(spec.test_cases)
                    failed |= self.run_and_check(spec)
                except Exception:
                    log.exception("Failed to run and check", expanded)
                    failed = 1
            if self.args.save_results:
                spec.writeto(expanded.replace(".expanded", ".yaml"))
            if failed and self.args.exit_first_failure:
                return 1
        log.info(f"Executed {test_count} tests defined in {spec_count} specs.")
        log.info(
            f"Specs defined {template_count} templates with {expansion_count} template expansions."
        )
        log.info("All tests passed." if not failed else "Some tests failed.")
        return failed

    def expand_templates(self, spec_path: str) -> tuple[TemplatedDoc, str]:
        log.debug("Expanding templates for", spec_path)
        doc = TemplatedDoc.from_file(spec_path)
        doc.parse()
        expanded = str(Path(self.args.output) / (Path(spec_path).name + ".expanded"))
        doc.writeto(expanded)
        return doc, expanded

    def parse_expanded_spec(self, expanded: str) -> Spec:
        log.debug("Parsing expanded spec", expanded)
        spec = Spec(
            expanded, self.args.exit_first_failure, self.args.drop_uninteresting
        )
        spec.parse()
        return spec

    def run_and_check(self, spec: Spec) -> int:
        log.debug("Running and checking", spec)
        return spec.run_and_check()


if __name__ == "__main__":
    sys.exit(ShDoctest(sys.argv[1:]).main())
