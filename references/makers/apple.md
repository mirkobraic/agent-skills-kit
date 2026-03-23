# Apple MakerNote

> Part of [Manufacturer MakerNote Dictionaries](README.md)

Apple's MakerNote contains metadata specific to iPhone, iPad, and iPod touch
cameras. It stores computational photography flags, device sensor data,
burst/Live Photo identifiers, image processing parameters, and scene
analysis results from the Neural Engine that have no standard EXIF
equivalent.

**ImageIO constant:** `kCGImagePropertyMakerAppleDictionary` (iOS 7.0+)

---

## Format

- **Header:** `"Apple iOS\0"` (10 bytes) followed by a 2-byte version
  (`0x00 0x01`) and `"MM"` byte order marker (big-endian)
- **Internal structure:** Standard TIFF IFD starting at offset 14
- **Special encoding:** Several tag values are binary property lists
  (bplist), a format native to Apple platforms. These contain structured
  data like CMTime dictionaries, AE analysis matrices, scene classification
  results, and Photographic Styles parameters.
- **Offset resilience:** Not a concern -- Apple MakerNote is always written
  fresh by the camera pipeline (never rewritten from an existing source)

```
Apple MakerNote layout:
  Offset 0:   "Apple iOS\0"  (10-byte signature, hex: 41 70 70 6C 65 20 69 4F 53 00)
  Offset 10:  0x00 0x01      (version)
  Offset 12:  "MM"           (byte order: big-endian)
  Offset 14:  [IFD entry count]
  Offset 16+: [IFD entries...]
```

---

## Complete Tag Reference

Tags extracted from Apple MakerNote, as decoded by ExifTool (Apple.pm)
and community reverse-engineering. **Apple does not officially document
these tags.** Tag names and meanings are derived from ExifTool's naming
conventions and internal Apple framework symbol names discovered through
reverse engineering.

### Core Tags

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0001 (1) | MakerNoteVersion | int32s | MakerNote format version (observed: 12-15, increasing with iOS versions) |
| 0x0002 (2) | AEMatrix | undef (bplist) | Auto-exposure matrix data; binary plist containing AE analysis grid. Large structure; full format not publicly decoded. |
| 0x0003 (3) | RunTime | undef (bplist) | Device uptime at capture; binary plist encoding a CMTime structure (time since last boot, excluding standby). See detail below. |
| 0x0004 (4) | AEStable | int32s | Auto-exposure stability flag. `0` = AE was not stable (converging), `1` = AE was stable (converged) |
| 0x0005 (5) | AETarget | int32s | Auto-exposure target luminance value |
| 0x0006 (6) | AEAverage | int32s | Auto-exposure average luminance of the metered scene |
| 0x0007 (7) | AFStable | int32s | Autofocus stability flag. `0` = AF was not stable, `1` = AF achieved stable focus |
| 0x0008 (8) | AccelerationVector | rational64s[3] | XYZ acceleration in units of g. Encodes device orientation at capture. See detail below. |

### HDR and Computational Photography

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x000a (10) | HDRImageType | int32s | `3` = HDR Image (merged from multiple exposures via Smart HDR / Deep Fusion / Photonic Engine), `4` = Original Image (non-HDR single frame) |
| 0x000e (14) | ImageCaptureRequestIdentifier | string | Unique identifier for the capture request |
| 0x0014 (20) | ImageCaptureType | int32s | Capture mode identifier (see table below) |
| 0x001f (31) | QRMOutputType | int32s | Quadra-resolution merge output type (computational pipeline stage identifier) |
| 0x0020 (32) | LuminanceNoiseAmplitude | rational64s | Measured luminance noise level in the captured image |
| 0x0021 (33) | HDRHeadroom | rational64s | HDR headroom value in stops; indicates available dynamic range above SDR white |
| 0x002b (43) | SignalToNoiseRatio | rational64s | Measured signal-to-noise ratio of the captured image |
| 0x002d (45) | ColorTemperature | int32s | Color temperature of the scene illuminant (Kelvin) |
| 0x0030 (48) | HDRGain | rational64s | HDR gain applied during computational merge |
| 0x0033 (51) | NRFStatus | int32s | Noise reduction filter status |

### ImageCaptureType Values (Tag 20)

| Value | Capture Mode |
|-------|-------------|
| 1 | ProRAW (Apple ProRAW / DNG) |
| 2 | Portrait mode |
| 10 | Standard photo |

