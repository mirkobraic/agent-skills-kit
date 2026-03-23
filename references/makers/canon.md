# Canon MakerNote

> Part of [Manufacturer MakerNote Dictionaries](README.md)

Canon MakerNote is one of the most extensively documented vendor MakerNote
formats. It stores detailed camera settings, lens identification, autofocus
data, and diagnostic information in a structured IFD hierarchy with dozens
of sub-structures.

**ImageIO constant:** `kCGImagePropertyMakerCanonDictionary` (iOS 4.0+)

---

## Format

- **Header:** None. The IFD starts immediately at the first byte of the
  MakerNote data -- no signature or magic bytes.
- **Byte order:** Same as the main TIFF header
- **Internal structure:** Standard TIFF IFD with absolute offsets (from
  the TIFF header start)
- **Offset type:** Absolute -- **most fragile** of all vendor formats
- **Format detection:** Since there is no header signature, the decoder
  must rely on the camera Make being "Canon" in the TIFF IFD

Canon's MakerNote is the most extensively documented by ExifTool
(~5,000 lines in `Canon.pm`). The MakerNote uses several distinct data
patterns:
- **Simple tags:** Single values (strings, integers)
- **Array tags:** Indexed arrays where each position has a defined meaning
  (CameraSettings, ShotInfo, FocusInfo, ProcessingInfo)
- **Sub-structures:** Complex binary structures with model-dependent
  layouts (CameraInfo, ColorData)

---

## Top-Level Tag Reference

The Canon MakerNote IFD contains entries that point to both simple values
and complex sub-structures. Tags listed with `int16s[]` or `int16u[]`
types are arrays where specific indices carry defined meanings.

### Identification and Information

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0006 (6) | ImageType | string | Camera model string (e.g., `"Canon EOS R5"`, `"Canon EOS 5D Mark IV"`) |
| 0x0007 (7) | FirmwareVersion | string | Firmware version (e.g., `"Firmware Version 1.8.1"`) |
| 0x0008 (8) | FileNumber | int32u | Sequential file counter (wraps at 9999 per folder) |
| 0x0009 (9) | OwnerName | string | Owner name (set in camera menu) |
| 0x000c (12) | SerialNumber | int32u | Camera body serial number (numeric) |
| 0x000e (14) | FileLength | int32u | File size in bytes |
| 0x0010 (16) | CanonModelID | int32u | Numeric model identifier (see table below) |
| 0x0015 (21) | SerialNumberFormat | int32u | Serial number format identifier |
| 0x0096 (150) | InternalSerialNumber | string | Internal alphanumeric serial (e.g., `"AB1234567890"`) |

### Camera Settings and Shot Data

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0001 (1) | CameraSettings | int16s[] | Camera settings array (see detailed section below) |
| 0x0002 (2) | FocalLength | int16u[] | Focal length info: [FocalType, FocalLength, FocalPlaneXSize, FocalPlaneYSize] |
| 0x0003 (3) | FlashInfo | int16u[] | Flash-related parameters |
| 0x0004 (4) | ShotInfo | int16s[] | Shot information array (see detailed section below) |
| 0x0005 (5) | Panorama | int16s[] | Panorama stitching info |

### Image Processing

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x000d (13) | CameraInfo | undef | Camera info sub-structure (model-dependent binary format, contains shutter count on some models) |
| 0x000f (15) | CustomFunctions | int16u[] | Custom function settings (model-dependent) |
| 0x001c (28) | DateStampMode | int16u | Date stamp mode |
| 0x001d (29) | MyColors | int16u[] | My Colors mode settings |
| 0x001e (30) | FirmwareRevision | int32u | Firmware revision number |
| 0x0023 (35) | Categories | int32u[2] | Image categories (bit flags) |
| 0x0093 (147) | CanonFileInfo | int16s[] | File info: file number, bracket mode, bracket value |
| 0x009a (154) | AspectInfo | int32u[] | Aspect ratio info |

### Lens

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0095 (149) | LensModel | string | Lens model name (e.g., `"EF24-70mm f/2.8L II USM"`, `"RF24-105mm F4 L IS USM"`) |
| 0x0097 (151) | DustRemovalData | undef | Dust delete data for in-camera dust removal |
| 0x4019 (16409) | LensInfo | int16u[] | Detailed lens info array (focal lengths, aperture range) |

