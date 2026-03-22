# Supported Image Formats

ImageIO's format support is queryable at runtime:

- `CGImageSourceCopyTypeIdentifiers()` — all **readable** UTIs
- `CGImageDestinationCopyTypeIdentifiers()` — all **writable** UTIs

The lists below reflect the state as of iOS 18 / macOS 15.

---

## Standard Raster Formats


| Format      | UTI                  | Read | Write | iOS  | Dictionary                       |
| ----------- | -------------------- | ---- | ----- | ---- | -------------------------------- |
| JPEG / JFIF | `public.jpeg`        | ✓    | ✓     | 4.0+ | `kCGImagePropertyJFIFDictionary` |
| PNG         | `public.png`         | ✓    | ✓     | 4.0+ | `kCGImagePropertyPNGDictionary`  |
| GIF         | `com.compuserve.gif` | ✓    | ✓     | 4.0+ | `kCGImagePropertyGIFDictionary`  |
| TIFF        | `public.tiff`        | ✓    | ✓     | 4.0+ | `kCGImagePropertyTIFFDictionary` |
| BMP         | `com.microsoft.bmp`  | ✓    | ✓     | 4.0+ | —                                |
| ICO         | `com.microsoft.ico`  | ✓    | ✓     | 4.0+ | —                                |


---

## Modern Formats


| Format           | UTI                    | Read | Write | iOS   | Dictionary                               |
| ---------------- | ---------------------- | ---- | ----- | ----- | ---------------------------------------- |
| HEIC (HEVC)      | `public.heic`          | ✓    | ✓     | 11.0+ | `kCGImagePropertyHEIFDictionary` (16.0+) |
| HEIF (generic)   | `public.heif`          | ✓    | ✓     | 16.0+ | `kCGImagePropertyHEIFDictionary`         |
| HEICS (sequence) | `public.heics`         | ✓    | ✓     | 13.0+ | `kCGImagePropertyHEICSDictionary`        |
| WebP             | `org.webmproject.webp` | ✓    | —     | 14.0+ | `kCGImagePropertyWebPDictionary`         |
| AVIF             | `public.avif`          | ✓    | ✓?    | 16.0+ | `kCGImagePropertyAVISDictionary`         |
| AVIS (sequence)  | `public.avis`          | ✓    | —     | 16.0+ | `kCGImagePropertyAVISDictionary`         |
| JPEG XL          | `public.jpeg-xl`       | ✓    | —     | 17.0+ | —                                        |
| JPEG 2000        | `public.jpeg-2000`     | ✓    | ✓     | 4.0+  | —                                        |


> **AVIF write note:** Apple confirms AVIF read support in iOS 16, but no
> public documentation explicitly lists `public.avif` as a writable
> `CGImageDestination` type. Verify write support at runtime via
> `CGImageDestinationCopyTypeIdentifiers()`.
>
> **JPEG XL note:** ImageIO decode support added in iOS 17. The formal
> `UTType.jpegxl` constant was added later in iOS 18.2; use the UTI string
> `"public.jpeg-xl"` directly on iOS 17. Camera capture (write) only on
> iPhone 16 series; files are wrapped in a DNG container.

---

## RAW Formats

All RAW formats are **read-only** in ImageIO. DNG is the one exception where
ImageIO can also write.


| Format        | Extension(s) | Vendor            | Dictionary                       |
| ------------- | ------------ | ----------------- | -------------------------------- |
| DNG           | .dng         | Universal (Adobe) | `kCGImagePropertyDNGDictionary`  |
| Canon CR2     | .cr2         | Canon             | `kCGImagePropertyRawDictionary`  |
| Canon CR3     | .cr3         | Canon             | `kCGImagePropertyRawDictionary`  |
| Canon CRW     | .crw         | Canon (legacy)    | `kCGImagePropertyCIFFDictionary` |
| Nikon NEF     | .nef         | Nikon             | `kCGImagePropertyRawDictionary`  |
| Nikon NRW     | .nrw         | Nikon (Coolpix)   | `kCGImagePropertyRawDictionary`  |
| Sony ARW      | .arw         | Sony              | `kCGImagePropertyRawDictionary`  |
| Sony SRF      | .srf         | Sony (legacy)     | `kCGImagePropertyRawDictionary`  |
| Fujifilm RAF  | .raf         | Fujifilm          | `kCGImagePropertyRawDictionary`  |
| Olympus ORF   | .orf         | Olympus           | `kCGImagePropertyRawDictionary`  |
| Pentax PEF    | .pef         | Pentax            | `kCGImagePropertyRawDictionary`  |
| Panasonic RW2 | .rw2         | Panasonic         | `kCGImagePropertyRawDictionary`  |


> Apple maintains a per-camera support list updated with each OS release.
> See Apple Support article HT211241 for the full list.
>
> **Fujifilm RAF caveat:** Only uncompressed RAF is supported; compressed
> RAF files may not decode.

---

## HDR & Specialty Formats


| Format       | UTI                        | Read | Write | iOS   | Dictionary                          |
| ------------ | -------------------------- | ---- | ----- | ----- | ----------------------------------- |
| OpenEXR      | `com.ilm.openexr-image`    | ✓    | ✓     | 11.3+ | `kCGImagePropertyOpenEXRDictionary` |
| Radiance HDR | `public.radiance`          | ✓    | —     | —     | —                                   |
| TGA          | `com.truevision.tga-image` | ✓    | ✓     | 14.0+ | `kCGImagePropertyTGADictionary`     |
| PBM          | `public.pbm`               | ✓    | ✓     | —     | —                                   |


