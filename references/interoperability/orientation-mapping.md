# Orientation Mapping — Three Numbering Systems

> Part of [Interoperability Reference](README.md)

Image orientation on Apple platforms involves three different numbering
systems that look similar but are **not interchangeable**. Confusing them
is one of the most common metadata bugs in iOS development.

---

## The Three Systems

| System | Values | Used By |
|--------|--------|---------|
| EXIF/TIFF Orientation | 1-8 | Image files (JPEG, HEIC, TIFF, etc.), ExifTool, all non-Apple tools |
| `CGImagePropertyOrientation` | 1-8 (same values, same meaning as EXIF) | ImageIO framework, `kCGImagePropertyOrientation`, Vision framework |
| `UIImage.Orientation` | 0-7 (**different numbering!**) | UIKit, `UIImage.imageOrientation` |

> **The critical distinction:** `CGImagePropertyOrientation` and EXIF use
> identical values (1-8). `UIImage.Orientation` uses completely different
> raw values (0-7) with different numbering. Never use `UIImage.Orientation`
> raw values where EXIF/CGImagePropertyOrientation values are expected.

---

## EXIF Orientation Values (1-8)

The EXIF specification (CIPA DC-008) defines orientation using the position
of the "0th row" and "0th column" of the stored pixel data relative to the
visual image.

### Complete Value Table

| Value | Row 0 Position | Column 0 Position | Transform to Display | Common Name |
|-------|---------------|-------------------|---------------------|-------------|
| 1 | Top | Left | None (identity) | Normal |
| 2 | Top | Right | Flip horizontal (mirror across vertical axis) | Mirrored |
| 3 | Bottom | Right | Rotate 180 | Upside down |
| 4 | Bottom | Left | Flip vertical (mirror across horizontal axis) | Mirrored upside down |
| 5 | Left | Top | Transpose (mirror across top-left to bottom-right diagonal) | Transposed |
| 6 | Right | Top | Rotate 90 CW | Rotated 90 CW |
| 7 | Right | Bottom | Transverse (mirror across top-right to bottom-left diagonal) | Transversed |
| 8 | Left | Bottom | Rotate 90 CCW (270 CW) | Rotated 90 CCW |

### Visual Diagrams

Each diagram shows the stored pixel layout. The letter `F` is used as an
asymmetric reference to show orientation. To display correctly, the viewer
must apply the inverse of the described transform.

```
Value 1 (Normal)              Value 2 (Mirrored horizontal)
+----------+                  +----------+
| F  F  F  |  -> up          |  F  F  F |  -> up
| F        |                  |        F |
| F        |                  |        F |
| F  F     |                  |     F  F |
+----------+                  +----------+
Display: as-is                Display: flip horizontally

Value 3 (Rotated 180)        Value 4 (Mirrored vertical / flipped)
+----------+                  +----------+
|     F  F |                  | F  F     |
|        F |                  | F        |
|        F |  -> up           | F        |  -> up
| F  F  F  |                  |  F  F  F |
+----------+                  +----------+
Display: rotate 180           Display: flip vertically

Value 5 (Transposed)         Value 6 (Rotated 90 CW)
+------+                      +------+
| F  F |                      |    F |
| F    |  -> up               |    F |  -> up
|      |                      | F  F |
| F  F |                      | F    |
|    F |                      | F    |
+------+                      +------+
Display: mirror + 90 CCW      Display: rotate 90 CCW

Value 7 (Transversed)        Value 8 (Rotated 90 CCW)
+------+                      +------+
| F    |                      | F    |
| F  F |  -> up               | F    |  -> up
|      |                      | F  F |
| F    |                      |    F |
| F  F |                      |    F |
+------+                      +------+
Display: mirror + 90 CW       Display: rotate 90 CW
```

### Mathematical Transforms

Each orientation value corresponds to one of the 8 elements of the dihedral
group D4 (symmetries of a square). They can be decomposed into combinations
of two primitive operations: 90-degree rotation and horizontal flip.

| Value | Rotation | Flip | Matrix (row, col -> display x, y) |
|-------|----------|------|---------------------------------|
| 1 | 0 | No | `[1 0; 0 1]` |
| 2 | 0 | Yes | `[-1 0; 0 1]` |
| 3 | 180 | No | `[-1 0; 0 -1]` |
| 4 | 180 | Yes | `[1 0; 0 -1]` |
| 5 | 90 CCW | Yes | `[0 1; 1 0]` |
| 6 | 90 CW | No | `[0 -1; 1 0]` |
| 7 | 90 CW | Yes | `[0 -1; -1 0]` |
| 8 | 90 CCW | No | `[0 1; -1 0]` |