### Autofocus

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0012 (18) | AFInfo | int16u[] | Autofocus information (older EOS models) |
| 0x0013 (19) | ThumbnailImageValidArea | int16u[4] | Valid area of embedded thumbnail |
| 0x0024 (36) | FaceDetect1 | int16u[] | Face detection data (first set) |
| 0x0025 (37) | FaceDetect2 | int16u[] | Face detection data (second set) |
| 0x0026 (38) | AFInfo2 | int16u[] | Modern AF information (see section below) |
| 0x0028 (40) | ImageUniqueID | undef[16] | Unique image identifier (binary) |
| 0x4013 (16403) | AFMicroAdj | int32s[] | AF Micro Adjustment values |
| 0x4028 (16424) | AFConfig | int16s[] | AF configuration / AF Tab info |

### White Balance and Color

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x002f (47) | WBInfo | int32u[] | White balance info |
| 0x00a0 (160) | ProcessingInfo | int16s[] | Image processing parameters |
| 0x00a1 (161) | ToneCurveTable | int16u[] | Tone curve table |
| 0x00a2 (162) | SharpnessTable | int16u[] | Sharpness table |
| 0x00a3 (163) | SharpnessFreqTable | int16u[] | Sharpness frequency table |
| 0x00a4 (164) | WhiteBalanceTable | int16u[] | White balance table |
| 0x00a9 (169) | ColorBalance | int16s[] | Color balance data |
| 0x00aa (170) | MeasuredColor | int16u[] | Measured color info |
| 0x00ae (174) | ColorTemperature | int16u | Color temperature (Kelvin) |
| 0x00b0 (176) | CanonFlags | int16u[] | Canon internal flags |
| 0x00b4 (180) | ColorInfo | int16s[] | Color information |
| 0x4001 (16385) | ColorData | int16s[] | Color data (model-dependent; contains WB calibration, color matrices) |
| 0x4003 (16387) | ColorInfo2 | int16s[] | Additional color info |

### Picture Style and Effects

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0099 (153) | CustomFunctions2 | int16u[] | Custom functions (newer EOS models) |
| 0x4005 (16389) | Flavor | int16u[] | Picture style / flavor |
| 0x4008 (16392) | PictureStyleUserDef | int16u[] | User-defined picture styles |
| 0x4009 (16393) | PictureStylePC | int16u[] | Picture style (PC) |
| 0x4010 (16400) | CustomPictureStyleFileName | string | Custom picture style filename |

### Lens Correction and Processing

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x4015 (16405) | VignettingCorr | int16s[] | Vignetting correction data |
| 0x4016 (16406) | VignettingCorr2 | int16s[] | Vignetting correction part 2 |
| 0x4018 (16408) | LightingOpt | int16s[] | Lighting optimizer settings |
| 0x4020 (16416) | AmbienceInfo | int16s[] | Ambience selection info |
| 0x4024 (16420) | FilterInfo | int16s[] | Creative filter info |
| 0x4025 (16421) | HDRInfo | int16s[] | HDR shooting info |

### Other

| Tag ID | Name | Type | Description |
|--------|------|------|-------------|
| 0x0035 (53) | TimeInfo | int32s[] | Time zone and daylight saving info |
| 0x0038 (56) | BatteryType | undef | Battery type information |
| 0x00d0 (208) | VRDOffset | int32u | Offset to VRD (Variable Range Data) recipe |
| 0x00e0 (224) | SensorInfo | int16u[] | Sensor dimensions and active area crop info |
| 0x4002 (16386) | CRWParam | undef | CRW (Canon RAW) format parameters |

---

## CameraSettings Array (Tag 0x0001)

The CameraSettings tag is a **signed 16-bit integer array** where each
index position encodes a specific camera setting. This is Canon's most
important metadata structure, providing detailed information about camera
configuration at the time of capture.

**Array indexing starts at 1** (index 0 is unused/reserved).

