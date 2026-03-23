# ICC Profile Pitfalls on iOS

Common mistakes, subtle bugs, and non-obvious behaviors when working with ICC
color profiles in iOS image workflows.

---

## 1. Assuming sRGB When the Image Is Display P3

**The problem:** Code that treats all RGB images as sRGB will desaturate
wide-gamut content. On iPhones with P3 displays (iPhone 7+), the camera
captures in Display P3 by default. If you process pixel data assuming sRGB
values, reds will appear less vivid and greens less saturated than the
photographer intended.

**How common this is:** Very. Every iPhone photo since late 2016 is Display P3.
Any app that processes user photos will encounter P3 images routinely.

**Detection:**

```swift
if let colorSpace = cgImage.colorSpace {
    if #available(iOS 12.0, *) {
        if colorSpace.isWideGamutRGB {
            // This image has a gamut wider than sRGB
            // Display P3, Adobe RGB, Rec. 2020, ProPhoto RGB, etc.
        }
    }
    // Or check the name directly:
    if colorSpace.name == CGColorSpace.displayP3 {
        // Display P3 image
    }
}
```

**Fix:** Always respect the image's `CGColorSpace`. When performing pixel-level
operations, work in the image's native color space or convert explicitly:

```swift
// Convert to a known color space for pixel processing
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
let context = CGContext(
    data: nil, width: w, height: h,
    bitsPerComponent: 8, bytesPerRow: 0,
    space: srgb,
    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
)
context?.draw(cgImage, in: CGRect(x: 0, y: 0, width: w, height: h))
// Pixel data is now sRGB -- ColorSync performed the conversion
```

**Subtlety:** If you create a `CGContext` with sRGB and draw a P3 image into it,
the conversion is automatic and correct. But if you read raw pixel bytes from a
P3 image and treat them as sRGB without converting, colors will be wrong. The
P3 value (255, 0, 0) represents a deeper red than sRGB (255, 0, 0).

---

## 2. kCGImageDestinationOptimizeColorForSharing Silently Converts to sRGB

**The problem:** Setting `kCGImageDestinationOptimizeColorForSharing = true`
converts wide-gamut images to sRGB without any warning or callback. For
Display P3 images, colors outside the sRGB gamut are permanently clipped.
This is data loss that cannot be undone.

**When it matters:**

- A vibrant sunset photo captured in Display P3 has deep oranges and reds
  that sRGB cannot represent. After conversion, those colors are flattened.
- An app that "optimizes for sharing" before saving to the user's photo
  library permanently degrades the image.

**What exactly happens:** The option uses Relative Colorimetric rendering
intent, which clips out-of-gamut colors to the nearest sRGB color. In-gamut
colors are preserved accurately, but the ~25% of the P3 gamut that extends
beyond sRGB is lost.

**Safer alternatives:**

1. Only use this option when actually sharing (AirDrop, social media upload).
2. Keep the original wide-gamut image in storage.
3. Convert on export, not on save:

```swift
// Only convert at the point of sharing, not storage
func prepareForSharing(original: CGImage, to url: URL) {
    let dest = CGImageDestinationCreateWithURL(
        url as CFURL, UTType.jpeg.identifier as CFString, 1, nil)!
    let opts: [CFString: Any] = [
        kCGImageDestinationOptimizeColorForSharing: true
    ]
    CGImageDestinationAddImage(dest, original, opts as CFDictionary)
    CGImageDestinationFinalize(dest)
}
```

**Bonus use case:** This option is also useful for handling images with unusual
or unrecognized color spaces (uRGB, eciRGB v2, device-specific profiles) that
cause issues when loaded via Core Image. Converting to sRGB normalizes the
color space for downstream processing.

---

## 3. ICC v2 vs v4 Compatibility

**The problem:** ICC v4 profiles may not be recognized by older software,
web browsers, or third-party image processing libraries. When a v4 profile
is not recognized, the image may render with incorrect colors or fall back
to an assumed sRGB.

**Current landscape (2025+):**

