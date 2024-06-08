import os
import grp
import subprocess
import tempfile

# from unittest.mock import patch

from sh_doctest.numbered_line import NumberedLine
from sh_doctest.shell import shell, set_header, set_trailer, process_run_as


def test_shell_runs_script():
    script = "echo 'Hello, World!'"
    result = shell(script)
    assert result.stdout.strip() == "Hello, World!"


def test_shell_runs_script_with_cwd():
    script = "pwd"
    cwd = tempfile.mkdtemp()
    result = shell(script, cwd=cwd)
    assert (
        result.stdout.strip().replace("/private", "") == cwd
    )  # adjust for OS-X /private


def test_shell_runs_script_with_timeout():
    script = "sleep 5"
    try:
        shell(script, timeout=1)
    except subprocess.TimeoutExpired:
        pass
    else:
        assert False, "Should have raised an exception"


def test_shell_runs_script_with_check():
    script = "exit 1"
    try:
        shell(script, check=True)
        assert False, "Should have raised an exception"
    except subprocess.CalledProcessError:
        pass


def test_set_trailer():
    set_header("echo 'Header'")
    set_trailer("echo 'Trailer'")
    script = "echo 'Test'"
    result = shell(script)
    assert result.stdout.strip() == "Header\nTest\nTrailer"


def test_shell_runs_script_with_run_as():
    script = "whoami"
    user = os.getenv("USER")
    gid = os.getgid()
    group = grp.getgrgid(gid).gr_name
    combined = user + ":" + group
    set_header("")
    set_trailer("")
    result = shell(script, run_as=NumberedLine(combined))
    assert result.stdout.strip() == combined.split(":")[0]


def test_process_run_as_with_user_only():
    run_as = NumberedLine("testuser")
    user, group, extra_groups = process_run_as(run_as)
    assert user == "testuser"
    assert group == "testuser"
    assert extra_groups == ["testuser"]


def test_process_run_as_with_user_and_group():
    run_as = NumberedLine("testuser:testgroup")
    user, group, extra_groups = process_run_as(run_as)
    assert user == "testuser"
    assert group == "testgroup"
    assert extra_groups is None


def test_process_run_as_with_user_group_and_extra_groups():
    run_as = NumberedLine("testuser:testgroup:extragroup1,extragroup2")
    user, group, extra_groups = process_run_as(run_as)
    assert user == "testuser"
    assert group == "testgroup"
    assert extra_groups == ["extragroup1", "extragroup2"]


def test_process_run_as_with_user_and_extra_groups():
    run_as = NumberedLine("testuser::extragroup1,extragroup2")
    user, group, extra_groups = process_run_as(run_as)
    assert user == "testuser"
    assert group == "testuser"
    assert extra_groups == ["extragroup1", "extragroup2"]


def test_process_run_as_with_empty_group():
    run_as = NumberedLine("testuser:")
    user, group, extra_groups = process_run_as(run_as)
    assert user == "testuser"
    assert group == "testuser"
    assert extra_groups is None


def test_process_run_as_with_none():
    user, group, extra_groups = process_run_as(None)
    assert user is None
    assert group is None
    assert extra_groups is None