| Index | Name | Notable Values |
|-------|------|---------------|
| 1 | MacroMode | `1` = Macro, `2` = Normal |
| 2 | SelfTimer | Self-timer delay in 1/10 sec; `0` = off |
| 3 | Quality | `1` = Economy, `2` = Normal, `3` = Fine, `4` = RAW, `5` = Superfine, `130` = Normal Movie, `131` = Movie |
| 4 | CanonFlashMode | `0` = Off, `1` = Auto, `2` = On, `3` = Red-eye reduction, `4` = Slow sync, `5` = Auto + red-eye, `6` = On + red-eye, `16` = External |
| 5 | ContinuousDrive | `0` = Single, `1` = Continuous, `2` = Movie, `3` = Continuous Speed Priority, `4` = Continuous Low, `5` = Continuous High, `6` = Silent Single, `9` = Single + Timer, `10` = Continuous + Timer |
| 7 | FocusMode | `0` = One-Shot AF, `1` = AI Servo AF, `2` = AI Focus AF, `3` = Manual Focus, `4` = Single, `5` = Continuous, `6` = Manual Focus (alt), `16` = Pan Focus, `256` = AF + MF, `512` = Movie Snap Focus, `519` = Movie Servo AF |
| 9 | RecordMode | `1` = JPEG, `2` = CRW+THM, `3` = AVI+THM, `4` = TIF, `5` = TIF+JPEG, `6` = CR2, `7` = CR2+JPEG, `9` = MOV, `10` = MP4, `11` = CRM, `12` = CR3, `13` = CR3+JPEG, `14` = HIF, `15` = CR3+HIF |
| 10 | ImageSize | `0` = Large, `1` = Medium, `2` = Small, `5` = Medium 1, `6` = Medium 2, `7` = Medium 3, `8` = Postcard, `9` = Widescreen, `14` = Small 1, `15` = Small 2, `16` = Small 3 |
| 11 | EasyMode | `0` = Full Auto, `1` = Manual, `2` = Landscape, `3` = Fast Shutter, `4` = Slow Shutter, `5` = Night, `6` = Gray Scale, `7` = Sepia, `8` = Portrait, `9` = Sports, `10` = Macro, `11` = Black & White, ... (50+ scene mode values) |
| 12 | DigitalZoom | `0` = None, `1` = 2x, `2` = 4x, `3` = Other |
| 13 | Contrast | `-1` = Low, `0` = Normal, `1` = High |
| 14 | Saturation | `-1` = Low, `0` = Normal, `1` = High |
| 15 | Sharpness | `-1` = Low, `0` = Normal, `1` = High |
| 16 | CameraISO | Auto ISO value (`0` = not set; otherwise the effective ISO speed) |
| 17 | MeteringMode | `0` = Default, `1` = Spot, `2` = Average, `3` = Evaluative, `4` = Partial, `5` = Center-weighted average |
| 18 | FocusRange | `0` = Manual, `1` = Auto, `2` = Not Known, `3` = Macro, `4` = Very Close, `5` = Close, `6` = Middle Range, `7` = Far Range, `8` = Pan Focus, `9` = Super Macro, `10` = Infinity |
| 19 | AFPoint | `0x2005` = Manual AF point, `0x3000` = None (MF), `0x3001` = Auto, `0x3002` = Right, `0x3003` = Center, `0x3004` = Left, `0x4001` = Auto AF point |
| 20 | ExposureMode | `0` = Easy, `1` = Program AE, `2` = Shutter speed priority (Tv), `3` = Aperture priority (Av), `4` = Manual, `5` = Depth-of-field AE (A-DEP), `6` = M-Dep, `7` = Bulb, `8` = Flexible-priority AE (Fv) |
| 22 | LensType | Canon lens type index (numeric ID; maps to lens name via ExifTool lookup table) |
| 23 | MaxFocalLength | Maximum focal length in focal units |
| 24 | MinFocalLength | Minimum focal length in focal units |
| 25 | FocalUnits | Focal length units per mm (typically `1`; focal length = value / FocalUnits) |
| 26 | MaxAperture | Maximum aperture (encoded; aperture = 2^(value/64)) |
| 27 | MinAperture | Minimum aperture (encoded) |
| 28 | FlashActivity | `0` = Did not fire, `1` = Fired |
| 29 | FlashBits | Bitfield: b0=Internal flash, b1=External E-TTL, b2=External A-TTL, b3=External flash fired, etc. |
| 32 | FocusContinuous | `0` = Single, `1` = Continuous, `8` = Manual |
| 33 | AESetting | `0` = Normal AE, `1` = Exposure compensation, `2` = AE lock, `3` = AE lock + exposure comp, `4` = No AE |
| 34 | ImageStabilization | `0` = Off, `1` = On, `2` = Shoot Only, `3` = Panning, `4` = Dynamic, `256` = Off (2), `257` = On (2), `258` = Shoot Only (2), `259` = Panning (2), `260` = Dynamic (2) |
| 36 | SpotMeteringMode | `0` = Center, `1` = AF Point |
| 39 | ManualFlashOutput | Manual flash output level |
| 41 | ColorTone | Color tone adjustment value |

