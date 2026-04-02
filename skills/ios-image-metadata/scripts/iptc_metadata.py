#!/usr/bin/env python3
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

DEFAULT_GROUP_PREFIXES = [
    "IPTC",
    "XMP-iptcCore",
    "XMP-iptcExt",
    "XMP-plus",
    "XMP-xmpRights",
    "XMP-dc",
    "XMP-photoshop",
]


def _ensure_exiftool(exiftool_path: Optional[str]) -> None:
    if exiftool_path:
        if not os.path.exists(exiftool_path):
            print(f"exiftool not found at: {exiftool_path}", file=sys.stderr)
            sys.exit(1)
        return
    if shutil.which("exiftool") is None:
        print(
            "exiftool not found on PATH. Install exiftool or pass --exiftool PATH.\n"
            "macOS (Homebrew): brew install exiftool\n"
            "Debian/Ubuntu: sudo apt-get update && sudo apt-get install -y libimage-exiftool-perl",
            file=sys.stderr,
        )
        sys.exit(1)


def _split_csv(items: Iterable[str]) -> List[str]:
    out: List[str] = []
    for item in items:
        parts = [p.strip() for p in item.split(",") if p.strip()]
        out.extend(parts)
    return out


def _split_params(items: Iterable[str]) -> List[str]:
    out: List[str] = []
    for item in items:
        parts = [p.strip() for p in item.split(",") if p.strip()]
        for part in parts:
            out.extend(shlex.split(part))
    return out