---

## Legacy & Specialty Formats


| Format          | UTI                         | Read | Write | Platform   | Dictionary                       |
| --------------- | --------------------------- | ---- | ----- | ---------- | -------------------------------- |
| PSD (Photoshop) | `com.adobe.photoshop-image` | ✓    | ✓     | All        | `kCGImageProperty8BIMDictionary` |
| PDF             | `com.adobe.pdf`             | ✓    | ✓     | All        | —                                |
| ICNS            | `com.apple.icns`            | ✓    | —     | macOS only | —                                |
| PICT            | `com.apple.pict`            | ✓    | —     | macOS only | —                                |
| SGI             | —                           | ✓    | —     | macOS only | —                                |
| MPO             | `public.mpo-image`          | ✓    | —     | All        | —                                |


---

## GPU Texture Formats

Primarily for game/GPU rendering, not photo applications:


| Format | UTI                 | Platform | Notes                                          |
| ------ | ------------------- | -------- | ---------------------------------------------- |
| ASTC   | `org.khronos.astc`  | iOS 8+   | Read + Write; recommended for modern iOS (A8+) |
| KTX    | `org.khronos.ktx`   | iOS 14+  | Read + Write; Khronos texture container        |
| KTX2   | `org.khronos.ktx2`  | iOS 14+  | Read + Write; Khronos texture container v2     |
| PVR    | `public.pvr`        | iOS      | Read only; legacy, prefer ASTC                 |
| ATX    | `com.apple.atx`     | iOS      | Read + Write; Apple texture format             |
| DDS    | `com.microsoft.dds` | iOS      | Read + Write; DirectDraw Surface               |


---

## Metadata Capabilities by Format

### Which formats support which metadata standards?


| Format        | EXIF | XMP         | IPTC IIM | ICC | GPS (via EXIF) |
| ------------- | ---- | ----------- | -------- | --- | -------------- |
| **JPEG**      | ✓    | ✓           | ✓        | ✓   | ✓              |
| **TIFF**      | ✓    | ✓           | ✓        | ✓   | ✓              |
| **HEIF/HEIC** | ✓    | ✓           | —        | ✓   | ✓              |
| **AVIF**      | —    | ✓           | —        | ✓   | —              |
| **PNG**       | —    | ✓ (iTXt)    | —        | ✓   | —              |
| **WebP**      | —?   | ✓           | —        | ✓   | —?             |
| **DNG**       | ✓    | ✓           | —        | ✓   | ✓              |
| **Other RAW** | ✓    | ✓ (sidecar) | —        | ✓   | ✓              |
| **GIF**       | —    | —           | —        | —   | —              |
| **BMP**       | —    | —           | —        | —   | —              |
| **OpenEXR**   | —    | ✓           | —        | ✓   | —              |


> **Key takeaway:** JPEG and TIFF are the only formats supporting all three
> metadata standards (EXIF + XMP + IPTC IIM). Modern formats (HEIF, WebP,
> AVIF) use EXIF and/or XMP only.
>
> **WebP note:** The WebP container format supports EXIF chunks, and ImageIO
> may expose EXIF/GPS properties from WebP files. Apple does not explicitly
> document this; verify at runtime on your target OS.
>
> **AVIF note:** Apple documents AVIF format support but does not publish a
> fully explicit metadata capability matrix by standard. Treat this row as a
> conservative default and validate required keys on your target OS at runtime.

### Animation support


| Format          | Animated | API                                                                          | iOS                            |
| --------------- | -------- | ---------------------------------------------------------------------------- | ------------------------------ |
| GIF             | ✓        | `CGAnimateImageAtURLWithBlock` + per-frame `CGImageSourceCreateImageAtIndex` | 4.0+ (frames), 13.0+ (animate) |
| APNG            | ✓        | `CGAnimateImageAtURLWithBlock`                                               | 13.0+                          |
| HEICS           | ✓        | Multi-image `CGImageSource`                                                  | 13.0+                          |
| WebP (animated) | ✓        | Multi-image `CGImageSource` (frame iteration)                               | 14.0+ (read)                   |


### Auxiliary data support (depth, gain maps, mattes)


| Format | Depth | Gain Map      | Portrait Matte | Segmentation |
| ------ | ----- | ------------- | -------------- | ------------ |
| HEIC   | ✓     | ✓             | ✓              | ✓            |
| JPEG   | —     | ✓ (iOS 14.1+) | —              | —            |
| DNG    | ✓     | —             | —              | —            |


---

## Recent Additions Timeline


| iOS  | Formats Added                                                                                          |
| ---- | ------------------------------------------------------------------------------------------------------ |
| 4.0  | JPEG, PNG, GIF, TIFF, BMP, ICO, JPEG 2000, PSD, RAW (DNG, CR2, NEF, ARW, etc.)                         |
| 7.0  | — (XMP metadata API added, not formats)                                                                |
| 11.0 | HEIC/HEIF read-write                                                                                   |
| 11.3 | OpenEXR read                                                                                           |
| 13.0 | HEICS (image sequences)                                                                                |
| 14.0 | WebP read, TGA read                                                                                    |
| 16.0 | AVIF/AVIS read, HEIF dictionary, AVIS dictionary                                                       |
| 17.0 | JPEG XL read, `kCGImageSourceDecodeToHDR` / `kCGImageSourceDecodeToSDR`                                |
| 18.0 | JPEG XL camera write (iPhone 16 only), ISO 21496-1 HDR encoding, `kCGImageAuxiliaryDataTypeISOGainMap` |