For orientations 5-8, the display dimensions are transposed (width and
height swap).

### Common Sources in Practice

| Value | When It Occurs |
|-------|---------------|
| 1 | Landscape photo (home button right on iPhone), most desktop screenshots, images from web |
| 3 | Landscape photo (home button left on iPhone) |
| 6 | Portrait photo (home button bottom on iPhone) — **most common iPhone portrait** |
| 8 | Portrait photo (home button top on iPhone) |
| 2, 4, 5, 7 | Mirrored variants — front-facing camera selfies (especially older iOS), software transforms |

> iPhone cameras always write an orientation tag. The physical sensor is
> fixed in landscape orientation; the orientation tag tells software how
> to rotate the stored pixels for correct display.

---

## CGImagePropertyOrientation

`CGImagePropertyOrientation` is an Apple enum that uses the **same values
and semantics as EXIF orientation**. The mapping is 1:1 — no conversion
needed.

| Case | Raw Value | EXIF Equivalent |
|------|-----------|-----------------|
| `.up` | 1 | 1 (Normal) |
| `.upMirrored` | 2 | 2 (Mirrored) |
| `.down` | 3 | 3 (180) |
| `.downMirrored` | 4 | 4 (Mirrored vertical) |
| `.leftMirrored` | 5 | 5 (Transposed) |
| `.right` | 6 | 6 (90 CW) |
| `.rightMirrored` | 7 | 7 (Transversed) |
| `.left` | 8 | 8 (90 CCW) |

**Used by:**
- `kCGImagePropertyOrientation` (top-level property returned by
  `CGImageSourceCopyPropertiesAtIndex`)
- `kCGImageSourceCreateThumbnailWithTransform` (apply orientation when
  generating thumbnails)
- `kCGImageDestinationOrientation` (set orientation during lossless copy)
- Vision framework `VNImageRequestHandler(cgImage:orientation:)`
- Core Image `CIImage(image:options:)` with `kCIImageApplyOrientationProperty`

---

## UIImage.Orientation

`UIImage.Orientation` uses a **completely different numbering**. The case
names are similar to `CGImagePropertyOrientation` but the raw integer values
do not match.

| Case | Raw Value | EXIF Equivalent | CGImagePropertyOrientation |
|------|-----------|-----------------|---------------------------|
| `.up` | 0 | 1 | `.up` (1) |
| `.down` | 1 | 3 | `.down` (3) |
| `.left` | 2 | 8 | `.left` (8) |
| `.right` | 3 | 6 | `.right` (6) |
| `.upMirrored` | 4 | 2 | `.upMirrored` (2) |
| `.downMirrored` | 5 | 4 | `.downMirrored` (4) |
| `.leftMirrored` | 6 | 5 | `.leftMirrored` (5) |
| `.rightMirrored` | 7 | 7 | `.rightMirrored` (7) |

### Why UIImage Uses Different Values

`UIImage.Orientation` was defined in early iOS (iPhone OS 2.0) before
`CGImagePropertyOrientation` existed. Its numbering reflects the order in
which orientations were added to UIKit, prioritizing the four most common
cases (`.up`, `.down`, `.left`, `.right`) as values 0-3. The mirrored
variants (4-7) were added later.

`CGImagePropertyOrientation` was introduced in iOS 4.0 and deliberately
matches EXIF values for direct interoperability with image file metadata.
Apple chose not to change UIKit's existing enum to avoid breaking deployed
apps.

### The Specific Danger

The values that differ most dangerously:

| UIImage Case | UIImage Raw | EXIF Value | EXIF Meaning |
|-------------|------------|------------|--------------|
| `.down` | **1** | **3** | UIImage 1 means `.down` but EXIF 1 means Normal |
| `.left` | **2** | **8** | UIImage 2 means `.left` but EXIF 2 means Mirrored |
| `.right` | **3** | **6** | UIImage 3 means `.right` but EXIF 3 means 180 |
| `.upMirrored` | **4** | **2** | UIImage 4 means `.upMirrored` but EXIF 4 means FlipV |

If you use `uiImage.imageOrientation.rawValue` as an EXIF orientation value,
every non-normal orientation will be wrong.

---

## Complete Three-Way Mapping Table