### Burst Mode

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x000b (11) | BurstUUID | string | Unique identifier shared by all photos in a burst sequence. The Photos app uses this UUID to group burst images. Third-party apps can use it for burst import. |

### Live Photo and Media Grouping

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0011 (17) | ContentIdentifier | string | UUID that links a Live Photo's still image to its companion video (MOV). The same UUID appears in the video's QuickTime metadata as `com.apple.quicktime.content.identifier`. This is the fundamental mechanism that makes Live Photos work. |
| 0x0015 (21) | ImageUniqueID | string | Unique image identifier |
| 0x0025 (37) | PhotoIdentifier | string | Unique photo identifier (distinct from ImageUniqueID) |

### Focus and Stabilization

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x000c (12) | FocusDistanceRange | rational64s[2] | Near and far focus distance [near, far] in meters |
| 0x000f (15) | OISMode | int32s | Optical Image Stabilization mode. Indicates sensor-shift OIS state. |
| 0x0026 (38) | FocusPosition | int32u | Lens focus position (hardware-level actuator position) |
| 0x002f (47) | FocusPosition2 | int32s | Alternative sensor-level focus position value |
| 0x003d (61) | AFConfidence | int32s | Time-of-Flight-assisted autofocus estimator confidence level |

### Scene and Orientation

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x000d (13) | Unknown (13) | int32s | Undocumented |
| 0x0016 (22) | SceneClassification | undef (bplist) | Scene analysis results from the Neural Engine. Binary plist containing scene type probabilities. |
| 0x0017 (23) | StillImageCaptureFlags | int32s | Capture flag bits; only valid when ContentIdentifier (tag 17) exists |
| 0x0019 (25) | Unknown (25) | int32s | Undocumented |
| 0x001a (26) | Unknown (26) | int32s | Undocumented |

### Camera Hardware

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x002e (46) | CameraType | int32s | Which camera module was used (see table below) |
| 0x003f (63) | GreenGhostMitigationStatus | int32s | Status of green ghost lens flare mitigation |

### CameraType Values (Tag 46)

| Value | Camera |
|-------|--------|
| 0 | Back Wide Angle (main camera) |
| 1 | Back Normal (telephoto on dual-camera systems, or ultra-wide context) |
| 6 | Front-facing camera |

### Photographic Styles (iOS 16+)

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0040 (64) | SemanticStyle | undef (bplist) | Photographic Styles data. Binary plist with keys: `_1` = Tone, `_2` = Warmth, `_3` = Style preset |
| 0x0041 (65) | SemanticStyleRenderingVer | string | Rendering version for the Photographic Styles pipeline |
| 0x0042 (66) | SemanticStylePreset | int32s | Style preset applied (Standard, Vibrant, Rich Contrast, Warm, Cool) |

### SemanticStyle Preset Values (Tag 66 / extracted from Tag 64)

| Value | Photographic Style |
|-------|--------------------|
| 1 | Standard |
| 2 | Vibrant |
| 3 | Rich Contrast |
| 4 | Warm |
| 5 | Cool |

### Additional Tags (Newer iOS Versions)

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0027 (39) | Unknown (39) | -- | Undocumented |
| 0x0046 (70) | ToFBlindSpot | int32s | Time-of-Flight autofocus estimator contains blind spot indicator |
| 0x0048 (72) | LeaderFollowerAF | int32s | Leader-follower autofocus leader focus method |

> **Note:** Many Apple MakerNote tags remain undocumented or partially
> understood. Apple does not publish MakerNote specifications. New tags
> appear with each major iOS release as new camera features are added.
> Tag 2 (AEMatrix) and Tag 22 (SceneClassification) contain large bplist
> structures whose full schemas are not publicly decoded.

---

## Key Tags in Detail

### RunTime (Tag 3) -- CMTime Structure

The RunTime tag encodes a `CMTime` value as a binary property list. This
represents the elapsed time since the device was last booted, **excluding
time spent in standby/sleep mode** but including time on wall power.

The bplist decodes to a dictionary with keys matching Apple's `CMTime`
struct fields:

```json
{
  "epoch": 0,
  "flags": 1,
  "timescale": 1000000000,
  "value": 123456789012345
}
```

**Elapsed time in seconds** = `value / timescale`

In the example above: `123456789012345 / 1000000000` = ~123,456.8 seconds
(~34.3 hours since boot).

