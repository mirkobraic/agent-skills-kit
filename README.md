# iOS Image Metadata Skill

Reference-first skill repository for image metadata work on Apple platforms.
It covers ImageIO APIs and metadata standards used in real iOS/macOS pipelines:
EXIF, XMP, IPTC, GPS, TIFF, ICC, interoperability behavior, and format-specific
constraints.

## Start Here

- `SKILL.md` — primary skill entry point and quick routing table.
- `references/README.md` — central index of all reference folders.
- `PLAN.md` — project roadmap and scope notes.

## Repository Layout

- `references/imageio/` — ImageIO API surface, property keys, formats, pitfalls
- `references/exif/`, `references/xmp/`, `references/iptc/`, `references/gps/`, `references/tiff/`, `references/icc/` — standard-specific deep dives
- `references/interoperability/` — cross-standard reconciliation and orientation mapping
- `references/formats/` — container/encoding behavior by format
- `references/makers/` — vendor MakerNote dictionaries
- `scripts/iptc_metadata.py` — ExifTool-based IPTC/XMP utility
