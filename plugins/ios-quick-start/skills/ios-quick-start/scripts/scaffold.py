#!/usr/bin/env python3
"""
ios-quick-start scaffold script.

Reads the template/ directory, substitutes two tokens (PascalCase and lowercase
project name) in both file contents and file/folder names, writes the result to
{dest}/{ProjectName}/, and initialises a git repo with a first commit.

Usage:
    python3 scaffold.py "<project name>" [--dest <path>]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

TOKEN_PASCAL = "__PROJECT_NAME__"
TOKEN_LOWER = "__PROJECT_NAME_LOWER__"

# File suffixes we consider text and therefore apply token substitution to.
# Binary files (e.g. .png, .xcassets image contents) are copied byte-for-byte.
TEXT_SUFFIXES = {
    ".swift", ".md", ".plist", ".json", ".yml", ".yaml",
    ".xcworkspacedata", ".xcscheme", ".xcstrings",
    ".pbxproj", ".gitignore", ".gitkeep", ".txt",
    "",  # extensionless files like .gitignore show up with suffix "" when only dotfile — handled below too
}


def normalise_name(raw: str) -> tuple[str, str]:
    """Convert "project abc" → ("ProjectAbc", "projectabc")."""
    cleaned = re.sub(r"[^A-Za-z0-9\s_-]", " ", raw)
    words = re.split(r"[\s_\-]+", cleaned.strip())
    words = [w for w in words if w]
    if not words:
        raise ValueError(
            f"Project name {raw!r} does not contain any letters or digits."
        )
    parts = []
    for word in words:
        if word.isupper() and len(word) > 1:
            # Preserve acronyms like "IPTC" → "IPTC" (not "Iptc").
            parts.append(word)
        else:
            parts.append(word[0].upper() + word[1:])
    pascal = "".join(parts)
    if not pascal[0].isalpha():
        raise ValueError(
            f"Project name must start with a letter, got {pascal!r}."
        )
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", pascal):
        raise ValueError(
            f"Normalised project name {pascal!r} is not a valid Swift identifier."
        )
    lower = pascal.lower()
    return pascal, lower


def rename_path_segment(segment: str, pascal: str, lower: str) -> str:
    return segment.replace(TOKEN_PASCAL, pascal).replace(TOKEN_LOWER, lower)


def is_text_file(path: Path) -> bool:
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        return True
    # .gitignore, .gitkeep, .swiftlint.yml etc. are caught above, but handle
    # extensionless dotfiles that weren't listed.
    if suffix == "" and path.name.startswith("."):
        return True
    return False


# Directory names we refuse to copy out of the template. These should never exist
# inside a shipped template, but the IDE and SwiftPM occasionally leave them
# behind if someone opens a Package.swift in place.
SKIP_DIRS = {".build", ".swiftpm", "xcuserdata", "DerivedData"}
SKIP_FILES = {".DS_Store", "Package.resolved"}


def copy_tree(src: Path, dst: Path, pascal: str, lower: str) -> None:
    if dst.exists():
        raise FileExistsError(
            f"Destination {dst} already exists. Remove it or choose a different name."
        )
    for source_path in src.rglob("*"):
        relative = source_path.relative_to(src)
        # Skip anything that falls under a blocklisted directory or file name.
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if source_path.name in SKIP_FILES:
            continue

        renamed_parts = [
            rename_path_segment(part, pascal, lower) for part in relative.parts
        ]
        target_path = dst.joinpath(*renamed_parts)

        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        if is_text_file(source_path):
            try:
                contents = source_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # If the file has a known text suffix but contains non-UTF-8
                # bytes, we copy it byte-for-byte rather than crash. Substitution
                # would not be safe on such a file anyway.
                shutil.copy2(source_path, target_path)
                continue
            substituted = contents.replace(TOKEN_PASCAL, pascal).replace(
                TOKEN_LOWER, lower
            )
            target_path.write_text(substituted, encoding="utf-8")
        else:
            shutil.copy2(source_path, target_path)


def git_init_and_commit(project_dir: Path) -> None:
    try:
        subprocess.run(
            ["git", "init", "--quiet", "--initial-branch=main"],
            cwd=project_dir,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Older git does not support --initial-branch; fall back and rename.
        subprocess.run(["git", "init", "--quiet"], cwd=project_dir, check=True)
        subprocess.run(
            ["git", "symbolic-ref", "HEAD", "refs/heads/main"],
            cwd=project_dir,
            check=False,
        )
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "--quiet",
            "-m",
            "Initial commit from ios-quick-start",
        ],
        cwd=project_dir,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Raw project name (e.g. 'my cool app').")
    parser.add_argument(
        "--dest",
        default=None,
        help="Destination directory. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip `git init` and the initial commit.",
    )
    args = parser.parse_args()

    try:
        pascal, lower = normalise_name(args.name)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    script_dir = Path(__file__).resolve().parent
    template_dir = script_dir.parent / "template"
    if not template_dir.is_dir():
        print(
            f"error: template directory not found at {template_dir}",
            file=sys.stderr,
        )
        return 1

    dest_root = Path(args.dest).expanduser().resolve() if args.dest else Path.cwd()
    if not dest_root.is_dir():
        print(f"error: destination {dest_root} is not a directory", file=sys.stderr)
        return 1
    project_dir = dest_root / pascal

    try:
        copy_tree(template_dir, project_dir, pascal, lower)
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not args.no_git:
        try:
            git_init_and_commit(project_dir)
        except subprocess.CalledProcessError as exc:
            print(
                f"warning: git initialisation failed ({exc}). "
                f"The project files are still at {project_dir}.",
                file=sys.stderr,
            )

    print(f"Created {project_dir}")
    print(f"  project name: {pascal}")
    print(f"  bundle id:    com.mirkobraic.{lower}")
    print(f"  open with:    open {project_dir}/{pascal}.xcodeproj")
    return 0


if __name__ == "__main__":
    sys.exit(main())
