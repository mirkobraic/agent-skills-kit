# GIF Format Reference

GIF (Graphics Interchange Format) is a bitmap image format introduced by
CompuServe in 1987 (GIF87a) and updated in 1989 (GIF89a). It supports
animation, transparency, and palette-based color (up to 256 colors per frame).

GIF has **virtually no metadata support** -- it does not support EXIF, IPTC
IIM, ICC profiles, or GPS data. The XMP specification (Part 3) defines an
Application Extension mechanism for embedding XMP in GIF (`"XMP DataXMP"`),
but this is rarely used in practice and not supported by ImageIO. GIF's
primary relevance to ImageIO is animation (frame timing, loop count,
disposal methods).

---

## File Signature

```
GIF87a    -- version 87a (6 bytes: 47 49 46 38 37 61)
GIF89a    -- version 89a (6 bytes: 47 49 46 38 39 61)
```

The first six bytes identify the GIF version. Modern GIF files are virtually
always GIF89a.

---

## Version Comparison

| Feature                   | GIF87a (1987) | GIF89a (1989) |
|---------------------------|---------------|---------------|
| Raster image data         | Yes           | Yes           |
| Palette (up to 256 colors)| Yes          | Yes           |
| Interlacing               | Yes           | Yes           |
| Transparency              | No            | Yes           |
| Animation                 | No            | Yes           |
| Comment Extension         | No            | Yes           |
| Plain Text Extension      | No            | Yes           |
| Application Extension     | No            | Yes           |

---

## File Structure

### Overall Layout

```
Header                      "GIF87a" or "GIF89a" (6 bytes)
Logical Screen Descriptor   Canvas size, color table flags, background, aspect
[Global Color Table]        Optional (up to 256 RGB entries)

-- Repeated per frame: --
[Graphic Control Extension] GIF89a: delay, disposal, transparency
[Image Descriptor]          Frame position, size, local color table flags
[Local Color Table]         Optional per-frame palette
[Image Data]                LZW-compressed pixel indices

-- Other extensions (GIF89a): --
[Comment Extension]         Text comment (unstructured ASCII)
[Plain Text Extension]      Text overlay (rarely used)
[Application Extension]     App-specific (e.g., NETSCAPE2.0 loop count)

Trailer                     0x3B (1 byte, end of file)
```

---

## Logical Screen Descriptor

Immediately follows the header. Defines the canvas for all frames.

| Field               | Bytes | Description                           |
|---------------------|-------|---------------------------------------|
| Canvas Width        | 2     | Logical screen width (little-endian)  |
| Canvas Height       | 2     | Logical screen height (little-endian) |
| Packed Field        | 1     | Bit-packed flags (see below)          |
| Background Color    | 1     | Index into Global Color Table         |
| Pixel Aspect Ratio  | 1     | Aspect ratio hint (0 = not given)     |

**Packed Field bits:**

| Bits | Meaning                                      |
|------|----------------------------------------------|
| 7    | Global Color Table Flag (1 = present)        |
| 4-6  | Color Resolution (bits per primary color - 1)|
| 3    | Sort Flag (1 = GCT is sorted)               |
| 0-2  | Size of Global Color Table (N; table has 2^(N+1) entries) |

---

## Global Color Table

If the Global Color Table Flag is set, a color table follows with 3 bytes per
entry (R, G, B). The table contains `2^(N+1)` entries where N is the GCT Size
field (0-7), supporting up to 256 entries (768 bytes maximum).

---

## Graphic Control Extension (GIF89a)

Precedes each frame and controls animation timing, disposal, and transparency.
This is the key extension that enables GIF animation.

```
21 F9          Extension Introducer (0x21) + GCE Label (0xF9)
04             Block size (always 4 bytes of data)
[Packed]       Bit-packed flags
[Delay Time]   2 bytes, little-endian, in 1/100ths of a second
[Transparent Color Index]  1 byte
00             Block terminator
```

**Packed Field bits:**

| Bits | Meaning                                          |
|------|--------------------------------------------------|
| 5-7  | Reserved                                         |
| 2-4  | Disposal Method (0-7)                            |
| 1    | User Input Flag (wait for user action)           |
| 0    | Transparent Color Flag (1 = index is transparent)|

### Disposal Methods

| Value | Name                  | Behavior                                   |
|-------|-----------------------|--------------------------------------------|
| 0     | Unspecified           | Decoder chooses (typically same as 1)       |
| 1     | Do Not Dispose        | Frame remains in place; next frame draws over it |
| 2     | Restore to Background | Frame area is cleared to background color   |
| 3     | Restore to Previous   | Frame area is restored to state before this frame |
| 4-7   | Reserved              | Undefined; decoders typically treat as 0    |

**Disposal method significance for animation:**
- **Method 1** (Do Not Dispose) is used for animations where frames
  accumulate (each frame adds to the previous).
- **Method 2** (Restore to Background) is used for animations where each
  frame is drawn on a clean canvas.
- **Method 3** (Restore to Previous) is used for sprite-style animations
  where a moving element is drawn over a static background.

### Frame Delay

The delay time is in hundredths of a second (10 ms units). Special cases:

| Delay Value | Behavior                                       |
|-------------|------------------------------------------------|
| 0           | Undefined; browsers typically use 100 ms       |
| 1           | 10 ms; browsers typically clamp to 100 ms      |
| 2-5         | 20-50 ms; some browsers clamp to 100 ms        |
| >= 6        | Used as specified (60+ ms)                     |

**ImageIO delay keys:**

| Key                                        | Behavior                                   |
|--------------------------------------------|--------------------------------------------|
| `kCGImagePropertyGIFDelayTime`             | Clamped: values < 0.1s are rounded up to 0.1s |
| `kCGImagePropertyGIFUnclampedDelayTime`    | Actual delay value from the file           |

Always use `kCGImagePropertyGIFUnclampedDelayTime` for accurate animation
playback. The clamped version matches browser behavior but distorts
fast-animation GIFs.

---

## Image Descriptor

Each frame has an Image Descriptor defining its position and dimensions within
the canvas.

| Field               | Bytes | Description                           |
|---------------------|-------|---------------------------------------|
| Image Separator     | 1     | Always 0x2C (comma)                  |
| Left Position       | 2     | X offset from canvas left edge       |
| Top Position        | 2     | Y offset from canvas top edge        |
| Width               | 2     | Frame width in pixels                 |
| Height              | 2     | Frame height in pixels                |
| Packed Field        | 1     | Local color table flag, interlace, sort, LCT size |

Frames can be smaller than the canvas and positioned anywhere within it, which
enables efficient partial-frame animation.

---

## NETSCAPE Application Extension (Loop Count)

The NETSCAPE2.0 Application Extension controls how many times an animated GIF
loops. This is a de facto standard -- not part of the original GIF89a
specification, but universally supported.

```
21 FF          Extension Introducer + Application Extension Label
0B             Block size (11 bytes)
"NETSCAPE2.0"  Application identifier (11 bytes)
03             Sub-block size (3 bytes)
01             Sub-block ID (always 1 for loop count)
[Loop Count]   2 bytes, little-endian
00             Block terminator
```

| Loop Count Value | Meaning                                    |
|------------------|--------------------------------------------|
| 0                | Loop forever (infinite)                    |
| 1                | Play once (no repeat after initial play)   |
| N                | Play N additional times (N+1 total plays)  |

**Ambiguity warning:** Some implementations treat the loop count as "number
of additional plays" (so 1 = play twice total), while others treat it as
total plays (so 1 = play once). ImageIO uses `kCGImagePropertyGIFLoopCount`
with 0 = infinite.

---

## Comment Extension (GIF89a)

The Comment Extension stores arbitrary ASCII text. It is the only form of
textual metadata in GIF.

```
21 FE          Extension Introducer + Comment Extension Label
[Sub-blocks]   One or more data sub-blocks (1-255 bytes each)
00             Block terminator
```

Comments are rarely used and have no structured format. They are **not**
exposed by ImageIO's property dictionary system.

---

## Plain Text Extension (GIF89a)

The Plain Text Extension defines a text overlay to be rendered using a
built-in monospace font on a specified grid. In practice, this extension is
almost never used and is not supported by most modern renderers, browsers,
or ImageIO. It is included here only for completeness.

---

## LZW Compression

GIF uses Lempel-Ziv-Welch (LZW) compression for image data. The compressed
data follows the Image Descriptor (and optional Local Color Table) as a
sequence of sub-blocks, each prefixed by a size byte (1-255), terminated by
a zero-length sub-block (0x00).

The LZW minimum code size (1 byte) precedes the sub-blocks and determines
the initial code width. For most images, this is equal to the color table's
bit depth (e.g., 8 for a 256-color image).

**LZW patent history:** The LZW algorithm was subject to Unisys patents that
expired in 2003-2004 worldwide. This is no longer a concern but historically
drove the development of PNG as a patent-free alternative.

---

## Color Limitations

| Property          | Value                                       |
|-------------------|---------------------------------------------|
| Max colors        | 256 per frame (8-bit palette index)         |
| Color tables      | Global + optional per-frame local tables    |
| Transparency      | 1-bit (one palette index marked transparent)|
| Alpha channel     | No (binary transparency only)               |
| Color depth       | 24-bit RGB palette entries                  |
| Interlacing       | Supported (4-pass scheme)                   |
| Bit depth         | 1 to 8 bits per pixel (palette index)       |

---

## Metadata Capacity Summary

| Standard    | Supported | Notes                                         |
|-------------|-----------|-----------------------------------------------|
| **EXIF**    | No        | No mechanism for EXIF data                    |
| **XMP**     | Limited   | XMP Spec Part 3 defines Application Extension mechanism, but rarely used and not supported by ImageIO |
| **IPTC IIM**| No        | No mechanism for IPTC data                    |
| **ICC**     | No        | No color profile support; limited to palette  |
| **GPS**     | No        | No location data support                      |
| **Comment** | Yes (limited) | Comment Extension (unstructured ASCII text) |