| Software | v4 Support |
|----------|-----------|
| Apple ColorSync (iOS/macOS) | Full support |
| Chrome/Edge | Full support |
| Firefox | Full support |
| Safari | Full support |
| Adobe Photoshop/Lightroom | Full support (but defaults to writing v2) |
| Older Windows GDI apps | Limited or no support |
| Legacy prepress RIPs | May not support v4 |
| Some third-party iOS SDKs | May parse ICC themselves, ignoring v4 features |

**Apple's behavior:** CoreGraphics and ColorSync fully support both v2 and v4.
Apple's built-in named color spaces handle versioning internally. You only
encounter this issue when:

1. Embedding third-party ICC profiles (e.g., from a color calibrator).
2. Processing images with custom ICC parsing code.
3. Sharing files with non-Apple platforms running legacy software.

**Mitigation:** When maximum compatibility is required, use v2 profiles or
convert to sRGB (which has a universally recognized v2 profile). Adobe
applications default to writing v2 profiles for embedded images for exactly
this reason.

---

## 4. Missing ICC Profile Defaults

**The problem:** When an image file has no embedded ICC profile, different
renderers make different assumptions:

| Renderer | Default Assumption |
|----------|-------------------|
| Web browsers (per W3C) | sRGB |
| Apple ColorSync | sRGB (for RGB images) |
| Adobe Photoshop | Configurable (usually sRGB or Adobe RGB) |
| Windows Photo Viewer | sRGB (or no management) |
| GIMP | sRGB (configurable) |
| Core Image (iOS) | sRGB |

**When this matters:**

- An image edited in Adobe RGB with the profile stripped will appear
  oversaturated in sRGB-assuming renderers (because Adobe RGB values are
  being interpreted as sRGB, and the green primary is much wider).
- A Display P3 image with the profile stripped will have incorrect colors
  everywhere because P3 values are being interpreted as sRGB.
- GIF images (which cannot embed profiles) are always treated as sRGB.

**Fix:** Always embed an ICC profile in images that are not sRGB. Even for
sRGB images, embedding the profile is best practice -- it removes ambiguity.

**Special case -- HEIF/HEIC:** HEIF files without an explicit `colr` box
default to specific CICP values (primaries=1/sRGB, transfer=13/sRGB). This
is defined in the HEIF specification, not left to renderer interpretation.

---

## 5. CMYK Images on iOS

**The problem:** iOS has limited CMYK support. While `CGColorSpace.genericCMYK`
exists, and ImageIO can read CMYK images (JPEG, TIFF, PSD), the rendering
pipeline has significant constraints:

- **UIKit cannot render CMYK directly.** UIImage will convert CMYK to RGB
  internally, but the conversion quality depends on having a valid ICC profile.
- **No CMYK bitmap contexts on iOS.** You cannot create a `CGContext` with
  a CMYK color space on iOS (this works on macOS). Attempting to do so will
  return `nil`.
- **Metal and GPU rendering assume RGB.** CMYK textures cannot be uploaded
  to the GPU.
- **Color accuracy depends on the profile.** Without a CMYK ICC profile,
  there is no mathematically correct way to convert CMYK to RGB -- the
  mapping is device-dependent. The generic CMYK profile provides a
  reasonable approximation but may not match the intended output device.

**Practical impact:**

```swift
// This CAN work on iOS -- ImageIO reads the CMYK data:
let source = CGImageSourceCreateWithURL(cmykJpegURL as CFURL, nil)!
let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil)!
// cgImage.colorSpace?.model == .cmyk  (true -- it's still CMYK)

// Drawing it triggers automatic CMYK -> RGB conversion via ColorSync
let uiImage = UIImage(cgImage: cgImage)
// Display may be correct IF the CMYK file had a valid ICC profile

// BUT: trying to create a CMYK CGContext on iOS fails:
let cmykContext = CGContext(
    data: nil, width: 100, height: 100,
    bitsPerComponent: 8, bytesPerRow: 0,
    space: CGColorSpace(name: CGColorSpace.genericCMYK)!,
    bitmapInfo: CGImageAlphaInfo.none.rawValue
)
// cmykContext is nil on iOS!
```

**Recommendations:**

- Convert CMYK images to RGB server-side before sending to iOS.
- If you must handle CMYK on iOS, use Core Image (`CIImage`) which has
  better color space conversion support.
