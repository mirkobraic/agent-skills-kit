# Agent Skills

Collection of agent skills for personal software development.

## Skills

- **[ios-image-metadata](skills/ios-image-metadata/SKILL.md)** — Reference skill for image metadata work on iOS/macOS. Covers ImageIO APIs, EXIF, XMP, IPTC, GPS, TIFF, ICC, orientation mapping, and interoperability across metadata standards and image formats.

## Structure

```
.claude-plugin/
  marketplace.json        — marketplace catalog
skills/
  <skill-name>/
    .claude-plugin/
      plugin.json         — plugin manifest (version lives here)
    SKILL.md              — skill entry point
```
