# IPTC Metadata Tooling Guide (ExifTool CLI Wrapper)

## Table of contents

1. Purpose
2. Prerequisites
3. Tag naming conventions
4. Common workflows
5. Read command details
6. Write command details
7. Validate command details
8. Pass-through ExifTool parameters
9. Troubleshooting

## 1. Purpose

`scripts/iptc_metadata.py` is a thin wrapper around the ExifTool CLI. It supports:

- Reading IPTC/XMP metadata and returning JSON
- Writing IPTC/XMP metadata to a file
- Validating that expected fields were written correctly (exit code + JSON report)

Use this tool when you need deterministic verification of metadata written by an app (e.g., a Swift app that writes IPTC fields).

## 2. Prerequisites

- ExifTool must be installed and available on PATH, or pass `--exiftool /path/to/exiftool`.
- Recommended install commands:
  - macOS: `brew install exiftool`
  - Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y libimage-exiftool-perl`

## 3. Tag naming conventions

- ExifTool tags are passed exactly as ExifTool expects.
- Common IPTC/XMP tag prefixes:
  - `XMP-iptcCore:`
  - `XMP-iptcExt:`
  - `XMP-plus:`
  - `XMP-xmpRights:`
  - `XMP-dc:`
  - `XMP-photoshop:`
  - `IPTC:` (legacy IIM datasets)

Namespace prefix mapping (spec docs) to ExifTool group names:

- `Iptc4xmpCore` -> `XMP-iptcCore`
- `Iptc4xmpExt` -> `XMP-iptcExt`
- `plus` -> `XMP-plus`
- `xmpRights` -> `XMP-xmpRights`
- `dc` -> `XMP-dc`
- `photoshop` -> `XMP-photoshop`

Examples:

- `XMP-iptcExt:DigitalSourceType`
- `XMP-iptcCore:Creator`
- `IPTC:Caption-Abstract`

## 4. Common workflows

### A) Read metadata (all IPTC-related)

```
python3 scripts/iptc_metadata.py read image.jpg --iptc
```

### B) Read specific tags

```
python3 scripts/iptc_metadata.py read image.jpg \
  --tags XMP-iptcExt:DigitalSourceType,XMP-iptcCore:Creator
```

### C) Write tags

```
python3 scripts/iptc_metadata.py write image.jpg \
  --set-inline XMP-iptcExt:DigitalSourceType=https://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia \
  --set-inline XMP-iptcCore:Creator=Jane Doe
```

### D) Validate tags (non-zero exit on mismatch)

```
python3 scripts/iptc_metadata.py validate image.jpg \
  --expect-inline XMP-iptcExt:DigitalSourceType=https://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia \
  --expect-inline XMP-iptcCore:Creator=Jane Doe
```

## 5. Read command details

- `read` outputs JSON to stdout, using ExifTool `-j -G1 -a -s`.
- Use `--iptc` to filter to common IPTC-related groups.
- Use `--groups` to filter custom group prefixes.
- If you pass both `--iptc` and `--groups`, the groups are merged.
- Use `--tags` to request exact tags (no filtering applied after).

Examples:

```
python3 scripts/iptc_metadata.py read image.jpg --groups XMP-iptcExt,XMP-iptcCore
python3 scripts/iptc_metadata.py read image.jpg --tags XMP-iptcCore:Creator
```

## 6. Write command details

- Provide tags via `--set` (JSON file) and/or `--set-inline` (repeatable).
- JSON must be a dictionary of `{tag: value}`. Values may be strings or lists.
- Repeating `--set-inline` or `--expect-inline` with the same tag collects values into a list.

Example JSON (`expected-tags.json`):

```
{
  "XMP-iptcExt:DigitalSourceType": "https://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
  "XMP-iptcCore:Creator": ["Jane Doe", "John Smith"]
}
```

Write using JSON:

```
python3 scripts/iptc_metadata.py write image.jpg --set expected-tags.json
```

## 7. Validate command details

- Provide expected tags via `--expect` (JSON) and/or `--expect-inline`.
- Outputs JSON with:
  - `ok`: true/false
  - `missing`: list of missing tags
  - `mismatched`: map of tag to `{expected, actual}`
- Exit code is 0 on success, 2 on mismatch/missing.
- Use `--contains` if you want expected values to be a subset of the actual list.
- Use `--unordered` to compare lists as sets.

Example (subset match):

```
python3 scripts/iptc_metadata.py validate image.jpg \
  --expect-inline XMP-iptcCore:Creator=Jane Doe \
  --contains
```

## 8. Pass-through ExifTool parameters

Use `--params` to pass additional ExifTool flags. This is useful for:

- `-overwrite_original` to avoid sidecar/backup files
- `-P` to preserve file timestamps
- `-charset` if working with specific encodings

`--params` can be repeated and also accepts comma-separated lists. Commas are treated as separators, so repeat the flag if a value must contain a literal comma.

Example:

```
python3 scripts/iptc_metadata.py write image.jpg \
  --params "-overwrite_original -P" \
  --set-inline XMP-iptcCore:Creator=Jane Doe
```

## 9. Troubleshooting

- If a tag does not appear, confirm the tag name and namespace prefix in the IPTC TechReference.
- If validation fails, run `read --tags ...` for the exact tag and compare actual values.
- If ExifTool is missing, install it or pass `--exiftool` with a full path.
