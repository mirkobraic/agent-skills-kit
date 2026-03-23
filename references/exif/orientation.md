# EXIF Orientation

> Part of [EXIF Reference](README.md)

Orientation tag (0x0112) lives in IFD0 and indicates how the image should be
rotated/mirrored for correct display. This is one of the most commonly accessed
EXIF tags. For ImageIO orientation constants and UIImage differences, see
[`imageio-mapping.md`](imageio-mapping.md#orientation-in-imageio).

---

## Orientation Values

The value describes the position of row 0 and column 0 of the stored pixel
data relative to the visual image:

| Value | Row 0 Position | Col 0 Position | Transform to Display |
|-------|---------------|----------------|---------------------|
| 1 | Top | Left | Normal (no transform) |
| 2 | Top | Right | Horizontal flip |
| 3 | Bottom | Right | 180° rotation |
| 4 | Bottom | Left | Vertical flip |
| 5 | Left | Top | Transpose (90° CW + horizontal flip) |
| 6 | Right | Top | 90° clockwise |
| 7 | Right | Bottom | Transverse (90° CW + vertical flip) |
| 8 | Left | Bottom | 90° counter-clockwise |

### Visual Reference

```
Value 1       Value 2       Value 3       Value 4
■ ■ □ □       □ □ ■ ■       □ □ □ □       □ □ □ □
■ □ □ □       □ □ □ ■       □ □ □ ■       ■ □ □ □
□ □ □ □       □ □ □ □       ■ □ □ □       □ □ □ ■
□ □ □ □       □ □ □ □       ■ ■ □ □       □ □ ■ ■

Value 5       Value 6       Value 7       Value 8
■ ■ □ □       □ □ □ ■       □ □ ■ ■       ■ □ □ □
■ □ □ □       □ □ □ ■       □ □ □ ■       □ □ □ ■
□ □ □ □       □ □ ■ □       □ □ ■ □       □ ■ □ □
□ □ □ □       □ □ ■ ■       ■ ■ □ □       ■ ■ □ □
```

---

## Common Camera Values

| Shooting Position | EXIF Orientation | Value |
|-------------------|-----------------|-------|
| Landscape, sensor top = scene top | 1 (normal) | Most common default |
| Landscape, camera upside-down | 3 (180°) | |
| Portrait, sensor top = scene right | 6 (90° CW) | Standard portrait on most phones |
| Portrait, sensor top = scene left | 8 (90° CCW) | |

iPhones default to orientation 6 when shooting portrait (home button at bottom).

---

## XMP Representation

In XMP, orientation maps to `tiff:Orientation` as an integer with the same
1–8 values. See [`xmp-mapping.md`](xmp-mapping.md#ifd0-tags--tiff-namespace).

---

## Orientation Pitfalls

- **Duplication:** Orientation exists in both IFD0 (tag 0x0112) and may be
  duplicated at other levels by software. Ensure consistency when editing.
- **Pixel data vs display:** The orientation tag does NOT change the stored
  pixels. It tells viewers how to transform when displaying. Some software
  "bakes in" the rotation (rewrites pixels) and resets orientation to 1.
- **Thumbnail mismatch:** The thumbnail in IFD1 may have different orientation
  than the main image if software only updated one.