---

## ShotInfo Array (Tag 0x0004)

Shot-specific exposure data captured at the moment of shutter release.
Values encoded in APEX (Additive System of Photographic Exposure) where
noted.

| Index | Name | Description |
|-------|------|-------------|
| 1 | AutoISO | Auto ISO speed value (log2 scale) |
| 2 | BaseISO | Base ISO (before auto adjustment); actual ISO = BaseISO * 2^(AutoISO/100) |
| 3 | MeasuredEV | Measured exposure value |
| 4 | TargetAperture | Target aperture value (APEX encoding) |
| 5 | TargetExposureTime | Target exposure time (APEX encoding) |
| 6 | ExposureCompensation | Exposure compensation (APEX) |
| 7 | WhiteBalance | `0` = Auto, `1` = Daylight, `2` = Cloudy, `3` = Tungsten, `4` = Fluorescent, `5` = Flash, `6` = Custom, `8` = Shade, `9` = Kelvin |
| 8 | SlowShutter | `0` = Off, `1` = Night Scene, `2` = On, `3` = None |
| 9 | SequenceNumber | Shot sequence number within burst |
| 13 | FlashGuideNumber | Flash guide number |
| 14 | AFPointsInFocus | Bitmask of AF points that achieved focus |
| 15 | FlashExposureComp | Flash exposure compensation (APEX) |
| 16 | AutoExposureBracketing | AEB step value |
| 19 | ApertureValue | Actual aperture value (APEX) |
| 20 | ShutterSpeedValue | Actual shutter speed (APEX) |
| 21 | MeasuredEV2 | Measured EV (second reading) |
| 24 | SelfTimer2 | Self-timer countdown (1/10 sec) |
| 29 | FlashOutput | Flash output level |

---

## Lens Identification

Canon stores lens data in multiple locations, providing redundancy:

| Source | Tag/Index | Content | Reliability |
|--------|-----------|---------|-------------|
| CameraSettings[22] | LensType | Numeric lens type ID | Requires lookup table; changes with new lenses |
| CameraSettings[23-25] | MaxFocal / MinFocal / FocalUnits | Focal length range | Reliable for zoom range identification |
| CameraSettings[26-27] | MaxAperture / MinAperture | Aperture range (encoded) | Reliable |
| Tag 0x0095 | LensModel | Lens name string | **Most reliable** -- human-readable name |
| Tag 0x4019 | LensInfo | Detailed lens info array | Full lens specification |

The **LensModel** string (tag 0x0095) is the most reliable lens
identifier because it contains the full marketing name. The LensType
numeric ID requires a lookup table maintained by ExifTool that must be
updated as new lenses are released. Canon RF-mount lenses and EF-mount
adapted lenses both appear here.

### Common Lens Name Prefixes

| Prefix | Meaning |
|--------|---------|
| EF | Canon EF mount (full-frame DSLR) |
| EF-S | Canon EF-S mount (APS-C DSLR) |
| EF-M | Canon EF-M mount (mirrorless, discontinued) |
| RF | Canon RF mount (full-frame mirrorless) |
| RF-S | Canon RF-S mount (APS-C mirrorless) |
| TS-E | Tilt-shift lens |
| MP-E | Macro photo lens |

---

## Camera Identification

| Tag | Content | Example |
|-----|---------|---------|
| 0x0006 (ImageType) | Camera model string | `"Canon EOS R5"` |
| 0x0007 (FirmwareVersion) | Firmware version | `"Firmware Version 1.8.1"` |
| 0x000c (SerialNumber) | Body serial number (numeric) | `123456789` |
| 0x0010 (CanonModelID) | Numeric model ID | `0x80000424` (EOS R5) |
| 0x0096 (InternalSerialNumber) | Internal serial (alphanumeric) | `"AB1234567890"` |

### Selected CanonModelID Values

