# EXIF Technical Structure & Complete Tag Tables

> Part of [EXIF Reference](README.md)

The EXIF binary format: APP1 structure, TIFF header, IFD entry format, data
types, byte order, and **complete tag tables for every IFD** as defined by the
EXIF specification (CIPA DC-008, detailed from 3.0 with version-aware guidance
through the latest published 3.1 revision).

These tables document the raw EXIF standard independent of any framework. For
ImageIO-specific keys and XMP mappings, see [`tag-reference.md`](tag-reference.md)
and [`xmp-mapping.md`](xmp-mapping.md).

---

## APP1 Data Layout (JPEG)

In JPEG files, EXIF data lives in the APP1 marker segment (`0xFFE1`):

```
FFD8                 JPEG SOI (Start of Image)
FFE1                 APP1 Marker
SSSS                 APP1 Data Size (2 bytes, big-endian, includes itself)
45786966 0000        Exif Header ("Exif\0\0", 6 bytes)
                     ─── TIFF structure begins here ───
4949 2A00 08000000   TIFF Header (example: little-endian)
XXXX...              IFD0 (main image) directory entries
LLLLLLLL             Link to IFD1 (4 bytes, offset or 0x00000000)
XXXX...              IFD0 data area
XXXX...              Exif SubIFD directory entries
XXXX...              Exif SubIFD data area
XXXX...              GPS IFD (if present)
XXXX...              IFD1 (thumbnail) directory entries
00000000             End of IFD chain
XXXX...              IFD1 data area
FFD8...FFD9          Thumbnail JPEG data
                     ─── TIFF structure ends ───
FFXX...              Other JPEG markers (DQT, DHT, SOF, SOS, etc.)
FFD9                 JPEG EOI (End of Image)
```

**All offsets** within the TIFF structure are counted from the first byte of
the TIFF header (the `"II"` or `"MM"` byte order marker).

---

## TIFF Header (8 bytes)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 2 bytes | Byte order | `0x4949` ("II") = little-endian; `0x4D4D` ("MM") = big-endian |
| 2 | 2 bytes | Magic number | Always `0x002A` (42) |
| 4 | 4 bytes | IFD0 offset | Offset to first IFD, usually `0x00000008` (immediately after header) |

iPhones write little-endian. Most digital cameras use little-endian. Some
manufacturers (Ricoh, older Kodak) use big-endian.

---

## IFD Entry Format (12 bytes)

Each tag in an IFD is a fixed 12-byte entry:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 2 bytes | Tag ID | Tag number (identifies the kind of data) |
| 2 | 2 bytes | Data format | One of the 13 type IDs below |
| 4 | 4 bytes | Component count | Number of values of the given format |
| 8 | 4 bytes | Value / Offset | If total data size (format size x count) <= 4 bytes, the value is stored here directly. Otherwise, this field contains an offset to where the data is stored |

An IFD starts with a 2-byte count of entries, followed by that many 12-byte
entries, followed by a 4-byte offset to the next IFD (or `0x00000000` if last).

---

## Data Types

| ID | Name | Bytes/Component | Description |
|----|------|-----------------|-------------|
| 1 | BYTE | 1 | Unsigned 8-bit integer |
| 2 | ASCII | 1 | 7-bit ASCII string, null-terminated. Count includes the null |
| 3 | SHORT | 2 | Unsigned 16-bit integer |
| 4 | LONG | 4 | Unsigned 32-bit integer |
| 5 | RATIONAL | 8 | Two LONGs: numerator, then denominator |
| 6 | SBYTE | 1 | Signed 8-bit integer |
| 7 | UNDEFINED | 1 | Arbitrary byte sequence (meaning defined per tag) |
| 8 | SSHORT | 2 | Signed 16-bit integer |
| 9 | SLONG | 4 | Signed 32-bit integer |
| 10 | SRATIONAL | 8 | Two SLONGs: signed numerator, then signed denominator |
| 11 | FLOAT | 4 | IEEE 754 single-precision float |
| 12 | DOUBLE | 8 | IEEE 754 double-precision float |
| 129 | UTF-8 | 1 | UTF-8 encoded text **(EXIF 3.0+)** |

---

## Size Constraint in JPEG