**Use cases:**
- **Photo sequencing:** Compare RunTime values to determine the exact
  time interval between two photos (more precise than EXIF DateTimeOriginal
  which has only 1-second resolution)
- **Burst analysis:** Photos in a burst will have RunTime values
  milliseconds apart
- **Device uptime forensics:** Can indicate how long a device has been
  active

### AccelerationVector (Tag 8) -- Device Orientation

Three signed rational values representing the acceleration vector (gravity
direction) at the moment of capture, measured in units of g (~9.81 m/s^2).

**Coordinate system** (as viewed from the **front** of the device):
- **+X** = toward the left edge
- **+Y** = toward the bottom edge
- **+Z** = into the screen (toward the user)

| Device Position | X | Y | Z |
|----------------|---|---|---|
| Portrait, home button down | ~0 | ~-1.0 | ~0 |
| Portrait, home button up (inverted) | ~0 | ~+1.0 | ~0 |
| Landscape, home button right | ~-1.0 | ~0 | ~0 |
| Landscape, home button left | ~+1.0 | ~0 | ~0 |
| Face up on table | ~0 | ~0 | ~-1.0 |
| Face down on table | ~0 | ~0 | ~+1.0 |

This is **significantly more precise** than EXIF Orientation (quantized to
8 discrete values) and can be used for:
- Fine rotation correction (sub-degree accuracy)
- Determining if the device was tilted during capture
- Detecting if the device was in motion (acceleration magnitude != 1.0g)

### BurstUUID (Tag 11) -- Burst Grouping

All photos captured in a single burst share the same BurstUUID string.
The Photos app and third-party applications use this UUID to:
- Group burst images into a single visual stack
- Identify the "key photo" within a burst (selected by computational
  analysis or user choice)
- Enable "Select best" functionality

This is **distinct from** `PHAsset.burstIdentifier`, which is a Photos
framework database identifier. The MakerNote BurstUUID is the raw
EXIF-level identifier embedded in the image file itself. When importing
burst photos from non-iPhone sources, copying this MakerNote tag is what
causes the Photos app to group them correctly.

### ContentIdentifier (Tag 17) -- Live Photo Linking

The ContentIdentifier UUID is the fundamental mechanism that makes Live
Photos work. It links two separate files:

1. **Still image** (HEIC or JPEG) -- UUID in MakerNote tag 17
2. **Video file** (MOV) -- same UUID in QuickTime metadata as
   `com.apple.quicktime.content.identifier`

When both files are present with matching UUIDs, the system treats them as
a single Live Photo. If either file is missing or the UUIDs don't match,
the Live Photo association is broken and only the still image is displayed.

```swift
// Reading ContentIdentifier from a still image
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]
let apple = props?[kCGImagePropertyMakerAppleDictionary as String] as? [String: Any]
let contentID = apple?["17"] as? String  // e.g., "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
```

### HDRImageType (Tag 10) -- HDR Processing Flag

Indicates whether the image is the result of HDR processing:

| Value | Meaning |
|-------|---------|
| 3 | HDR Image -- merged from multiple exposures (Smart HDR, Deep Fusion, Photonic Engine) |
| 4 | Original Image -- single exposure, no HDR merge applied |

This tag does **not** distinguish between Smart HDR generations (Smart
HDR 1/2/3/4) or between Smart HDR and Deep Fusion. It only indicates
whether multi-frame merging occurred. The specific computational pipeline
(Smart HDR vs Deep Fusion vs Photonic Engine) is selected automatically
by the ISP and Neural Engine based on scene analysis and is not explicitly
tagged in the MakerNote.

### ImageCaptureType (Tag 20) -- Capture Mode

Identifies the primary capture mode used:

| Value | Meaning | Notes |
|-------|---------|-------|
| 1 | ProRAW | Apple ProRAW DNG output |
| 2 | Portrait mode | Depth-enabled capture with bokeh simulation |
| 10 | Standard photo | Normal photo capture (including HDR variants) |

### HDRHeadroom (Tag 33) -- Dynamic Range

The HDRHeadroom tag (added in iOS 16+ era) indicates the available dynamic
range above SDR white, measured in stops. This relates to the HDR gain map
system (`kCGImageAuxiliaryDataTypeHDRGainMap`) and enables adaptive display
on HDR-capable screens.

### SemanticStyle (Tag 64) -- Photographic Styles

