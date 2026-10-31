"""Keep the child's exit code and all test output; no shell pipeline."""
from pathlib import Path
import subprocess
import sys


def main():
    folder = Path(__file__).resolve().parent
    if sys.argv[1:] == ["--demo-failure"]:
        result = subprocess.run([sys.executable, "-c", "print('Intentional failure fixture'); raise SystemExit(1)"],
                                cwd=folder, check=False)
    elif sys.argv[1:]:
        print("Usage: python run_checks.py [--demo-failure]", file=sys.stderr)
        return 2
    else:
        result = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_reader_lab.py"],
                                cwd=folder, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