All EXIF data must fit in a single APP1 segment: **65,535 bytes (64 KB)** max.
This constrains thumbnail size, MakerNote size, and total tag count. HEIF, PNG,
WebP, and AVIF do not have this limit.

---

## EXIF in File Formats

| Format | Storage Location | Size Limit | Notes |
|--------|-----------------|------------|-------|
| **JPEG** | APP1 segment (`0xFFE1`) | 64 KB | Most common; full EXIF support |
| **TIFF** | Native IFD structure | No practical limit | EXIF is part of the TIFF structure itself |
| **HEIF/HEIC** | EXIF item in ISOBMFF container | No 64 KB limit | Full EXIF; iPhone default since iOS 11 |
| **DNG** | TIFF-based structure | No practical limit | Full EXIF + extensive DNG-specific tags |
| **PNG** | `eXIf` chunk (PNG 1.5+) | No 64 KB limit | Adoption growing |
| **WebP** | EXIF chunk in RIFF container | No 64 KB limit | Read-only in ImageIO |
| **AVIF** | EXIF item in ISOBMFF container | No 64 KB limit | Similar to HEIF |
| **GIF** | Not supported | — | No EXIF capability |

---

## IFD0 Tags (Main Image)

IFD0 contains TIFF baseline tags describing the main image. These tags describe
the image file itself — resolution, color space, creator, and pointers to
sub-IFDs.

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x010e | ImageDescription | ASCII | Any | Image title / description |
| 0x010f | Make | ASCII | Any | Camera manufacturer |
| 0x0110 | Model | ASCII | Any | Camera model name/number |
| 0x0112 | Orientation | SHORT | 1 | Image orientation: 1=top-left (normal), 2=top-right (H flip), 3=bottom-right (180), 4=bottom-left (V flip), 5=left-top, 6=right-top (90 CW), 7=right-bottom, 8=left-bottom (90 CCW) |
| 0x011a | XResolution | RATIONAL | 1 | Horizontal resolution. Default 72/1 (72 DPI) |
| 0x011b | YResolution | RATIONAL | 1 | Vertical resolution. Default 72/1 (72 DPI) |
| 0x0128 | ResolutionUnit | SHORT | 1 | 1=no unit, 2=inch (default), 3=centimeter |
| 0x0131 | Software | ASCII | Any | Firmware or software version |
| 0x0132 | DateTime | ASCII | 20 | Last modified: `"YYYY:MM:DD HH:MM:SS\0"` (20 bytes including null) |
| 0x013b | Artist | ASCII | Any | Creator / photographer name |
| 0x013e | WhitePoint | RATIONAL | 2 | Chromaticity of white point (CIE x, y). D65 = 3127/10000, 3290/10000 |
| 0x013f | PrimaryChromaticities | RATIONAL | 6 | RGB chromaticities (CIE x, y for each). CCIR 709: 640/1000, 330/1000, 300/1000, 600/1000, 150/1000, 60/1000 |
| 0x0211 | YCbCrCoefficients | RATIONAL | 3 | YCbCr-to-RGB coefficients. Default 0.299, 0.587, 0.114 |
| 0x0213 | YCbCrPositioning | SHORT | 1 | 1=centered, 2=co-sited (datum point) |
| 0x0214 | ReferenceBlackWhite | RATIONAL | 6 | Black/white reference values. YCbCr: Y pair, Cb pair, Cr pair |
| 0x8298 | Copyright | ASCII | Any | Copyright string. Photographer + editor separated by null |
| 0x8769 | ExifIFDPointer | LONG | 1 | **Offset to Exif SubIFD** |
| 0x8825 | GPSInfoIFDPointer | LONG | 1 | **Offset to GPS IFD** (see `../gps/`) |

---

## Exif SubIFD Tags (Capture Data)

The Exif SubIFD is the core of EXIF — pointed to by IFD0 tag 0x8769. Contains
all camera settings, exposure data, timestamps, lens info, and processing tags.