| EXIF Value | CGImagePropertyOrientation | UIImage.Orientation | Transform | Dimensions Swap? |
|------------|--------------------------|--------------------|-----------|-----------------|
| 1 | `.up` (1) | `.up` (0) | None | No |
| 2 | `.upMirrored` (2) | `.upMirrored` (4) | Flip horizontal | No |
| 3 | `.down` (3) | `.down` (1) | Rotate 180 | No |
| 4 | `.downMirrored` (4) | `.downMirrored` (5) | Flip vertical | No |
| 5 | `.leftMirrored` (5) | `.leftMirrored` (6) | Transpose | **Yes** |
| 6 | `.right` (6) | `.right` (3) | Rotate 90 CW | **Yes** |
| 7 | `.rightMirrored` (7) | `.rightMirrored` (7) | Transverse | **Yes** |
| 8 | `.left` (8) | `.left` (2) | Rotate 90 CCW | **Yes** |

> For orientations 5-8, the displayed image dimensions are transposed: a
> 4032x3024 stored image displays as 3024x4032.

---

## Conversion Code (Swift)

### CGImagePropertyOrientation -> UIImage.Orientation

```swift
extension UIImage.Orientation {
    /// Convert from CGImagePropertyOrientation (EXIF values 1-8)
    /// to UIImage.Orientation (UIKit values 0-7).
    init(_ cgOrientation: CGImagePropertyOrientation) {
        switch cgOrientation {
        case .up:            self = .up
        case .upMirrored:    self = .upMirrored
        case .down:          self = .down
        case .downMirrored:  self = .downMirrored
        case .left:          self = .left
        case .leftMirrored:  self = .leftMirrored
        case .right:         self = .right
        case .rightMirrored: self = .rightMirrored
        }
    }
}
```

### UIImage.Orientation -> CGImagePropertyOrientation

```swift
extension CGImagePropertyOrientation {
    /// Convert from UIImage.Orientation (UIKit values 0-7)
    /// to CGImagePropertyOrientation (EXIF values 1-8).
    init(_ uiOrientation: UIImage.Orientation) {
        switch uiOrientation {
        case .up:            self = .up
        case .upMirrored:    self = .upMirrored
        case .down:          self = .down
        case .downMirrored:  self = .downMirrored
        case .left:          self = .left
        case .leftMirrored:  self = .leftMirrored
        case .right:         self = .right
        case .rightMirrored: self = .rightMirrored
        @unknown default:    self = .up
        }
    }
}
```

### EXIF Integer -> CGImagePropertyOrientation

```swift
extension CGImagePropertyOrientation {
    /// Create from EXIF orientation integer (1-8).
    /// Returns .up for out-of-range values.
    init(exifValue: UInt32) {
        self = CGImagePropertyOrientation(rawValue: exifValue) ?? .up
    }
}
```

### Reading Orientation from ImageIO

```swift
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]

// Top-level orientation (EXIF value 1-8, same as CGImagePropertyOrientation)
let exifOrientation = props?[kCGImagePropertyOrientation as String] as? UInt32 ?? 1
let cgOrientation = CGImagePropertyOrientation(rawValue: exifOrientation) ?? .up
let uiOrientation = UIImage.Orientation(cgOrientation)
```

### Writing Orientation via XMP

```swift
let mutable = CGImageMetadataCreateMutable()
// tiff:Orientation uses EXIF values (1-8)
CGImageMetadataSetValueWithPath(mutable, nil,
    "tiff:Orientation" as CFString,
    "\(cgOrientation.rawValue)" as CFString)
```

### Applying Orientation to a CGImage for Display

```swift
func applyOrientation(_ image: CGImage,
                       orientation: CGImagePropertyOrientation) -> CGImage? {
    let ciImage = CIImage(cgImage: image)
        .oriented(forExifOrientation: Int32(orientation.rawValue))
    let context = CIContext()
    return context.createCGImage(ciImage, from: ciImage.extent)
}
```

---

## Orientation Locations in Metadata

Orientation can appear in multiple places within the same file:

| Location | ImageIO Key | Notes |
|----------|-------------|-------|
| Top-level property | `kCGImagePropertyOrientation` | Convenience; derived from TIFF Orientation by ImageIO |
| TIFF IFD0 | `kCGImagePropertyTIFFDictionary` -> `Orientation` | Primary storage location in TIFF-based formats |
| XMP | `tiff:Orientation` | XMP mirror of TIFF tag |
| Exif IFD | Rare — some non-conformant tools write it here | Not standard; if present, ImageIO prefers TIFF IFD value |

### TIFF vs Exif IFD Orientation

The EXIF specification stores orientation in IFD0 (the TIFF IFD), not in the
Exif IFD. This is correct per the EXIF spec — orientation is a TIFF tag
(0x0112), not an EXIF-specific tag. However, some non-conformant tools write
an orientation tag in the Exif IFD as well.

