import unittest
from unittest.mock import patch, Mock
from sh_doctest.case import Case, CaseParser, CaseRunner, CaseChecker
from sh_doctest.numbered_line import NumberedLine
from sh_doctest.line_block import LineBlock
from sh_doctest.command_result import CommandResult


class TestCase(unittest.TestCase):
    def test_to_simpl(self):
        case = Case()
        case.narrative = LineBlock(["This is a test case."])
        case.name = NumberedLine("Test Case", 1)
        case.run_as = NumberedLine("root", 2)
        case.commands = LineBlock(["echo 'Hello, World!'"])
        case.expected = CommandResult(
            exit_code=NumberedLine("0", 3), stdout=LineBlock(["Hello, World!"])
        )
        case.result = CommandResult(
            exit_code=NumberedLine("0", 3), stdout=LineBlock(["Hello, World!"])
        )
        case.comparison = {
            "stdout": "Passed",
            "stderr": "Passed",
            "exit_code": "Passed",
        }

        expected_simpl = [
            "--------------------------------------------------------------------------------",
            {"narrative": ["0: This is a test case."]},
            {"name": "1: Test Case"},
            {"run_as": "2: root"},
            {"commands": ["0: echo 'Hello, World!'"]},
            {
                "expected": [
                    {"exit_code": "3: 0"},
                    {"stdout": ["0: Hello, World!"]},
                    {"stderr": []},
                ]
            },
            {
                "result": [
                    {"exit_code": "3: 0"},
                    {"stdout": ["0: Hello, World!"]},
                    {"stderr": []},
                ]
            },
            {
                "comparison": {
                    "exit_code": "Passed",
                    "stderr": "Passed",
                    "stdout": "Passed",
                },
            },
        ]

        self.assertEqual(case.to_simpl(), expected_simpl)

    def test_is_interesting(self):
        case = Case()
        case.comparison = {
            "stdout": "Passed",
            "stderr": "Passed",
            "exit_code": "Passed",
        }
        self.assertFalse(case.is_interesting())

        case.comparison = {
            "stdout": "Passed",
            "stderr": "Failed",
            "exit_code": "Passed",
        }
        self.assertTrue(case.is_interesting())


class TestCaseParser(unittest.TestCase):
    def test_parse(self):
        lines = LineBlock.from_text(
            """
This is a test case.

name: Test Case
run_as: root
$ echo 'Hello, World!'
Hello, World!
"""
        )
        parser = CaseParser(lines)
        case = parser.parse()

        self.assertEqual(case.narrative, LineBlock(["This is a test case."]))
        self.assertEqual(case.name, NumberedLine("Test Case", 3))
        self.assertEqual(case.run_as, NumberedLine("root", 4))
        self.assertEqual(case.commands, LineBlock(["echo 'Hello, World!'"]))
        self.assertEqual(case.expected.exit_code, NumberedLine("0", 7))
        self.assertEqual(case.expected.stdout, LineBlock(["Hello, World!"]))
        self.assertEqual(case.expected.stderr, LineBlock())


class TestCaseRunner(unittest.TestCase):
    @patch("sh_doctest.case.shell.shell")
    def test_run(self, mock_shell):
        case = Case()
        case.commands = LineBlock(["echo 'Hello, World!'"])
        case.run_as = NumberedLine("root", 1)

        mock_result = Mock()
        mock_result.stdout = "Hello, World!\n"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_shell.return_value = mock_result

        runner = CaseRunner(case)
        runner.run()

        mock_shell.assert_called_once_with("echo 'Hello, World!'", run_as="root")
        self.assertEqual(case.result.exit_code, NumberedLine("0", -1))
        self.assertEqual(case.result.stdout, LineBlock(["Hello, World!"]))
        self.assertEqual(case.result.stderr, LineBlock())


class TestCaseChecker(unittest.TestCase):
    def test_check_exit_code(self):
        case = Case()
        case.expected.exit_code = NumberedLine("0", 1)
        case.result.exit_code = NumberedLine("0", 1)
        checker = CaseChecker(case)
        self.assertEqual(checker.check_exit_code(), "Passed")

        case.expected.exit_code = NumberedLine("1", 1)
        case.result.exit_code = NumberedLine("0", 1)
        self.assertEqual(checker.check_exit_code(), "Expected exit code 1,  got 0.")

        case.expected.exit_code = NumberedLine("fail", 1)
        case.result.exit_code = NumberedLine("1", 1)
        self.assertEqual(checker.check_exit_code(), "Passed")

    def test_check_pattern(self):
        case = Case()
        case.expected.stdout = LineBlock(["Hello, World!"])
        case.result.stdout = LineBlock(["Hello, World!"])
        checker = CaseChecker(case)
        self.assertEqual(
            checker.check_pattern(
                case.expected.exit_code, case.expected.stdout, case.result.stdout
            ),
            "Passed",
        )

        case.expected.stdout = LineBlock(["Hello, World!"])
        case.result.stdout = LineBlock(["Hello, World!", "Extra line"])
        expected_diff = "\n".join(
            [
                "--- expected",
                "",
                "+++ result",
                "",
                "@@ -1 +1,2 @@",
                "",
                " Hello, World!",
                "+Extra line",
            ]
        )
        self.assertEqual(
            checker.check_pattern(
                case.expected.exit_code, case.expected.stdout, case.result.stdout
            ),
            expected_diff,
        )


if __name__ == "__main__":
    unittest.main()