### Exposure & Sensitivity

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x829a | ExposureTime | RATIONAL | 1 | Shutter speed in seconds (e.g., 1/250 = 0.004) |
| 0x829d | FNumber | RATIONAL | 1 | F-stop (e.g., 2.8) |
| 0x8822 | ExposureProgram | SHORT | 1 | 0=not defined, 1=manual, 2=normal program, 3=aperture priority, 4=shutter priority, 5=creative (slow program), 6=action (high-speed), 7=portrait, 8=landscape |
| 0x8827 | ISOSpeedRatings | SHORT | Any | ISO sensitivity value(s) |
| 0x8830 | SensitivityType | SHORT | 1 | Which ISO 12232 parameter: 1=SOS, 2=REI, 3=SOS+REI, 4=ISO Speed, 5=SOS+ISO, 6=REI+ISO, 7=all *(v2.3+)* |
| 0x8831 | StandardOutputSensitivity | LONG | 1 | SOS value *(v2.3+)* |
| 0x8832 | RecommendedExposureIndex | LONG | 1 | REI value *(v2.3+)* |
| 0x8833 | ISOSpeed | LONG | 1 | ISO speed value *(v2.3+)* |
| 0x8834 | ISOSpeedLatitudeyyy | LONG | 1 | ISO speed latitude yyy *(v2.3+)* |
| 0x8835 | ISOSpeedLatitudezzz | LONG | 1 | ISO speed latitude zzz *(v2.3+)* |
| 0x9201 | ShutterSpeedValue | SRATIONAL | 1 | APEX shutter speed. Exposure time = 2^(-value) |
| 0x9202 | ApertureValue | RATIONAL | 1 | APEX aperture. F-number = 2^(value/2) |
| 0x9203 | BrightnessValue | SRATIONAL | 1 | APEX brightness. -1 = unknown |
| 0x9204 | ExposureBiasValue | SRATIONAL | 1 | Exposure compensation in EV |
| 0x9205 | MaxApertureValue | RATIONAL | 1 | Smallest F-number of lens (APEX) |
| 0x9206 | SubjectDistance | RATIONAL | 1 | Distance to subject in meters. 0=unknown, 0xFFFFFFFF=infinity |
| 0x9207 | MeteringMode | SHORT | 1 | 0=unknown, 1=average, 2=center-weighted, 3=spot, 4=multi-spot, 5=multi-segment (pattern), 6=partial, 255=other |
| 0x9208 | LightSource | SHORT | 1 | 0=unknown, 1=daylight, 2=fluorescent, 3=tungsten, 4=flash, 9=fine weather, 10=cloudy, 11=shade, 12–15=fluorescent variants, 17=std light A, 18=std light B, 19=std light C, 20=D55, 21=D65, 22=D75, 23=D50, 24=ISO studio tungsten, 255=other |
| 0x9209 | Flash | SHORT | 1 | Bitfield: bit 0=fired, bits 1–2=return detection, bits 3–4=mode, bit 5=no flash function, bit 6=red-eye reduction |
| 0xa215 | ExposureIndex | RATIONAL | 1 | Exposure index selected on camera |
| 0xa402 | ExposureMode | SHORT | 1 | 0=auto, 1=manual, 2=auto bracket *(v2.2+)* |
| 0xa407 | GainControl | SHORT | 1 | 0=none, 1=low gain up, 2=high gain up, 3=low gain down, 4=high gain down *(v2.2+)* |

### Lens & Focal Length

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x920a | FocalLength | RATIONAL | 1 | Actual focal length in mm |
| 0xa405 | FocalLengthIn35mmFilm | SHORT | 1 | 35mm equivalent focal length in mm. 0=unknown *(v2.2+)* |
| 0xa20e | FocalPlaneXResolution | RATIONAL | 1 | Pixels per FocalPlaneResolutionUnit on sensor (X) |
| 0xa20f | FocalPlaneYResolution | RATIONAL | 1 | Pixels per FocalPlaneResolutionUnit on sensor (Y) |
| 0xa210 | FocalPlaneResolutionUnit | SHORT | 1 | 1=no unit, 2=inch, 3=centimeter |
| 0xa432 | LensSpecification | RATIONAL | 4 | [MinFL, MaxFL, MinFN@MinFL, MinFN@MaxFL] *(v2.3+)* |
| 0xa433 | LensMake | ASCII | Any | Lens manufacturer *(v2.3+)* |
| 0xa434 | LensModel | ASCII | Any | Lens model name/number *(v2.3+)* |
| 0xa435 | LensSerialNumber | ASCII | Any | Lens serial number *(v2.3+)* |

