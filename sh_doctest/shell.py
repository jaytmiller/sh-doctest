import subprocess
import tempfile
import os

from .log import log

# -----------------------------------------------------------------------------------

HEADER = "#!\bin/bash set -eu -o pipefail\n"
TRAILER = "\nexit 0\n"


def set_header(script: str) -> None:
    global HEADER
    HEADER = script
    log.debug(f"Setting header:\n{'.'*80}\n{script}")


def set_trailer(script: str) -> None:
    global TRAILER
    TRAILER = script
    log.debug(f"Setting trailer:\n{'.'*80}\n{script}")


def shell(
    script: str,
    cwd: str = ".",
    timeout: int = 10,
    check: bool = False,
    interpreter: str = "/bin/bash",
    run_as=None,
) -> subprocess.CompletedProcess:
    """Treat `script` as an inline multi-line bash script and execute it after switching
    to the `cwd` directory.
    """
    # global HEADER, TRAILER
    combined_script = f"""#!{interpreter}

{HEADER}

# ...............................................................................

{script}

# ...............................................................................

{TRAILER}
"""
    user, group, extra_groups = process_run_as(run_as)
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False)
    try:
        tmp.write(combined_script)
        tmp.flush()
        tmp.close()
        os.chmod(tmp.name, 0o755)
        result = subprocess.run(
            (interpreter, tmp.name),
            text=True,
            capture_output=True,
            check=check,
            cwd=cwd,
            timeout=timeout,
            user=user,
            group=group,
            extra_groups=extra_groups,
        )
    finally:
        os.remove(tmp.name)
    return result


def process_run_as(run_as):
    if run_as:
        parts = run_as.line.split(":")
        if len(parts) == 1:
            user = parts[0]
            group = user
            extra_groups = [user]
        else:
            user, group = parts[:2]
            group = group.strip() or user
            extra_groups = parts[2].split(",") if parts[2:] else None
    else:
        user, group, extra_groups = None, None, None
    return user, group, extra_groups