def _run_exiftool(exiftool_path: Optional[str], args: List[str]) -> str:
    exe = exiftool_path or "exiftool"
    cmd = [exe] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        print(message or "exiftool failed", file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout


def _filter_groups(item: Dict[str, Any], groups: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if "SourceFile" in item:
        out["SourceFile"] = item["SourceFile"]
    for key, value in item.items():
        if key == "SourceFile":
            continue
        if any(key.startswith(f"{prefix}:") for prefix in groups):
            out[key] = value
    return out


def _load_tags_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Tag JSON must be an object of {tag: value}.")
    return data


def _parse_inline_tags(pairs: Iterable[str]) -> Dict[str, Any]:
    tags: Dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid tag assignment: {pair}")
        key, value = pair.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid tag assignment: {pair}")
        existing = tags.get(key)
        if existing is None:
            tags[key] = value
        elif isinstance(existing, list):
            existing.append(value)
        else:
            tags[key] = [existing, value]
    return tags


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return [value]


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _compare_value(
    expected: Any,
    actual: Any,
    contains: bool,
    unordered: bool,
) -> Tuple[bool, Any, Any]:
    if expected is None:
        return (actual is not None, expected, actual)

    expected = _normalize_scalar(expected)
    actual = _normalize_scalar(actual)

    if contains:
        expected_list = [_normalize_scalar(item) for item in _as_list(expected)]
        actual_list = [_normalize_scalar(item) for item in _as_list(actual)]
        ok = all(item in actual_list for item in expected_list)
        return (ok, expected, actual)

    expected_is_list = isinstance(expected, list)
    actual_is_list = isinstance(actual, list)

    if expected_is_list or actual_is_list:
        expected_list = [_normalize_scalar(item) for item in _as_list(expected)]
        actual_list = [_normalize_scalar(item) for item in _as_list(actual)]
        if unordered:
            ok = set(expected_list) == set(actual_list)
            return (ok, expected, actual)
        if len(expected_list) == 1 and len(actual_list) == 1:
            return (expected_list[0] == actual_list[0], expected, actual)
        return (expected_list == actual_list, expected, actual)

    return (expected == actual, expected, actual)


def cmd_read(args: argparse.Namespace) -> None:
    _ensure_exiftool(args.exiftool)
    params = _split_params(args.params or [])
    base_args = ["-j", "-G1", "-a", "-s"]
    tag_args: List[str] = []
    if args.tags:
        tags = _split_csv(args.tags)
        tag_args = [f"-{tag}" for tag in tags]
    output = _run_exiftool(args.exiftool, base_args + params + tag_args + args.files)
    data = json.loads(output)
    if not args.tags:
        groups = _split_csv(args.groups or [])
        if args.iptc:
            groups = DEFAULT_GROUP_PREFIXES + [g for g in groups if g not in DEFAULT_GROUP_PREFIXES]
        if groups:
            data = [_filter_groups(item, groups) for item in data]
    json.dump(data, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")


def cmd_write(args: argparse.Namespace) -> None:
    _ensure_exiftool(args.exiftool)
    tags: Dict[str, Any] = {}
    if args.set:
        tags.update(_load_tags_json(args.set))
    if args.set_inline:
        tags.update(_parse_inline_tags(args.set_inline))
    if not tags:
        print("No tags provided. Use --set JSON or --set-inline key=value.", file=sys.stderr)
        sys.exit(1)
    params = _split_params(args.params or [])
    tag_args: List[str] = []
    for tag, value in tags.items():
        values = value if isinstance(value, list) else [value]
        for entry in values:
            tag_args.append(f"-{tag}={entry}")
    _run_exiftool(args.exiftool, params + tag_args + [args.file])


def cmd_validate(args: argparse.Namespace) -> None:
    _ensure_exiftool(args.exiftool)
    expected: Dict[str, Any] = {}
    if args.expect:
        expected.update(_load_tags_json(args.expect))
    if args.expect_inline:
        expected.update(_parse_inline_tags(args.expect_inline))
    if not expected:
        print("No expected tags provided. Use --expect JSON or --expect-inline key=value.", file=sys.stderr)
        sys.exit(1)

    expected_tags = list(expected.keys())
    params = _split_params(args.params or [])
    tag_args = [f"-{tag}" for tag in expected_tags]
    output = _run_exiftool(args.exiftool, ["-j", "-G1", "-a", "-s"] + params + tag_args + [args.file])
    data = json.loads(output)

    actual_item = data[0] if data else {}
    missing: List[str] = []
    mismatched: Dict[str, Dict[str, Any]] = {}
    for tag, expected_value in expected.items():
        if tag not in actual_item:
            missing.append(tag)
            continue
        ok, exp, act = _compare_value(
            expected_value,
            actual_item.get(tag),
            contains=args.contains,
            unordered=args.unordered,
        )
        if not ok:
            mismatched[tag] = {"expected": exp, "actual": act}

    report = {
        "file": args.file,
        "ok": not missing and not mismatched,
        "missing": missing,
        "mismatched": mismatched,
    }
    json.dump(report, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")
    if missing or mismatched:
        sys.exit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read/write IPTC metadata using the ExifTool CLI."
    )
    parser.add_argument(
        "--exiftool",
        help="Path to the exiftool executable if not on PATH.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    read_parser = subparsers.add_parser("read", help="Read metadata to JSON.")
    read_parser.add_argument("files", nargs="+", help="Image files to read.")
    read_parser.add_argument(
        "--tags",
        action="append",
        help="Tag or comma-separated tag list (e.g., XMP-iptcExt:DigitalSourceType).",
    )
    read_parser.add_argument(
        "--params",
        action="append",
        help="Pass-through exiftool params (repeat or comma-separated).",
    )
    read_parser.add_argument(
        "--groups",
        action="append",
        help="Filter output to group prefixes (repeat or comma-separated).",
    )
    read_parser.add_argument(
        "--iptc",
        action="store_true",
        help="Filter output to common IPTC-related groups.",
    )
    read_parser.set_defaults(func=cmd_read)

    write_parser = subparsers.add_parser("write", help="Write metadata from JSON.")
    write_parser.add_argument("file", help="Image file to update.")
    write_parser.add_argument(
        "--set",
        help="Path to JSON file with {tag: value} mappings.",
    )
    write_parser.add_argument(
        "--set-inline",
        action="append",
        help="Inline tag assignment, repeatable (e.g., XMP-iptcCore:Creator=Jane Doe).",
    )
    write_parser.add_argument(
        "--params",
        action="append",
        help="Pass-through exiftool params (repeat or comma-separated).",
    )
    write_parser.set_defaults(func=cmd_write)

    validate_parser = subparsers.add_parser("validate", help="Validate expected metadata.")
    validate_parser.add_argument("file", help="Image file to validate.")
    validate_parser.add_argument(
        "--expect",
        help="Path to JSON file with {tag: value} expected mappings.",
    )
    validate_parser.add_argument(
        "--expect-inline",
        action="append",
        help="Inline expected tag assignment, repeatable (e.g., XMP-iptcExt:DigitalSourceType=https://...).",
    )
    validate_parser.add_argument(
        "--params",
        action="append",
        help="Pass-through exiftool params (repeat or comma-separated).",
    )
    validate_parser.add_argument(
        "--contains",
        action="store_true",
        help="Check expected values are contained in actual list values.",
    )
    validate_parser.add_argument(
        "--unordered",
        action="store_true",
        help="When both values are lists, compare as sets.",
    )
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