### Date & Time

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x9003 | DateTimeOriginal | ASCII | 20 | When original image was captured: `"YYYY:MM:DD HH:MM:SS\0"` |
| 0x9004 | DateTimeDigitized | ASCII | 20 | When image was digitized: `"YYYY:MM:DD HH:MM:SS\0"` |
| 0x9290 | SubSecTime | ASCII | Any | Fractional seconds for IFD0 DateTime. Variable length decimal digits |
| 0x9291 | SubSecTimeOriginal | ASCII | Any | Fractional seconds for DateTimeOriginal |
| 0x9292 | SubSecTimeDigitized | ASCII | Any | Fractional seconds for DateTimeDigitized |
| 0x9010 | OffsetTime | ASCII | 7 | UTC offset for IFD0 DateTime: `"+HH:MM\0"` or `"-HH:MM\0"` *(v2.31+)* |
| 0x9011 | OffsetTimeOriginal | ASCII | 7 | UTC offset for DateTimeOriginal *(v2.31+)* |
| 0x9012 | OffsetTimeDigitized | ASCII | 7 | UTC offset for DateTimeDigitized *(v2.31+)* |

### Image Dimensions & Color

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0xa002 | PixelXDimension | SHORT/LONG | 1 | Valid image width for compressed data |
| 0xa003 | PixelYDimension | SHORT/LONG | 1 | Valid image height for compressed data |
| 0xa001 | ColorSpace | SHORT | 1 | Standard EXIF: 1=sRGB, 65535=uncalibrated. Value 2 appears in some files/tools as non-standard Adobe RGB signaling |
| 0x9101 | ComponentsConfiguration | UNDEFINED | 4 | Channel order: 0=does not exist, 1=Y, 2=Cb, 3=Cr, 4=R, 5=G, 6=B. Typical: `[1,2,3,0]` = YCbCr |
| 0x9102 | CompressedBitsPerPixel | RATIONAL | 1 | Average compression ratio |
| 0xa500 | Gamma | RATIONAL | 1 | Gamma coefficient *(v2.3+)* |

### Scene & Processing

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0xa403 | WhiteBalance | SHORT | 1 | 0=auto, 1=manual *(v2.2+)* |
| 0xa404 | DigitalZoomRatio | RATIONAL | 1 | 0=not used *(v2.2+)* |
| 0xa406 | SceneCaptureType | SHORT | 1 | 0=standard, 1=landscape, 2=portrait, 3=night scene *(v2.2+)* |
| 0xa301 | SceneType | UNDEFINED | 1 | 1=directly photographed |
| 0xa40c | SubjectDistanceRange | SHORT | 1 | 0=unknown, 1=macro, 2=close, 3=distant *(v2.2+)* |
| 0xa408 | Contrast | SHORT | 1 | 0=normal, 1=soft, 2=hard *(v2.2+)* |
| 0xa409 | Saturation | SHORT | 1 | 0=normal, 1=low, 2=high *(v2.2+)* |
| 0xa40a | Sharpness | SHORT | 1 | 0=normal, 1=soft, 2=hard *(v2.2+)* |
| 0xa401 | CustomRendered | SHORT | 1 | 0=normal, 1=custom *(v2.2+)* |
| 0xa300 | FileSource | UNDEFINED | 1 | 1=film scanner, 2=reflection print scanner, 3=digital still camera |
| 0xa302 | CFAPattern | UNDEFINED | Any | Color filter array pattern |
| 0xa217 | SensingMethod | SHORT | 1 | 1=not defined, 2=one-chip color area, 3=two-chip, 4=three-chip, 5=color sequential area, 7=trilinear, 8=color sequential linear |
| 0x9214 | SubjectArea | SHORT | 2–4 | 2=center point (x,y), 3=circle (x,y,d), 4=rectangle (x,y,w,h) *(v2.2+)* |
| 0xa214 | SubjectLocation | SHORT | 2 | (x, y) of main subject |