Introduced with iPhone 13 (iOS 15) and expanded in iPhone 14 (iOS 16),
Photographic Styles let users customize the tone mapping and color
rendering of the computational photography pipeline. The SemanticStyle
tag stores the applied style as a binary plist with parameters:

- **Tone** (`_1`): Tone mapping adjustment value
- **Warmth** (`_2`): Color temperature bias value
- **Preset** (`_3`): Style preset identifier (Standard, Vibrant, Rich
  Contrast, Warm, Cool)

These parameters are applied during the computational photography merge
pipeline, not as a post-processing filter. The style affects skin tones
differently from backgrounds thanks to semantic segmentation.

---

## Computational Photography Context

Apple MakerNote tags are tightly coupled to the iPhone's computational
photography pipeline. The tags record the output of various pipeline
stages but do not expose the full internal processing chain.

### Smart HDR / Deep Fusion / Photonic Engine

The HDRImageType (tag 10) flag indicates HDR processing occurred, but the
specific pipeline is not explicitly tagged:

| Pipeline | When Used | Introduced |
|----------|-----------|------------|
| Smart HDR | Well-lit scenes, fast motion | iPhone XS (2018) |
| Deep Fusion | Medium to low light, rich texture | iPhone 11 (2019) |
| Night Mode | Very low light, long exposure | iPhone 11 (2019) |
| Photonic Engine | All conditions (enhanced Deep Fusion) | iPhone 14 (2022) |

All these pipelines merge multiple frames captured in rapid succession.
The MakerNote records the *result* but not which pipeline was selected.

### Apple ProRAW

ProRAW images (ImageCaptureType = 1) are DNG 1.6 files that embed
computational photography results:
- **Profile Gain Table Map** -- tone mapping data for editors
- **Semantic Segmentation Masks** -- skin, sky, etc. (stored as auxiliary
  data, not in MakerNote)
- **Linear DNG** with Apple-specific extensions

The computational data is in DNG tags and auxiliary data, not MakerNote.

### Auxiliary Data (Separate API)

The following computational photography outputs are stored as **auxiliary
image data**, accessed through `CGImageSourceCopyAuxiliaryDataInfoAtIndex`,
NOT through the MakerNote dictionary:

| Data | API Constant | iOS |
|------|-------------|-----|
| Depth map | `kCGImageAuxiliaryDataTypeDepth` | 11.0+ |
| Disparity map | `kCGImageAuxiliaryDataTypeDisparity` | 11.0+ |
| Portrait matte | `kCGImageAuxiliaryDataTypePortraitEffectsMatte` | 12.0+ |
| Skin/hair/teeth/glasses mattes | `kCGImageAuxiliaryDataTypeSemanticSegmentation*Matte` | 13.0+ |
| HDR gain map | `kCGImageAuxiliaryDataTypeHDRGainMap` | 14.1+ |
| Spatial photos | `kCGImagePropertyGroups` (top-level) | 18.0+ |

---

## Reading Apple MakerNote in Swift

### Basic Access

```swift
import ImageIO

func readAppleMakerNote(from url: URL) -> [String: Any]? {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else {
        return nil
    }

    guard let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
            as? [String: Any] else {
        return nil
    }

    return properties[kCGImagePropertyMakerAppleDictionary as String]
            as? [String: Any]
}
```

### Extracting Specific Values

