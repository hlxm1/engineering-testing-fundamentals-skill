"""Copy this self-contained skill to a user-selected root, never overwrite."""
from pathlib import Path
import argparse
import shutil


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", required=True, type=Path,
                        help="Existing or desired agent skill ROOT directory")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / "skills/zeng-engineering-testing"
    parent = args.dest.expanduser().resolve()
    target = parent / source.name
    if not (source / "SKILL.md").is_file():
        parser.error("source skill is missing")
    if target.exists() or target.is_symlink():
        parser.error(f"destination already exists; nothing overwritten: {target}")
    if parent == source or source in parent.parents:
        parser.error("destination must not be inside the source skill")
    parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"Installed {source.name} at {target}")


if __name__ == "__main__":
    main()