### Subject & Flash Detail

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0xa20b | FlashEnergy | RATIONAL | 1 | Flash energy in BCPS |
| 0xa20c | SpatialFrequencyResponse | UNDEFINED | Any | Camera SFR per ISO 12233 |
| 0xa40b | DeviceSettingDescription | UNDEFINED | Any | Camera device settings *(v2.2+)* |
| 0x8824 | SpectralSensitivity | ASCII | Any | Spectral sensitivity per ASTM E-1417 |
| 0x8828 | OECF | UNDEFINED | Any | Opto-Electronic Conversion Function per ISO 14524 |

### Composite Images (v2.32+)

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0xa460 | CompositeImage | SHORT | 1 | 0=unknown, 1=not composite, 2=general composite, 3=composite captured while shooting |
| 0xa461 | SourceImageNumberOfCompositeImage | SHORT | 2 | [total source images, used source images] |
| 0xa462 | SourceExposureTimesOfCompositeImage | UNDEFINED | Any | Total exposure time + individual exposure times |

### Environmental Conditions (v2.31+)

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x9400 | Temperature | SRATIONAL | 1 | Ambient temperature in degrees Celsius |
| 0x9401 | Humidity | RATIONAL | 1 | Relative humidity in percent |
| 0x9402 | Pressure | RATIONAL | 1 | Atmospheric pressure in hPa |
| 0x9403 | WaterDepth | SRATIONAL | 1 | Water depth in meters (negative = above surface) |
| 0x9404 | Acceleration | RATIONAL | 1 | Acceleration in mGal (10^-5 m/s^2) |
| 0x9405 | CameraElevationAngle | SRATIONAL | 1 | Camera tilt from horizontal in degrees |

### Version, Identity & Ownership

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x9000 | ExifVersion | UNDEFINED | 4 | Version as 4 ASCII bytes: `"0210"` = 2.1, `"0220"` = 2.2, `"0230"` = 2.3, `"0231"` = 2.31, `"0232"` = 2.32, `"0300"` = 3.0 |
| 0xa000 | FlashpixVersion | UNDEFINED | 4 | FlashPix version, usually `"0100"` |
| 0x927c | MakerNote | UNDEFINED | Any | Vendor-specific binary data. Format is proprietary per manufacturer. See [`makernote.md`](makernote.md) |
| 0x9286 | UserComment | UNDEFINED | Any | User comment. First 8 bytes = charset ID (`"ASCII\0\0\0"`, `"JIS\0\0\0\0\0"`, `"UNICODE\0"`, or 8x `\0` for undefined), remainder = text |
| 0xa420 | ImageUniqueID | ASCII | 33 | 128-bit unique ID as 32 hex characters + null |
| 0xa430 | CameraOwnerName | ASCII | Any | Camera owner *(v2.3+)* |
| 0xa431 | BodySerialNumber | ASCII | Any | Camera body serial number *(v2.3+)* |
| 0xa004 | RelatedSoundFile | ASCII | 13 | Name of related audio file (8.3 format) |
| 0xa005 | InteroperabilityIFDPointer | LONG | 1 | **Offset to Interoperability IFD** |

### EXIF 3.0 Identity Tags

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0xa436 | ImageTitle | ASCII/UTF-8 | Any | Title of the image |
| 0xa437 | Photographer | ASCII/UTF-8 | Any | Name of the photographer |
| 0xa438 | ImageEditor | ASCII/UTF-8 | Any | Name of the main image editor |
| 0xa439 | CameraFirmware | ASCII/UTF-8 | Any | Camera firmware name and version |
| 0xa43a | RAWDevelopingSoftware | ASCII/UTF-8 | Any | RAW development software |
| 0xa43b | ImageEditingSoftware | ASCII/UTF-8 | Any | Image editing software |
| 0xa43c | MetadataEditingSoftware | ASCII/UTF-8 | Any | Metadata editing software |

---

## GPS IFD Tags

