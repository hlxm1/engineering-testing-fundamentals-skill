"""Offline structural checks, source navigation, UTF-8, links, and release hygiene."""
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/zeng-engineering-testing"
EXCLUDED = {".git", "__pycache__"}
REQUIRED = ["README.md", "LICENSE", "NOTICE", "VALIDATION.md", "validation-results.json",
            "skills/zeng-engineering-testing/SKILL.md",
            "skills/zeng-engineering-testing/glossary.md",
            "skills/zeng-engineering-testing/patterns.md",
            "skills/zeng-engineering-testing/cheatsheet.md",
            "skills/zeng-engineering-testing/references/formula-audit.md",
            "skills/zeng-engineering-testing/references/quality-report.md",
            "skills/zeng-engineering-testing/references/learning-path.md",
            "skills/zeng-engineering-testing/references/source-index.json",
            "skills/zeng-engineering-testing/references/ocr-metrics.json"]


def public_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*") if p.is_file()
                  and not (EXCLUDED & set(p.relative_to(ROOT).parts)))


def validate() -> dict[str, int]:
    errors = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"required file missing: {rel}")
    files = public_files()
    links = 0
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        if p.is_symlink():
            errors.append(f"symlink not permitted: {rel}")
        if p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".zip", ".onnx", ".epub"}:
            errors.append(f"source/binary asset prohibited: {rel}")
        if "full_text" in p.name or p.name.startswith(".env"):
            errors.append(f"private extraction/config prohibited: {rel}")
        if p.stat().st_size > 1_000_000:
            errors.append(f"unexpected large release file: {rel}")
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"not UTF-8: {rel}")
            continue
        if text.startswith("\ufeff"):
            errors.append(f"unexpected UTF-8 BOM: {rel}")
        if re.search(r"[A-Za-z]:[/\\]Users[/\\]", text):
            errors.append(f"private user path: {rel}")
        if re.search(r"gh[pousr]_[A-Za-z0-9_]{20,}", text):
            errors.append(f"possible GitHub credential: {rel}")
        for char in text:
            c = ord(char)
            if (c < 32 and char not in "\n\r\t") or c in {0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF} or 0x202A <= c <= 0x202E or 0x2066 <= c <= 0x2069:
                errors.append(f"hidden/control code point U+{c:04X}: {rel}")
                break
        if p.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                errors.append(f"invalid JSON: {rel}: {e}")
        if p.suffix == ".py":
            try:
                ast.parse(text, filename=rel)
            except SyntaxError as e:
                errors.append(f"invalid Python: {rel}: {e}")
        if p.suffix == ".md":
            for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#", 1)[0]
                if not target:
                    continue
                links += 1
                resolved = (p.parent / target).resolve()
                if ROOT not in resolved.parents or not resolved.is_file():
                    errors.append(f"broken or external file link: {rel} -> {target}")

    master = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if not re.match(r"\A---\nname: zeng-engineering-testing\ndescription: .+\n---\n", master):
        errors.append("invalid skill frontmatter")
    chapter_files = sorted((SKILL / "chapters").glob("ch*.md"))
    if len(chapter_files) != 9:
        errors.append("expected exactly 9 chapter files")
    for p in chapter_files:
        t = p.read_text(encoding="utf-8")
        if not all(marker in t for marker in ("印刷", "PDF", "自编")):
            errors.append(f"chapter lacks source/example markers: {p.name}")

    index = json.loads((SKILL / "references/source-index.json").read_text(encoding="utf-8"))
    previous_end = 5
    sections = 0
    for expected, ch in enumerate(index["chapters"], start=1):
        lo, hi = ch["print_range"]
        if ch["number"] != expected or lo != previous_end + 1 or lo > hi:
            errors.append("chapter number/range discontinuity")
        if ch["pdf_range"] != [lo + 9, hi + 9]:
            errors.append("chapter PDF mapping invalid")
        if not (SKILL / ch["skill_file"]).is_file():
            errors.append("missing indexed chapter")
        for section in ch["sections"]:
            sections += 1
            if not lo <= section["print_start"] <= hi or section["pdf_start"] != section["print_start"] + 9:
                errors.append(f"section locator invalid: {section['id']}")
        previous_end = hi
    if len(index["chapters"]) != 9 or previous_end != 292 or sections != 46:
        errors.append("book coverage/index count incorrect")
    if not re.fullmatch(r"[0-9a-f]{64}", index["source"]["sha256"]):
        errors.append("source hash missing")
    metrics = json.loads((SKILL / "references/ocr-metrics.json").read_text(encoding="utf-8"))
    if metrics["pdf_pages_processed"] != 308 or [p["pdf_page"] for p in metrics["per_page"]] != list(range(1, 309)):
        errors.append("OCR page coverage incomplete")
    manifest_path = ROOT / "artifact-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        ignored = {"artifact-manifest.json", "VALIDATION.md", "validation-results.json"}
        covered = {p.relative_to(ROOT).as_posix() for p in files
                   if p.relative_to(ROOT).as_posix() not in ignored}
        if covered != set(manifest["files"]):
            errors.append("artifact manifest file set mismatch")
        for rel, record in manifest["files"].items():
            target = (ROOT / rel).resolve()
            if ROOT.resolve() not in target.parents or not target.is_file():
                errors.append(f"invalid manifest target: {rel}")
                continue
            payload = target.read_bytes()
            if hashlib.sha256(payload).hexdigest() != record["sha256"] or len(payload) != record["bytes"]:
                errors.append(f"artifact hash mismatch: {rel}")
    if errors:
        raise SystemExit("Validation failed:\n" + "\n".join("- " + e for e in errors))
    return {"public_text_files": len(files), "markdown_files": sum(p.suffix == ".md" for p in files),
            "checked_relative_links": links, "chapters": 9, "section_locators": sections,
            "ocr_pages": 308}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
    print("Repository validation passed.")