- Always preserve the CMYK ICC profile during any processing -- it is
  essential for accurate color conversion.
- Consider displaying a warning when CMYK images are detected, since the
  on-screen rendering may not match the intended print output.

---

## 6. Profile Stripping Through UIImage Round-Trips

**The problem:** Creating a `UIImage` from file data and then exporting with
`jpegData(compressionQuality:)` or `pngData()` does NOT preserve the original
ICC profile:

```swift
// Original file: Display P3 JPEG with embedded Display P3 ICC profile
let image = UIImage(contentsOfFile: displayP3Path)!

// Re-encode -- ICC profile is LOST
let data = image.jpegData(compressionQuality: 0.9)!

// The resulting JPEG has an sRGB profile (or device RGB),
// but the pixel values may still be P3-encoded.
// Result: colors are wrong.
```

**Why it happens:** UIImage's JPEG/PNG export methods create a new file from
the in-memory bitmap representation. The bitmap may have been converted to
the device's color space during UIImage creation. The export methods embed
whatever color space the internal bitmap uses (typically sRGB or device RGB),
which may or may not match the original file's color space.

**What gets lost:** Not just the ICC profile, but potentially ALL metadata --
EXIF, GPS, IPTC, XMP, and auxiliary data (gain maps, depth maps).

**Fix:** Use `CGImageSource` and `CGImageDestination` for any workflow where
color fidelity matters:

```swift
func preserveProfile(inputURL: URL, outputURL: URL, quality: CGFloat) {
    guard let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
          let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil),
          let dest = CGImageDestinationCreateWithURL(
              outputURL as CFURL, UTType.jpeg.identifier as CFString, 1, nil
          ) else { return }

    var opts = properties as! [CFString: Any]
    opts[kCGImageDestinationLossyCompressionQuality as CFString] = quality

    CGImageDestinationAddImage(dest, image, opts as CFDictionary)
    CGImageDestinationFinalize(dest)
    // Output JPEG has the same ICC profile as the input
}
```

**Alternative for UIImage-based workflows:** Use `UIGraphicsImageRenderer`
which respects the trait collection's display gamut:

```swift
let format = UIGraphicsImageRendererFormat()
format.preferredRange = .automatic  // Preserves wide color if available
let renderer = UIGraphicsImageRenderer(size: image.size, format: format)
```

---

## 7. HDR Gain Maps and Tone Mapping

**The problem:** Starting with iPhone 12 (iOS 14.1), Apple captures photos
with HDR gain maps. These are auxiliary data stored alongside the SDR base
image. The gain map allows the system to boost brightness on HDR-capable
displays (Extended Dynamic Range / EDR).

**Color management implications:**

- The SDR base image is typically Display P3 with a standard sRGB-like TRC.
- The gain map encodes per-pixel HDR headroom (how much brighter each pixel
  can be).
- When displayed on an EDR-capable screen, the system applies the gain map
  to extend luminance beyond 1.0 (SDR white).
- If you strip the gain map (by re-encoding through UIImage or not preserving
  auxiliary data), the image loses its HDR capability.

**ISO 21496-1 (Adaptive HDR):** Apple and Google cooperatively adopted this
ISO standard (published 2025) for interoperable HDR gain maps. The new constant
`kCGImageAuxiliaryDataTypeISOGainMap` (iOS 18+) represents the standardized
format, complementing Apple's proprietary gain map format
(`kCGImageAuxiliaryDataTypeHDRGainMap`, iOS 14.1+).

**Preserving HDR through processing:**

```swift
// Read gain map auxiliary data
let gainMapInfo = CGImageSourceCopyAuxiliaryDataInfoAtIndex(
    source, 0,
    kCGImageAuxiliaryDataTypeHDRGainMap as CFString
)

// Also check for ISO gain map (iOS 18+)
if #available(iOS 18.0, *) {
    let isoGainMap = CGImageSourceCopyAuxiliaryDataInfoAtIndex(
        source, 0,
        kCGImageAuxiliaryDataTypeISOGainMap as CFString
    )
}

// When writing, add it back
if let gainMapInfo = gainMapInfo as? [CFString: Any] {
    CGImageDestinationAddAuxiliaryDataInfo(
        destination,
        kCGImageAuxiliaryDataTypeHDRGainMap as CFString,
        gainMapInfo as CFDictionary
    )
}
```

