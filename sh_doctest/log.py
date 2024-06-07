import sys
import traceback


# -----------------------------------------------------------------------------------


class Log:
    level: str
    mode: str

    def __init__(self, level="INFO", mode="w+"):
        self.level = level
        self.mode = mode
        self.handle = sys.stdout

    def set_level(self, level: str) -> None:
        self.level = level

    def debug_mode(self) -> bool:
        return self.level == "DEBUG"

    def log(self, level, *args, **keys) -> None:
        message = " ".join(str(a) for a in args)
        print(level, "-", message, file=self.handle, flush=True, **keys)

    def debug(self, *args, **keys):
        if self.level == "DEBUG":
            self.log("DEBUG", *args, **keys)

    def info(self, *args, **keys):
        self.log("INFO", *args, **keys)

    def warning(self, *args, **keys):
        self.log("WARN", *args, **keys)

    def error(self, *args, **keys):
        self.log("ERROR", *args, **keys)

    def critical(self, *args, **keys):
        self.log("CRITICAL", *args, **keys)

    def exception(self, *args, **keys):
        tb = traceback.format_exc()
        message = " ".join(str(a) for a in args)
        self.log("EXCEPTION", f"{message}\n{tb.rstrip()}", **keys)


log = Log()