| Model ID | Camera | Mount |
|----------|--------|-------|
| 0x80000424 | EOS R5 | RF |
| 0x80000520 | EOS R5 Mark II | RF |
| 0x80000453 | EOS R6 | RF |
| 0x80000487 | EOS R3 | RF |
| 0x80000498 | EOS R7 | RF |
| 0x80000464 | EOS R10 | RF |
| 0x80000480 | EOS R8 | RF |
| 0x80000421 | EOS R | RF |
| 0x80000428 | EOS RP | RF |
| 0x80000350 | EOS 5D Mark IV | EF |
| 0x80000349 | EOS 5DS | EF |
| 0x80000382 | EOS 80D | EF |
| 0x80000404 | EOS 90D | EF |
| 0x80000250 | EOS 7D | EF |
| 0x80000289 | EOS 7D Mark II | EF |
| 0x80000269 | EOS-1D X | EF |
| 0x80000328 | EOS-1D X Mark II | EF |
| 0x80000436 | EOS-1D X Mark III | EF |
| 0x80000281 | EOS M | EF-M |
| 0x80000355 | EOS M50 | EF-M |
| 0x03970000 | PowerShot G7 X Mark III | -- |

> The complete list contains 200+ entries. ExifTool's `Canon.pm` maintains
> the authoritative `%canonModelID` lookup table. IDs starting with
> `0x80000xxx` are EOS/RF cameras; IDs starting with `0x0xxx0000` are
> PowerShot/IXUS cameras.

---

## Autofocus Information

### AFInfo (Tag 0x0012) -- Older Format

Used by older EOS DSLRs (pre-2012). Contains the number of AF points,
valid AF point positions, and which points achieved focus. Format varies
by camera model.

### AFInfo2 (Tag 0x0026) -- Modern Format

Used by newer EOS DSLRs and all mirrorless bodies (including EOS R series).
Provides detailed AF data:

| Offset | Name | Description |
|--------|------|-------------|
| 0 | AFInfoSize | Size of AF info block in bytes |
| 1 | AFAreaMode | AF area selection mode (see table below) |
| 2 | NumAFPoints | Total number of AF points available |
| 3 | ValidAFPoints | Number of valid AF points in current mode |
| 4 | CanonImageWidth | Image width for AF coordinate mapping |
| 5 | CanonImageHeight | Image height for AF coordinate mapping |

### AFAreaMode Values

| Value | Mode |
|-------|------|
| 0 | Off (Manual Focus) |
| 1 | AF Point Expansion (left-right) |
| 2 | AF Point Expansion (all directions) |
| 3 | Zone AF |
| 4 | Single Point AF |
| 5 | Spot AF |
| 6 | AF Point Expansion (4-way) |
| 7 | Flexizone Multi |
| 8 | All AF Points |
| 9 | Flexizone Single |
| 10 | Large Zone AF |
| 11 | Large Zone AF (Vertical) |
| 12 | Large Zone AF (Horizontal) |
| 13 | Whole Area AF |
| 14 | Face+Tracking |

### Face Detection (Tags 0x0024, 0x0025)

Modern Canon cameras include face detection data with face positions
(center coordinates + width/height) in the image frame. The data is
stored as arrays of face rectangles.

---

## Shutter Count and Diagnostics

Canon does **not** store a straightforward "ShutterCount" tag like Nikon.
The shutter actuation count can be derived from model-dependent sources:

| Source | Availability | Notes |
|--------|-------------|-------|
| **FileNumber** (tag 0x0008) | All models | Sequential counter; wraps at 9999 per folder. Not total actuations. |
| **InternalSerialNumber** (tag 0x0096) | Some models | Encodes shutter count in specific character positions on some models |
| **CameraInfo** (tag 0x000d) | Many EOS models | Model-specific binary structure; contains shutter count at known byte offsets that vary by model and firmware |

ExifTool can extract `ShutterCount` from the CameraInfo structure for many
EOS models (including R5, R6, 5D Mark IV, etc.), but the byte offset within
CameraInfo varies by camera model and sometimes by firmware version. This
is one of the most model-dependent aspects of Canon MakerNote decoding.

---

## Known Idiosyncrasies

| Issue | Details |
|-------|---------|
| **350D firmware 1.0.1** | Reports thumbnail image size 10 bytes too long, causing data to run off the end of the APP1 segment |
| **40D firmware 1.0.4** | Writes MakerNote IFD entry count one greater than actual, causing decoders to read garbage for the last entry |
| **No header signature** | Format detection relies entirely on Make = "Canon" in TIFF IFD. Cannot be identified from MakerNote bytes alone. |
| **Absolute offsets** | Most fragile MakerNote format. Any insertion or deletion of EXIF data before the MakerNote will corrupt all internal pointers. |
| **Default value sentinels** | When Canon has no data for certain tags, they write specific sentinel values (e.g., 0xFFFF, -1) that should be treated as "not set" rather than displayed |
| **CameraInfo variations** | The CameraInfo (tag 0x000d) binary structure varies significantly between camera models and firmware versions. ExifTool uses model-specific decode tables. |
| **ColorData complexity** | The ColorData structure (tag 0x4001) has at least 12 different versions across camera generations, each with different layouts |