**Color space interaction:** HDR content may use extended color spaces:
- `CGColorSpace.extendedSRGB` -- sRGB primaries, values > 1.0 for HDR
- `CGColorSpace.extendedDisplayP3` -- P3 primaries, values > 1.0
- `CGColorSpace.displayP3_HLG` -- P3 with HLG transfer function
- `CGColorSpace.itur_2020_PQ` -- Rec. 2020 with PQ transfer function

The gain map itself is typically grayscale and does not carry a color space
in the traditional sense -- it encodes luminance ratios.

---

## 8. Large ICC Profiles in JPEG

**The problem:** JPEG APP2 segments are limited to ~64 KB each. Large ICC
profiles (CMYK output profiles can be 500 KB - 2 MB) must be chunked across
multiple APP2 segments. Some software does not correctly reassemble chunked
profiles.

**Symptoms:**

- Image opens with wrong colors (profile not found).
- Only the first 64 KB of the profile is read (partial profile = corrupted).
- Software reports "invalid ICC profile".

**Apple's handling:** ImageIO correctly reads and reassembles chunked
ICC profiles in JPEG. This is a non-issue when using Apple's APIs. It
becomes a problem when:

1. Using third-party JPEG libraries that do not handle chunking.
2. Manually parsing JPEG metadata without proper APP2 chunking support.
3. A buggy encoder writes incorrect sequence numbers or total count.

**Technical details:**
- Maximum 255 chunks per ICC profile (sequence number is 1 byte).
- Each chunk carries up to 65,519 bytes of profile data.
- Maximum total profile size: ~16.3 MB.
- Decoders must use sequence numbers, not file order, for reassembly.

**Mitigation:** When writing JPEG with large profiles, prefer smaller profiles
or convert to a simpler profile (sRGB, Display P3) if the CMYK profile is
only needed for specific workflows.

---

## 9. Generic Profiles vs Device-Specific Profiles

**The problem:** Generic profiles (like Apple's "Generic RGB Profile" or
"Color LCD") are not standardized ICC profiles. They represent the current
system's default color space, which varies across devices.

**Why it matters:**

- A JPEG tagged with "Color LCD" on one Mac will have a different color
  rendering on another Mac with a different display profile.
- "Generic RGB Profile" is a system-dependent profile that may or may not
  match sRGB -- it depends on the Mac's display calibration.
- These profiles have no meaning on non-Apple devices.

**Common generic profile names to watch for:**

| Profile Name | Source | Issue |
|-------------|--------|-------|
| `"Generic RGB Profile"` | macOS system default | Device-dependent |
| `"Color LCD"` | macOS display profile | Specific to one display |
| `"Apple RGB"` | Legacy Apple profile | Non-standard, obsolete |
| `"Generic CMYK Profile"` | macOS system CMYK | Approximation only |
| `"sRGB"` (without "IEC61966") | Some tools | May be non-standard variant |

**Detection and fix:**

```swift
if let profileName = properties[kCGImagePropertyProfileName] as? String {
    let genericProfiles = [
        "Generic RGB Profile",
        "Color LCD",
        "Apple RGB",
    ]
    if genericProfiles.contains(profileName) {
        // This image has a device-specific or generic profile.
        // Consider converting to sRGB or Display P3 for portability.
    }
}

// More reliable: check if it matches a named CGColorSpace
if let colorSpace = cgImage.colorSpace,
   colorSpace.name == nil {
    // No named match -- this is a custom or device-specific profile.
    // The profile may not be portable.
}
```

**Best practice:** When saving images for distribution, always convert to a
well-known standard profile (sRGB, Display P3, Adobe RGB). Never embed
device-specific or generic system profiles in images intended for sharing.

---

## 10. EXIF ColorSpace Tag Mismatch

**The problem:** The EXIF `ColorSpace` tag (tag 40961) only has two meaningful
values: 1 (sRGB) and 65535 (Uncalibrated). When an image has a Display P3 ICC
profile but the EXIF tag says sRGB (1), non-color-managed software may
incorrectly treat it as sRGB.