GIF is the only common image format with essentially **no practical**
structured metadata support. While the XMP specification defines a GIF
Application Extension mechanism, it is not widely adopted. If metadata is
needed, convert to a format with robust support (PNG, JPEG, HEIC).

---

## ImageIO Keys: `kCGImagePropertyGIFDictionary`

Available since iOS 4.0.

| Key                                        | Type      | Purpose                            |
|--------------------------------------------|-----------|------------------------------------|
| `kCGImagePropertyGIFLoopCount`             | CFNumber  | Loop count (0 = infinite)          |
| `kCGImagePropertyGIFDelayTime`             | CFNumber  | Frame delay (seconds, clamped >= 0.1) |
| `kCGImagePropertyGIFUnclampedDelayTime`    | CFNumber  | True frame delay (not clamped)     |
| `kCGImagePropertyGIFImageColorMap`         | CFData    | Per-frame local color table data   |
| `kCGImagePropertyGIFHasGlobalColorMap`     | CFBoolean | Has global color map               |
| `kCGImagePropertyGIFCanvasPixelWidth`      | CFNumber  | Canvas width in pixels             |
| `kCGImagePropertyGIFCanvasPixelHeight`     | CFNumber  | Canvas height in pixels            |
| `kCGImagePropertyGIFFrameInfoArray`        | CFArray   | Frame information array            |

---

## ImageIO Animation Support

GIF animation in ImageIO uses two approaches:

### Per-Frame Access (iOS 4.0+)

```swift
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let frameCount = CGImageSourceGetCount(source)

for i in 0..<frameCount {
    let image = CGImageSourceCreateImageAtIndex(source, i, nil)
    let props = CGImageSourceCopyPropertiesAtIndex(source, i, nil) as? [CFString: Any]
    let gifDict = props?[kCGImagePropertyGIFDictionary] as? [CFString: Any]

    // Read delay time
    let delay = gifDict?[kCGImagePropertyGIFUnclampedDelayTime] as? Double
        ?? gifDict?[kCGImagePropertyGIFDelayTime] as? Double
        ?? 0.1
}
```

### Animated Playback (iOS 13.0+)

```swift
CGAnimateImageAtURLWithBlock(url as CFURL, nil) { index, image, stop in
    // Called for each frame at the correct timing
    // ImageIO handles frame delays, disposal methods, and looping
}
```

The `CGAnimateImageAtURLWithBlock` API handles all animation complexities
(disposal methods, transparency, timing) automatically.

---

## Key Characteristics for iOS Development

| Property              | Value                                          |
|-----------------------|------------------------------------------------|
| UTI                   | `com.compuserve.gif`                           |
| ImageIO Read          | iOS 4.0+                                       |
| ImageIO Write         | iOS 4.0+                                       |
| ImageIO Dictionary    | `kCGImagePropertyGIFDictionary`                |
| Metadata Standards    | None (Comment Extension only)                  |
| Lossless Meta Edit    | No                                             |
| Color Depth           | 1-8 bit palette index (256 colors max)         |
| Color Models          | Indexed (palette-based) only                   |
| Alpha Channel         | No (1-bit transparency only)                   |
| Animation             | Yes (iOS 4.0+ frames, iOS 13.0+ animate API)  |
| Compression           | LZW (lossless for palette data)                |
| Max Dimensions        | 65,535 x 65,535 pixels (16-bit fields)         |

---

## Common Gotchas

1. **No metadata** -- GIF simply has no support for EXIF, XMP, IPTC, or ICC.
   Do not attempt to write metadata to GIF files. If you need metadata on
   an animated image, consider APNG or animated WebP.

2. **Delay time clamping** -- Browsers and ImageIO clamp frame delays below
   100 ms (0.1s) to prevent runaway animation. Use the unclamped delay key
   for faithful reproduction.

3. **Loop count semantics** -- The NETSCAPE2.0 loop count field has ambiguous
   semantics across implementations. A value of 0 universally means infinite,
   but non-zero values may be interpreted differently. Test on target platforms.

4. **256 color limit** -- Each frame is limited to 256 colors from its palette.
   Color banding is common with photographic content. GIF is best suited for
   graphics, logos, and simple animations.

5. **No lossless metadata editing** -- There is no meaningful metadata to edit,
   and `CGImageDestinationCopyImageSource` does not support GIF for lossless
   operations.

6. **Disposal method rendering** -- Different disposal methods produce very
   different visual results. Incorrect disposal handling causes ghost frames,
   artifacts, or blank backgrounds. The `CGAnimateImageAtURLWithBlock` API
   handles this correctly.

7. **File size** -- Animated GIFs with many frames or large dimensions can be
   very large due to the palette limitation and per-frame compression.
   Consider WebP or HEICS for better compression.

---

## Cross-References

- **GIF animation API:** `references/imageio/cgimagesource.md` (animation section)
- **APNG (modern alternative):** `references/formats/png.md` (APNG section)
- **WebP animated:** `references/formats/webp.md` (animation section)
- **HEICS sequences:** `references/formats/heif.md` (sequences section)
- **ImageIO format support:** `references/imageio/supported-formats.md`
- **All GIF keys:** `references/imageio/property-keys.md` (GIF Dictionary)