Pointed to by IFD0 tag 0x8825. Complete GPS tag reference is in `../gps/`.
Listed here for completeness of the IFD structure.

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x0000 | GPSVersionID | BYTE | 4 | Version `[2,3,0,0]`. Mandatory when GPS IFD present |
| 0x0001 | GPSLatitudeRef | ASCII | 2 | `"N"` or `"S"` |
| 0x0002 | GPSLatitude | RATIONAL | 3 | Degrees, minutes, seconds |
| 0x0003 | GPSLongitudeRef | ASCII | 2 | `"E"` or `"W"` |
| 0x0004 | GPSLongitude | RATIONAL | 3 | Degrees, minutes, seconds |
| 0x0005 | GPSAltitudeRef | BYTE | 1 | 0=above sea level, 1=below sea level |
| 0x0006 | GPSAltitude | RATIONAL | 1 | Altitude in meters |
| 0x0007 | GPSTimeStamp | RATIONAL | 3 | UTC time: hour, minute, second |
| 0x0008 | GPSSatellites | ASCII | Any | Satellites used for measurement |
| 0x0009 | GPSStatus | ASCII | 2 | `"A"`=measurement in progress, `"V"`=measurement interoperability |
| 0x000a | GPSMeasureMode | ASCII | 2 | `"2"`=2D, `"3"`=3D |
| 0x000b | GPSDOP | RATIONAL | 1 | Data degree of precision |
| 0x000c | GPSSpeedRef | ASCII | 2 | `"K"`=km/h, `"M"`=mph, `"N"`=knots |
| 0x000d | GPSSpeed | RATIONAL | 1 | Speed of GPS receiver |
| 0x000e | GPSTrackRef | ASCII | 2 | `"T"`=true direction, `"M"`=magnetic |
| 0x000f | GPSTrack | RATIONAL | 1 | Direction of movement (0.00–359.99 degrees) |
| 0x0010 | GPSImgDirectionRef | ASCII | 2 | `"T"`=true direction, `"M"`=magnetic |
| 0x0011 | GPSImgDirection | RATIONAL | 1 | Direction of image (0.00–359.99 degrees) |
| 0x0012 | GPSMapDatum | ASCII | Any | Geodetic survey data (e.g., `"WGS-84"`) |
| 0x0013 | GPSDestLatitudeRef | ASCII | 2 | `"N"` or `"S"` |
| 0x0014 | GPSDestLatitude | RATIONAL | 3 | Destination latitude: deg, min, sec |
| 0x0015 | GPSDestLongitudeRef | ASCII | 2 | `"E"` or `"W"` |
| 0x0016 | GPSDestLongitude | RATIONAL | 3 | Destination longitude: deg, min, sec |
| 0x0017 | GPSDestBearingRef | ASCII | 2 | `"T"`=true, `"M"`=magnetic |
| 0x0018 | GPSDestBearing | RATIONAL | 1 | Bearing to destination (0.00–359.99) |
| 0x0019 | GPSDestDistanceRef | ASCII | 2 | `"K"`=km, `"M"`=miles, `"N"`=nautical miles |
| 0x001a | GPSDestDistance | RATIONAL | 1 | Distance to destination |
| 0x001b | GPSProcessingMethod | UNDEFINED | Any | Location finding method name (8-byte charset prefix + text) |
| 0x001c | GPSAreaInformation | UNDEFINED | Any | GPS area name (8-byte charset prefix + text) |
| 0x001d | GPSDateStamp | ASCII | 11 | UTC date: `"YYYY:MM:DD\0"` |
| 0x001e | GPSDifferential | SHORT | 1 | 0=no correction, 1=differential correction applied |
| 0x001f | GPSHPositioningError | RATIONAL | 1 | Horizontal positioning error in meters *(v2.31+)* |

---

## Interoperability IFD Tags

Pointed to by Exif SubIFD tag 0xA005. Defines interoperability rules for
file exchange.

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x0001 | InteroperabilityIndex | ASCII | 4 | `"R98"` = ExifR98 (sRGB conformance), `"THM"` = DCF thumbnail file, `"R03"` = DCF option file (Adobe RGB) |
| 0x0002 | InteroperabilityVersion | UNDEFINED | 4 | Version, typically `"0100"` |
| 0x1000 | RelatedImageFileFormat | ASCII | Any | File format of related image |
| 0x1001 | RelatedImageWidth | LONG | 1 | Related image width |
| 0x1002 | RelatedImageLength | LONG | 1 | Related image height |