```swift
func extractAppleMetadata(from url: URL) {
    guard let makerNote = readAppleMakerNote(from: url) else { return }

    // Burst UUID (tag 11)
    if let burstUUID = makerNote["11"] as? String {
        print("Burst UUID: \(burstUUID)")
    }

    // Content Identifier for Live Photo (tag 17)
    if let contentID = makerNote["17"] as? String {
        print("Live Photo Content ID: \(contentID)")
    }

    // HDR Image Type (tag 10)
    if let hdrType = makerNote["10"] as? Int {
        switch hdrType {
        case 3: print("HDR merged image")
        case 4: print("Original (non-HDR) image")
        default: print("HDR type: \(hdrType)")
        }
    }

    // Acceleration Vector (tag 8) -- device orientation
    if let accel = makerNote["8"] as? [Double], accel.count == 3 {
        print("Acceleration: X=\(accel[0]), Y=\(accel[1]), Z=\(accel[2])")
    }

    // Focus Distance Range (tag 12) -- near/far in meters
    if let focusDist = makerNote["12"] as? [Double], focusDist.count == 2 {
        print("Focus range: \(focusDist[0])m - \(focusDist[1])m")
    }

    // Image Capture Type (tag 20)
    if let captureType = makerNote["20"] as? Int {
        switch captureType {
        case 1:  print("ProRAW capture")
        case 2:  print("Portrait mode")
        case 10: print("Standard photo")
        default: print("Capture type: \(captureType)")
        }
    }

    // Camera Type (tag 46) -- which lens module
    if let cameraType = makerNote["46"] as? Int {
        switch cameraType {
        case 0: print("Back wide angle (main)")
        case 1: print("Back telephoto / normal")
        case 6: print("Front-facing camera")
        default: print("Camera type: \(cameraType)")
        }
    }

    // AE and AF stability
    if let aeStable = makerNote["4"] as? Int {
        print("AE stable: \(aeStable == 1 ? "Yes" : "No")")
    }
    if let afStable = makerNote["7"] as? Int {
        print("AF stable: \(afStable == 1 ? "Yes" : "No")")
    }

    // Color Temperature (tag 45)
    if let colorTemp = makerNote["45"] as? Int {
        print("Color temperature: \(colorTemp) K")
    }

    // HDR Headroom (tag 33)
    if let headroom = makerNote["33"] as? Double {
        print("HDR headroom: \(headroom) stops")
    }

    // Signal-to-Noise Ratio (tag 43)
    if let snr = makerNote["43"] as? Double {
        print("SNR: \(snr)")
    }
}
```

### Writing / Preserving Apple MakerNote

Apple MakerNote data can be preserved when creating images:

```swift
func preserveAppleMakerNote(from sourceURL: URL, to destURL: URL) {
    guard let source = CGImageSourceCreateWithURL(sourceURL as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
          let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
                as? [String: Any] else { return }

    guard let dest = CGImageDestinationCreateWithURL(
            destURL as CFURL,
            UTType.heic.identifier as CFString,
            1, nil) else { return }

    // Pass the full properties dictionary (includes MakerApple)
    CGImageDestinationAddImage(dest, image, properties as CFDictionary)
    CGImageDestinationFinalize(dest)
}
```

For truly lossless metadata preservation (JPEG only), use
`CGImageDestinationCopyImageSource` instead, which copies raw bytes
without re-encoding.

---

## Privacy Considerations

Apple MakerNote contains several data points with privacy implications:

| Tag | Privacy Concern |
|-----|----------------|
| **AccelerationVector** (8) | Reveals device orientation; can indicate whether user was standing, lying down, or in a vehicle |
| **RunTime** (3) | Reveals device uptime since last reboot; can correlate events across photos and establish device usage patterns |
| **ContentIdentifier** (17) | Links still images to video files; reveals Live Photo associations |
| **BurstUUID** (11) | Reveals which photos were taken together in rapid succession |
| **CameraType** (46) | Reveals whether photo was taken with front or back camera (selfie detection) |
| **FocusDistanceRange** (12) | Reveals approximate distance to subject |
| **SceneClassification** (22) | Contains Neural Engine scene analysis (scene type probabilities) |
| **HDRImageType** (10) | Reveals computational processing applied |

**GPS stripping tools do NOT remove Apple MakerNote data.** For complete
metadata sanitization, the entire MakerNote must be stripped. The safest
approach is to recreate the image from decoded pixels with no metadata copy.

---

## Cross-References

- [MakerNote Concept](makernote-concept.md) -- How MakerNote works, offset fragility
- [ImageIO Auxiliary Data](../imageio/auxiliary-data.md) -- Depth maps, gain maps, segmentation mattes
- [ImageIO Property Keys](../imageio/property-keys.md) -- `kCGImagePropertyMakerAppleDictionary`
- [EXIF MakerNote](../exif/makernote.md) -- MakerNote in the EXIF standard

### External References

- [ExifTool Apple Tags](https://exiftool.org/TagNames/Apple.html) -- Comprehensive tag reference
- [ExifTool Apple.pm source](https://github.com/exiftool/exiftool/blob/master/lib/Image/ExifTool/Apple.pm) -- Tag definitions and bplist parsing
- [APPLE MakerNote decoding forum thread](https://exiftool.org/forum/index.php?topic=14975.0) -- Community reverse-engineering
- [metadata-extractor Apple bplist PR](https://github.com/drewnoakes/metadata-extractor/pull/395) -- Java/C# bplist parsing implementation
