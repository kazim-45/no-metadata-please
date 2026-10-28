# Metadata Scrubber

A simple, offline desktop tool that removes sensitive metadata from your photos, images, video and audio before you share them.

> Privacy and security are a right.

Photos and media files quietly carry hidden data: GPS coordinates, phone or camera model, serial numbers, timestamps, editing software, author names, comments and embedded thumbnails. Metadata Scrubber strips it out in a few clicks.

## Features

- Simple GUI: add files, click **Remove metadata**
- Batch processing with a progress bar and a per-file report of what was found (for example "GPS LOCATION")
- **Never touches your originals**: writes a cleaned copy named `<name>_clean.<ext>`
- Works fully offline: no network access, no telemetry, no accounts
- Bakes photo rotation into the pixels, so images don't come out sideways after the orientation tag is removed
- Optional colour profile (ICC) retention for accurate colours

## Supported formats

| Type | Formats | Needs |
|------|---------|-------|
| Images | JPG/JPEG, PNG, GIF (animated too), WebP (animated too), TIFF, BMP | Pillow |
| Video / audio | MP4, M4V, MOV, MKV, WebM, AVI, MP3, M4A, AAC, FLAC, WAV, OGG, OPUS | ffmpeg |

## Installation

Requires Python 3.8+.

```bash
git clone https://github.com/<your-username>/metadata-scrubber.git
cd metadata-scrubber
pip install -r requirements.txt
```

Tkinter ships with most Python installs. On some Linux distributions you need to install it separately:

```bash
sudo apt install python3-tk      # Debian / Ubuntu
sudo dnf install python3-tkinter # Fedora
```

**Optional, for video and audio:** install [ffmpeg](https://ffmpeg.org/download.html) and make sure it is on your `PATH`.

```bash
brew install ffmpeg              # macOS
sudo apt install ffmpeg          # Debian / Ubuntu
winget install ffmpeg            # Windows
```

## Usage

```bash
python metadata_scrubber.py
```

1. Click **Add files…** and pick one or more images or media files.
2. Optionally choose a different output folder.
3. Click **Remove metadata**.
4. Find your cleaned copies as `<name>_clean.<ext>`.

## How it works

- **Images:** each frame is rebuilt from raw pixel data only, so EXIF, XMP, IPTC, PNG text chunks, GIF comments and thumbnails are not carried over. The image is then saved fresh.
- **Video / audio:** ffmpeg copies the streams without re-encoding (`-c copy`) while dropping global and per-stream metadata, chapters and data streams.

## Limitations

- JPEGs are re-encoded at quality 95, so there is a very small quality change.
- The tool removes embedded metadata only. It cannot remove identifying **visible content** (faces, street signs, reflections, documents in frame) or hide your **filename**.
- Filesystem timestamps on the new file reflect when it was created.
- Unsupported formats (for example HEIC, RAW, PDF, Office documents) are skipped with a message.
- Always spot-check an important file yourself, for example with `exiftool cleaned_file.jpg`.

## Verifying the result

[ExifTool](https://exiftool.org/) is a good way to confirm a file is clean:

```bash
exiftool photo_clean.jpg
```

## Contributing

Issues and pull requests are welcome. Ideas: drag-and-drop support, HEIC support, PDF and Office document cleaning, a command-line mode.

## License

MIT, see [LICENSE](LICENSE).
