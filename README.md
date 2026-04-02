# Agent Skills Kit

Collection of Claude Code plugins for personal software development.

## Plugins

### ios-image-metadata

Reference plugin for image metadata work on iOS/macOS. Contains 8 focused skills:

| Skill | Description |
|-------|-------------|
| `imageio` | ImageIO APIs, property keys, format support matrices |
| `exif` | EXIF tags, IFD structure, MakerNote fields |
| `xmp` | XMP data model, namespaces, embedding |
| `iptc` | IPTC IIM + Extension, editorial/rights metadata |
| `gps` | GPS coordinates, sign/ref conventions |
| `tiff` | TIFF IFD tags, container structure |
| `icc` | ICC color profiles, Display P3 |
| `metadata-sync` | Cross-standard reconciliation, orientation mapping |

## Structure

```
.claude-plugin/
  marketplace.json              — marketplace catalog
plugins/
  <plugin-name>/
    .claude-plugin/
      plugin.json               — plugin manifest
    skills/
      <skill-name>/
        SKILL.md                — skill entry point
        references/             — reference documentation
```

## Usage

Add this marketplace to Claude Code:

```
/plugin marketplace add <repo-url>
/plugin install ios-image-metadata
```

Skills become available as `ios-image-metadata:<skill-name>` (e.g., `ios-image-metadata:exif`).
