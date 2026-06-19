"""Pre-commit hook: blocks .env files from being committed.

Usage:
- As standalone hook: copy to .git/hooks/pre-commit
- As pre-commit framework: see .pre-commit-config.yaml
- Manual: python scripts/check_no_env.py
"""
import subprocess
import sys

ALLOWED = {".env.example", ".env.ci"}


def main() -> int:
    try:
        staged = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            stderr=subprocess.DEVNULL,
        ).decode().splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0

    blocked: list[str] = []
    for path in staged:
        if path in ALLOWED:
            continue
        basename = path.rsplit("/", 1)[-1]
        if basename == ".env" or basename.startswith(".env."):
            blocked.append(path)

    if blocked:
        print("=" * 60, file=sys.stderr)
        print("BLOCKED: secret files detected in commit", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        for p in blocked:
            print(f"  {p}", file=sys.stderr)
        print("", file=sys.stderr)
        print("These files contain real credentials. To unblock:", file=sys.stderr)
        print("  git reset HEAD <file>", file=sys.stderr)
        print("  # verify .env is in .gitignore, then re-commit", file=sys.stderr)
        print("", file=sys.stderr)
        print("Allowed exceptions: .env.example (template only)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
