import unittest
from unittest.mock import Mock, patch

from sh_doctest.command_result import CommandResult
from sh_doctest.numbered_line import NumberedLine
from sh_doctest.line_block import LineBlock


class TestCommandResult(unittest.TestCase):
    def test_init(self):
        cmd_result = CommandResult()
        self.assertEqual(cmd_result.exit_code, NumberedLine("0"))
        self.assertEqual(cmd_result.stdout, LineBlock())
        self.assertEqual(cmd_result.stderr, LineBlock())

        exit_code = NumberedLine("1")
        stdout = LineBlock.from_text("stdout text")
        stderr = LineBlock.from_text("stderr text")
        cmd_result = CommandResult(exit_code, stdout, stderr)
        self.assertEqual(cmd_result.exit_code, exit_code)
        self.assertEqual(cmd_result.stdout, stdout)
        self.assertEqual(cmd_result.stderr, stderr)

    def test_bool(self):
        cmd_result = CommandResult()
        self.assertFalse(cmd_result)

        cmd_result.exit_code = NumberedLine("1")
        self.assertTrue(cmd_result)

        cmd_result.stdout = LineBlock.from_text("stdout text")
        self.assertTrue(cmd_result)

        cmd_result.stderr = LineBlock.from_text("stderr text")
        self.assertTrue(cmd_result)

    def test_to_simpl(self):
        cmd_result = CommandResult()
        self.assertEqual(cmd_result.to_simpl(), [])

        cmd_result.exit_code = NumberedLine("1")
        cmd_result.stdout = LineBlock.from_text("stdout text")
        cmd_result.stderr = LineBlock.from_text("stderr text")
        expected_simpl = [
            {"exit_code": cmd_result.exit_code.to_simpl()},
            {"stdout": cmd_result.stdout.to_simpl()},
            {"stderr": cmd_result.stderr.to_simpl()},
        ]
        self.assertEqual(cmd_result.to_simpl(), expected_simpl)

    @patch("subprocess.CompletedProcess")
    def test_from_completed_process(self, mock_completed_process):
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "stdout text"
        mock_result.stderr = "stderr text"
        mock_completed_process.return_value = mock_result

        cmd_result = CommandResult.from_completed_process(mock_result)
        self.assertEqual(cmd_result.exit_code, NumberedLine("1"))
        self.assertEqual(cmd_result.stdout, LineBlock.from_text("stdout text"))
        self.assertEqual(cmd_result.stderr, LineBlock.from_text("stderr text"))