When both TIFF IFD and Exif IFD contain orientation and they differ:
- **ImageIO** uses the TIFF IFD (IFD0) value
- **ExifTool** reads both but prefers IFD0

The top-level `kCGImagePropertyOrientation` returned by ImageIO is always
derived from the TIFF IFD orientation.

### HEIF/HEIC Orientation

HEIF stores orientation differently from JPEG/TIFF. The orientation is stored
as a `irot` (image rotation) and `imir` (image mirroring) box in the HEIF
container structure, not as a traditional TIFF/EXIF tag. However, ImageIO
abstracts this: the `kCGImagePropertyOrientation` key returns the equivalent
EXIF orientation value (1-8) regardless of the underlying format.

---

## Common Pitfalls

### 1. Using Raw UIImage.Orientation Values as EXIF Values

```swift
// BUG: UIImage.Orientation.right.rawValue is 3, but EXIF right is 6
let wrongExifValue = uiImage.imageOrientation.rawValue  // 3, not 6!

// CORRECT: Convert through CGImagePropertyOrientation
let cgOrientation = CGImagePropertyOrientation(uiImage.imageOrientation)
let correctExifValue = cgOrientation.rawValue  // 6
```

### 2. Forgetting to Apply Orientation When Displaying CGImage

`CGImage` does not carry orientation information. When you extract a
`CGImage` from a `CGImageSource`, you must apply the orientation transform
yourself or use `kCGImageSourceCreateThumbnailWithTransform: true`.

```swift
// Creates a correctly oriented thumbnail without manual rotation
let options: [CFString: Any] = [
    kCGImageSourceCreateThumbnailFromImageAlways: true,
    kCGImageSourceThumbnailMaxPixelSize: 200,
    kCGImageSourceCreateThumbnailWithTransform: true  // Apply orientation
]
let thumbnail = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary)
```

Without `kCGImageSourceCreateThumbnailWithTransform`, the thumbnail retains
the raw pixel orientation and may appear sideways or upside down.

### 3. Double-Rotation

`UIImageView` automatically applies `UIImage.imageOrientation` when
displaying. If you also manually rotate the image based on EXIF orientation,
the image will be rotated twice. Common scenario:

```swift
// BUG: Double rotation
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let orientation = /* read EXIF orientation */
let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil)!
let rotatedCGImage = applyOrientation(cgImage, orientation)  // Manual rotation
let uiImage = UIImage(cgImage: rotatedCGImage, scale: 1.0, orientation: orientation)
// UIImageView will rotate AGAIN based on the orientation property
```

**Fix:** Either apply orientation to pixels and set UIImage orientation to
`.up`, or pass raw pixels with the correct UIImage orientation and let UIKit
handle the transform.

### 4. Orientation Lost Through UIImage Round-Trip

`UIImage(data:)` reads the EXIF orientation and stores it in
`imageOrientation`. But `jpegData(compressionQuality:)` bakes the
orientation into the pixels and always writes EXIF orientation 1 (Normal).

```swift
// Before: EXIF orientation = 6 (90 CW), pixels are landscape
let image = UIImage(data: jpegData)!
print(image.imageOrientation)  // .right (UIKit value 3)

let newData = image.jpegData(compressionQuality: 0.8)!
// After: EXIF orientation = 1 (Normal), pixels are now portrait (rotated)
// The orientation was baked into the pixels
```

This is actually correct behavior for display purposes, but it means the
EXIF orientation tag no longer reflects the camera's physical orientation.
The tag will always be 1 after a UIImage round-trip.

### 5. Front Camera Mirroring

The front-facing camera on iPhone writes mirrored orientation values (2, 4,
5, 7) because the preview is displayed as a mirror image. Applications that
only handle orientations 1, 3, 6, 8 may display selfies incorrectly.

Starting in iOS 14, there is a user-accessible setting "Mirror Front Camera"
which, when enabled, writes unmirrored orientation values for front camera
photos. Apps should handle all 8 orientation values regardless.

### 6. Orientation Not Present

Some images have no orientation tag at all (e.g., images from web downloads,
screenshots, programmatically generated images). When absent, the correct
default is orientation 1 (Normal / `.up`).

```swift
let exifOrientation = props?[kCGImagePropertyOrientation as String] as? UInt32 ?? 1
// Default to 1 (Normal) when absent
```

---

## Affine Transforms for Each Orientation

For manual rotation/flip in Core Graphics. These transforms convert from
stored pixel coordinates to display coordinates:

```swift
func transform(for orientation: CGImagePropertyOrientation,
               imageSize: CGSize) -> CGAffineTransform {
    let w = imageSize.width
    let h = imageSize.height

    switch orientation {
    case .up:
        return .identity

    case .upMirrored:
        // Flip horizontal
        return CGAffineTransform(scaleX: -1, y: 1)
            .translatedBy(x: -w, y: 0)

    case .down:
        // Rotate 180
        return CGAffineTransform(translationX: w, y: h)
            .rotated(by: .pi)

    case .downMirrored:
        // Flip vertical
        return CGAffineTransform(scaleX: 1, y: -1)
            .translatedBy(x: 0, y: -h)

    case .leftMirrored:
        // Transpose: mirror + 90 CCW
        return CGAffineTransform(translationX: h, y: 0)
            .scaledBy(x: -1, y: 1)
            .rotated(by: -.pi / 2)

    case .right:
        // Rotate 90 CW (display requires 90 CCW)
        return CGAffineTransform(translationX: h, y: 0)
            .rotated(by: -.pi / 2)

    case .rightMirrored:
        // Transverse: mirror + 90 CW
        return CGAffineTransform(translationX: 0, y: w)
            .scaledBy(x: -1, y: 1)
            .rotated(by: .pi / 2)

    case .left:
        // Rotate 90 CCW (display requires 90 CW)
        return CGAffineTransform(translationX: 0, y: w)
            .rotated(by: .pi / 2)
    }
}
```

### Display Size Calculation

```swift
func displaySize(for orientation: CGImagePropertyOrientation,
                 storedSize: CGSize) -> CGSize {
    switch orientation {
    case .up, .upMirrored, .down, .downMirrored:
        return storedSize  // No dimension swap
    case .left, .leftMirrored, .right, .rightMirrored:
        return CGSize(width: storedSize.height, height: storedSize.width)  // Swap
    }
}
```

---

## Orientation Composition

When you apply a transform to an already-oriented image, you need to compose
orientations. This table shows the result of applying a 90 CW rotation to
each starting orientation:

| Starting | + 90 CW Rotation | Result |
|----------|-----------------|--------|
| 1 (Normal) | | 6 (90 CW) |
| 2 (Mirror H) | | 5 (Transpose) |
| 3 (180) | | 8 (90 CCW) |
| 4 (Mirror V) | | 7 (Transverse) |
| 5 (Transpose) | | 4 (Mirror V) |
| 6 (90 CW) | | 3 (180) |
| 7 (Transverse) | | 2 (Mirror H) |
| 8 (90 CCW) | | 1 (Normal) |

### Composition Function

```swift
func composeOrientation(
    base: CGImagePropertyOrientation,
    applying rotation: CGImagePropertyOrientation
) -> CGImagePropertyOrientation {
    // Represent each orientation as (rotation_count, is_mirrored)
    // where rotation_count is the number of 90 CW rotations (0-3)
    // and is_mirrored is whether a horizontal flip is applied before rotation
    //
    // 1=(0,F) 2=(0,T) 3=(2,F) 4=(2,T) 5=(1,T) 6=(1,F) 7=(3,T) 8=(3,F)

    let table: [(rot: Int, mir: Bool)] = [
        (0, false), // 1
        (0, true),  // 2
        (2, false), // 3
        (2, true),  // 4
        (1, true),  // 5
        (1, false), // 6
        (3, true),  // 7
        (3, false), // 8
    ]

    let b = table[Int(base.rawValue) - 1]
    let r = table[Int(rotation.rawValue) - 1]

    let newMir = b.mir != r.mir  // XOR for mirror
    let newRot: Int
    if r.mir {
        newRot = (b.rot + 4 - r.rot) % 4
    } else {
        newRot = (b.rot + r.rot) % 4
    }

    let resultTable: [[(Int, Bool)]] = [
        // Find the orientation matching (newRot, newMir)
    ]

    // Lookup result
    for i in 0..<8 {
        if table[i].rot == newRot && table[i].mir == newMir {
            return CGImagePropertyOrientation(rawValue: UInt32(i + 1))!
        }
    }
    return .up  // Should not reach here
}
```

---

## Cross-References

- [../imageio/pitfalls.md](../imageio/pitfalls.md) — Orientation confusion
  pitfall, UIImage metadata loss
- [../exif/orientation.md](../exif/orientation.md) — EXIF orientation
  specification details
- [overlapping-fields.md](overlapping-fields.md) — Orientation as overlapping
  field (TIFF IFD0, top-level, XMP)
- [pitfalls.md](pitfalls.md) — Orientation inconsistency across apps