---

## IFD1 Tags (Thumbnail Image)

IFD1 describes the embedded thumbnail. All IFD0 tags may also appear here.
The critical tags are:

| Tag | Name | Type | Count | Description |
|-----|------|------|-------|-------------|
| 0x0100 | ImageWidth | SHORT/LONG | 1 | Thumbnail width |
| 0x0101 | ImageLength | SHORT/LONG | 1 | Thumbnail height |
| 0x0102 | BitsPerSample | SHORT | 3 | Bits per channel. Usually `[8,8,8]` for uncompressed |
| 0x0103 | Compression | SHORT | 1 | 1=uncompressed, 6=JPEG (most common for thumbnails) |
| 0x0106 | PhotometricInterpretation | SHORT | 1 | 1=monochrome, 2=RGB, 6=YCbCr |
| 0x0111 | StripOffsets | SHORT/LONG | Any | Byte offset(s) to uncompressed image data strips |
| 0x0115 | SamplesPerPixel | SHORT | 1 | Components per pixel. 3 for color |
| 0x0116 | RowsPerStrip | SHORT/LONG | 1 | Rows per strip. If unstriped = ImageLength |
| 0x0117 | StripByteCounts | SHORT/LONG | Any | Byte count(s) per strip |
| 0x011a | XResolution | RATIONAL | 1 | Horizontal resolution |
| 0x011b | YResolution | RATIONAL | 1 | Vertical resolution |
| 0x011c | PlanarConfiguration | SHORT | 1 | 1=chunky (interleaved), 2=planar |
| 0x0128 | ResolutionUnit | SHORT | 1 | 1=no unit, 2=inch, 3=centimeter |
| 0x0201 | JPEGInterchangeFormat | LONG | 1 | **Offset to JPEG thumbnail SOI** (when Compression=6) |
| 0x0202 | JPEGInterchangeFormatLength | LONG | 1 | **Byte count of JPEG thumbnail data** |
| 0x0211 | YCbCrCoefficients | RATIONAL | 3 | YCbCr-to-RGB coefficients |
| 0x0212 | YCbCrSubSampling | SHORT | 2 | Chroma subsampling: [horizontal, vertical] |
| 0x0213 | YCbCrPositioning | SHORT | 1 | 1=centered, 2=co-sited |
| 0x0214 | ReferenceBlackWhite | RATIONAL | 6 | Black/white reference values |

### Thumbnail Formats

- **JPEG thumbnail** (most common): Compression (0x0103) = 6. Data located at
  JPEGInterchangeFormat offset, size = JPEGInterchangeFormatLength. Starts with
  `0xFFD8`, ends with `0xFFD9`. Recommended size: 160x120 pixels.
- **Uncompressed RGB**: Compression = 1, PhotometricInterpretation = 2.
  Data at StripOffsets, size = sum of StripByteCounts.
- **Uncompressed YCbCr**: Compression = 1, PhotometricInterpretation = 6.
  Requires YCbCr-to-RGB conversion using YCbCrCoefficients.

> **Privacy concern:** Editing software sometimes modifies the main image but
> fails to update the thumbnail, potentially leaking pre-edit content.

---

## Multi-Picture Format (MPF)

CIPA DC-007 extension for multi-image files (stereo 3D, panoramas). Lives in
JPEG APP2 segment, separate from the EXIF APP1.

| Tag | Name | Type | Description |
|-----|------|------|-------------|
| 0xb000 | MPFVersion | UNDEFINED | MP format version (4-byte value, typically `0100`) |
| 0xb001 | NumberOfImages | LONG | Total images in MPF file |
| 0xb002 | MPEntry (MPImageList) | UNDEFINED | MP entry list (`16 x NumberOfImages` bytes) |
| 0xb201 | MPFPanOrientation | LONG | Panoramic orientation |
| 0xb204 | MPFBaseViewpointNum | LONG | Base viewpoint for stereo |
| 0xb205 | MPFConvergenceAngle | SRATIONAL | Stereo convergence angle |
| 0xb206 | MPFBaselineLength | RATIONAL | Distance between stereo cameras |

Used by Apple for spatial photos (iPhone 15 Pro+ / Vision Pro).
