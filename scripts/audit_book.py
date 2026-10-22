#!/usr/bin/env python3
"""Read-only audit of a Markdown course book; never fetch or execute course code."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

try:
    from markdown_it import MarkdownIt
except ImportError:
    print("Missing markdown-it-py. Install scripts/requirements.txt in the chosen Python environment.", file=sys.stderr)
    raise SystemExit(2)

PARSER = MarkdownIt("commonmark")


def code_digest(text):
    """Fingerprint fence bodies only, allowing language-label/style changes."""
    bodies = [token.content for token in PARSER.parse(text) if token.type == "fence"]
    payload = json.dumps(bodies, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def subsection_ids(tokens):
    found = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and index + 1 < len(tokens):
            content = tokens[index + 1].content
            match = re.match(r"(\d+\.\d+\.\d+(?:\.\d+)*)\b", content)
            if match:
                found.append(match.group(1))
    return found


def audit(root, manifest_path=None):
    errors, warnings, documents = [], [], {}
    languages = Counter()
    local_references, fence_count = 0, 0

    def error(code, path, **extra):
        errors.append({"code": code, "path": str(path), **extra})

    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts) or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            error("unreadable-markdown", relative, message=str(exc))
            continue
        tokens = PARSER.parse(text)
        documents[path.resolve()] = (text, tokens)
        lines = text.splitlines()
        for token in tokens:
            if token.type == "fence":
                fence_count += 1
                language = token.info.split()[0] if token.info.strip() else ""
                languages[language or "(unlabeled)"] += 1
                if not language and token.content.strip():
                    warnings.append({"code": "unlabeled-code", "path": str(relative), "line": token.map[0] + 1})
                # markdown-it accepts EOF as a fence end. Report it so a
                # missing delimiter cannot silently swallow the rest of a book.
                last = lines[token.map[1] - 1] if token.map and token.map[1] else ""
                last = re.sub(r"^\s*(?:>\s*)*", "", last)
                closing = re.fullmatch(re.escape(token.markup[0]) + "{" + str(len(token.markup)) + ",}\\s*", last)
                if not closing:
                    error("unclosed-fence", relative, line=token.map[0] + 1)
            if token.type != "inline":
                continue
            for child in token.children or []:
                attribute = "href" if child.type == "link_open" else "src" if child.type == "image" else None
                if not attribute:
                    continue
                target = child.attrGet(attribute)
                if not target or target.startswith("#"):
                    continue
                try:
                    parsed = urlsplit(target)
                except ValueError:
                    error("invalid-link", relative, target=target)
                    continue
                if parsed.scheme or parsed.netloc:
                    continue
                local_references += 1
                resolved = path.parent / unquote(parsed.path)
                if not resolved.exists():
                    error("missing-local-target", relative, target=target)

    manifest = {}
    if manifest_path:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(manifest, dict):
                raise ValueError("Manifest root must be an object")
        except (OSError, UnicodeError, ValueError) as exc:
            error("invalid-manifest", manifest_path.name, message=str(exc))
            manifest = {}

    items = manifest.get("items", [])
    if not isinstance(items, list):
        error("invalid-items", manifest_path.name, message="items must be an array")
        items = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            error("invalid-item", "manifest", message="item must be an object")
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            error("missing-item-id", "manifest")
        elif identifier in seen:
            error("duplicate-item-id", "manifest", item_id=identifier)
        if isinstance(identifier, str):
            seen.add(identifier)
        availability = item.get("availability")
        if availability not in {"offline", "online", "unavailable"}:
            error("invalid-availability", "manifest", item_id=identifier)
        if availability != "offline":
            continue
        location = item.get("path")
        if not isinstance(location, str) or not location:
            error("missing-offline-path", "manifest", item_id=identifier)
            continue
        target = (root / location).resolve()
        if not target.is_file():
            error("missing-manifest-file", location, item_id=identifier)
            continue
        expected_hash = item.get("sha256")
        if expected_hash and hashlib.sha256(target.read_bytes()).hexdigest() != expected_hash:
            error("file-hash-mismatch", location, item_id=identifier)
        doc = documents.get(target)
        if item.get("code_sha256"):
            if not doc or code_digest(doc[0]) != item["code_sha256"]:
                error("code-body-mismatch", location, item_id=identifier)
        if "subsection_ids" in item:
            if not doc or subsection_ids(doc[1]) != item["subsection_ids"]:
                error("subsection-mismatch", location, item_id=identifier)

    groups = manifest.get("coverage_groups", [])
    if not isinstance(groups, list):
        error("invalid-coverage-groups", "manifest")
        groups = []
    for group in groups:
        if not isinstance(group, dict):
            error("invalid-coverage-group", "manifest")
            continue
        if not isinstance(group.get("languages"), list) or not isinstance(group.get("section_ids"), list):
            error("invalid-coverage-group", "manifest", message="languages and section_ids must be arrays")
            continue
        for language in group.get("languages", []):
            matching = [item.get("section_id") for item in items if isinstance(item, dict)
                        and item.get("kind") == group.get("kind")
                        and item.get("language") == language and item.get("availability") == "offline"]
            actual = Counter(matching)
            for section in group.get("section_ids", []):
                if actual[section] != 1:
                    error("coverage-mismatch", "manifest", kind=group.get("kind"), language=language,
                          section_id=section, actual=actual[section], expected=1)

    return {
        "ok": not errors,
        "stats": {"markdown_files": len(documents), "local_references": local_references,
                  "fenced_blocks": fence_count, "code_languages": dict(sorted(languages.items())),
                  "manifest_items": len(items)},
        "errors": errors,
        "warnings": warnings,
        "limits": ["No network requests or course-code execution.",
                   "Standard Markdown links checked; wikilinks and anchor navigation need separate review.",
                   "Structure and hashes do not prove translation accuracy or visual quality."]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Course book directory")
    parser.add_argument("--manifest", type=Path, help="Optional provenance/coverage manifest")
    parser.add_argument("--report", type=Path, help="Optional JSON report path; default is stdout only")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root must be an existing directory")
    result = audit(args.root.resolve(), args.manifest)
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