---

## Reading Canon MakerNote in Swift

```swift
import ImageIO

func readCanonMakerNote(from url: URL) {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
                  as? [String: Any],
          let canon = props[kCGImagePropertyMakerCanonDictionary as String]
                  as? [String: Any] else { return }

    // Keys are string representations of tag IDs

    // Camera model (tag 6)
    if let imageType = canon["6"] as? String {
        print("Camera: \(imageType)")
    }

    // Firmware (tag 7)
    if let firmware = canon["7"] as? String {
        print("Firmware: \(firmware)")
    }

    // Serial number (tag 12)
    if let serial = canon["12"] as? Int {
        print("Serial: \(serial)")
    }

    // Model ID (tag 16)
    if let modelID = canon["16"] as? Int {
        print("Model ID: 0x\(String(modelID, radix: 16))")
    }

    // Lens model (tag 149, i.e., 0x0095)
    if let lens = canon["149"] as? String {
        print("Lens: \(lens)")
    }

    // Color temperature (tag 174, i.e., 0x00ae)
    if let colorTemp = canon["174"] as? Int {
        print("Color temp: \(colorTemp) K")
    }

    // CameraSettings is tag "1" -- returned as an array by ImageIO
    if let settings = canon["1"] as? [Int] {
        // Focus mode (index 7)
        if settings.count > 7 {
            let focusModes = [0: "One-Shot AF", 1: "AI Servo AF",
                              2: "AI Focus AF", 3: "Manual Focus"]
            print("Focus: \(focusModes[settings[7]] ?? "Unknown (\(settings[7]))")")
        }
        // Exposure mode (index 20)
        if settings.count > 20 {
            let expModes = [0: "Easy", 1: "Program AE", 2: "Tv",
                            3: "Av", 4: "Manual", 5: "A-DEP",
                            7: "Bulb", 8: "Fv"]
            print("Exposure: \(expModes[settings[20]] ?? "Unknown")")
        }
        // Metering mode (index 17)
        if settings.count > 17 {
            let meterModes = [1: "Spot", 2: "Average", 3: "Evaluative",
                              4: "Partial", 5: "Center-weighted"]
            print("Metering: \(meterModes[settings[17]] ?? "Default")")
        }
        // Image stabilization (index 34)
        if settings.count > 34 {
            let isOn = settings[34]
            print("IS: \(isOn == 0 ? "Off" : "On (\(isOn))")")
        }
    }

    // ShotInfo is tag "4" -- returned as an array
    if let shotInfo = canon["4"] as? [Int] {
        // White balance (index 7)
        if shotInfo.count > 7 {
            let wbModes = [0: "Auto", 1: "Daylight", 2: "Cloudy",
                           3: "Tungsten", 4: "Fluorescent",
                           5: "Flash", 6: "Custom", 8: "Shade"]
            print("WB: \(wbModes[shotInfo[7]] ?? "Unknown")")
        }
    }
}
```

---

## Cross-References

- [MakerNote Concept](makernote-concept.md) -- How MakerNote works, offset fragility problem
- [Nikon MakerNote](nikon.md) -- Nikon-specific tags for comparison
- [ImageIO Property Keys](../imageio/property-keys.md) -- `kCGImagePropertyMakerCanonDictionary`
- [EXIF Tag Reference](../exif/tag-reference.md) -- Standard EXIF tags vs Canon MakerNote overlap

### External References

- [ExifTool Canon Tags](https://exiftool.org/TagNames/Canon.html) -- Comprehensive tag reference with all sub-structures
- [Exiv2 Canon Tags](https://exiv2.org/tags-canon.html) -- Tag documentation with type info
- [Canon MakerNote Specification](https://www.ozhiker.com/electronics/pjmt/jpeg_info/canon_mn.html) -- Early reverse-engineered specification
- [ExifTool Canon.pm source](https://github.com/exiftool/exiftool/blob/master/lib/Image/ExifTool/Canon.pm) -- Definitive decode tables (~5,000 lines)
- [Canon-Specific Metadata DeepWiki](https://deepwiki.com/exiftool/exiftool/9.1-canon-specific-metadata) -- Architecture overview