**How iPhones handle it:**

- When capturing in Display P3, iPhone writes `ColorSpace = 65535`
  (Uncalibrated) in EXIF and embeds the Display P3 ICC profile (or nclx CICP
  in HEIC). This is correct -- it tells EXIF-only readers "don't assume sRGB."
- Some third-party cameras and apps write `ColorSpace = 1` (sRGB) even when
  the embedded ICC profile is not sRGB. This mismatch causes problems.

**Impact:** A viewer that reads only EXIF (and not the ICC profile) will
assume sRGB and display incorrect colors for wide-gamut images.

**Precedence rule:** In a color-managed renderer, the ICC profile takes
precedence over the EXIF ColorSpace tag. The EXIF tag is a hint for
non-color-managed renderers, not a definitive color space declaration.

**Fix:** When writing images, ensure the EXIF `ColorSpace` tag is consistent
with the ICC profile:

```swift
var exifDict = (properties[kCGImagePropertyExifDictionary]
    as? [CFString: Any]) ?? [:]

if let colorSpace = cgImage.colorSpace, colorSpace.name == CGColorSpace.sRGB {
    exifDict[kCGImagePropertyExifColorSpace] = 1  // sRGB
} else {
    exifDict[kCGImagePropertyExifColorSpace] = 65535  // Uncalibrated
}

// Write back to properties
var mutableProps = properties as! [CFString: Any]
mutableProps[kCGImagePropertyExifDictionary as CFString] = exifDict
```

---

## Summary Table

| # | Pitfall | Severity | Fix |
|---|---------|----------|-----|
| 1 | Assuming sRGB for P3 images | High | Check `isWideGamutRGB` / profile name |
| 2 | OptimizeColorForSharing is lossy | High | Use only for sharing, not archival |
| 3 | ICC v4 compatibility | Medium | Use v2 profiles for maximum compatibility |
| 4 | Missing profile defaults | Medium | Always embed ICC profiles |
| 5 | CMYK on iOS | Medium | Convert to RGB server-side; no CMYK CGContext on iOS |
| 6 | UIImage strips ICC profile | High | Use CGImageSource/Destination instead |
| 7 | HDR gain map loss | Medium | Preserve auxiliary data explicitly |
| 8 | Large JPEG ICC chunking | Low | Apple handles it; watch third-party libs |
| 9 | Generic/device profiles | Medium | Convert to standard profiles before sharing |
| 10 | EXIF ColorSpace mismatch | Medium | Set 65535 for non-sRGB images |

---

## Quick Reference: Profile-Safe vs Profile-Unsafe Operations

| Operation | Profile Safe? | Notes |
|-----------|--------------|-------|
| `CGImageSourceCreateImageAtIndex` | Yes | Preserves CGColorSpace |
| `CGImageDestinationAddImage` | Yes | Embeds profile from CGColorSpace |
| `CGImageDestinationCopyImageSource` | Yes | Byte-for-byte preservation |
| `UIImage(contentsOfFile:)` | Partial | May convert to device space |
| `UIImage.jpegData(compressionQuality:)` | No | Strips profile, may convert |
| `UIImage.pngData()` | No | Strips profile, may convert |
| `CIImage` processing | Depends | Working space may differ from source |
| `CGContext.draw(_:in:)` | Converts | Automatic ColorSync conversion to context space |
| `kCGImageDestinationOptimizeColorForSharing` | Intentional | Converts to sRGB by design |

---

## Cross-References

- [Profile Basics](profile-basics.md) -- ICC structure and version differences
- [Common Profiles](common-profiles.md) -- sRGB, Display P3, Adobe RGB characteristics
- [Embedding](embedding.md) -- Per-format profile embedding (JPEG chunking, PNG compression)
- [ImageIO Integration](imageio-integration.md) -- Reading/writing profiles with Apple APIs
- [`imageio/pitfalls.md`](../imageio/pitfalls.md) -- UIImage metadata loss, orientation, threading
- [`exif/pitfalls.md`](../exif/pitfalls.md) -- EXIF-specific pitfalls including ColorSpace tag
