"""
Phoenix — entry point
Test case: healthcare data sharing between hospitals with GDPR compliance
"""

import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


class TeeWriter:
    """Writes to both console and file simultaneously."""
    def __init__(self, console, file):
        self.console = console
        self.file = file

    def write(self, data):
        self.console.write(data)
        self.file.write(data)

    def flush(self):
        self.console.flush()
        self.file.flush()

    def isatty(self):
        return False


# ── Select active problem ──────────────────────────────────────────────────────
ACTIVE = "role"  
# Options: "healthcare", "antibiotic", "scarring", "quantum", "facts", "render", "wall", "role"
# ──────────────────────────────────────────────────────────────────────────────

from phoenix import Phoenix
from problems import PROBLEMS

_log_file = open(f"output_{ACTIVE}.txt", "w", encoding="utf-8")
sys.stdout = TeeWriter(sys.stdout, _log_file)
sys.stderr = TeeWriter(sys.stderr, _log_file)

if __name__ == "__main__":
    phoenix = Phoenix(config=PROBLEMS[ACTIVE])
    result = phoenix.run()