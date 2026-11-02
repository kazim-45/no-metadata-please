# 🕵️ NO-METADATA

**Drag. Drop. Gone. A privacy-first metadata remover for your photos, images, video and audio.**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-red.svg)](#-requirements)
[![Offline](https://img.shields.io/badge/network-100%25%20offline-brightgreen.svg)](#-how-it-works)

Every photo you take quietly carries a diary: **where** you were, **what** device you used, **when** you took it, and **which** software touched it. NO-METADATA wipes all of it in one click, from a simple desktop window with drag and drop. Everything runs locally. Nothing is uploaded, logged or phoned home.

> *Privacy and security are a right.*

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **🖱️ Drag & Drop** | Drop files or whole folders onto the window. Folders are scanned recursively |
| **🧹 Deep Metadata Stripping** | GPS coordinates, device make/model, serial numbers, timestamps, software tags, author names, comments, XMP and embedded thumbnails |
| **🛡️ Originals Never Touched** | Writes a clean copy named `<name>_clean.<ext>`, so your source files are never modified |
| **📸 Multi-Format Support** | Images (JPG, PNG, GIF, WebP, TIFF, BMP), Video (MP4, MOV, MKV, WebM, AVI), Audio (MP3, M4A, FLAC, WAV, OGG, OPUS) |
| **🔎 Per-File Report** | Shows what was found and removed, for example `GPS LOCATION` or `device: Apple iPhone 14 Pro` |
| **⚡ Batch Processing** | Clean hundreds of files in one run with a live progress bar |
| **🔄 Orientation-Safe** | Bakes photo rotation into the pixels so images don't flip sideways once the tag is gone |
| **🌐 Fully Offline** | No network access, no telemetry, no accounts |

---

## 🚀 Quick Installation

**Linux / macOS (one command):**

```bash
# Clone the repository
git clone https://github.com/kazim-45/no-metadata-please.git
cd no-metadata-please

# Run the automated installer (one-time)
chmod +x install.sh
./install.sh

# Launch NO-METADATA from anywhere
no-metadata
```

The installer sets up a private environment, offers to install Tkinter if your system lacks it, and adds a `no-metadata` command plus an app-menu entry.

**Manual / Windows installation:**

```bash
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python no_metadata.py
```

**Optional, for video and audio files:**

```bash
sudo apt install ffmpeg         # Debian / Ubuntu / Kali
brew install ffmpeg             # macOS
winget install ffmpeg           # Windows
```

> 💡 To remove everything the installer created: `./uninstall.sh`

---

## 🎯 Use Cases

### 🔒 Privacy Hardening
Strip metadata before posting photos on social media, forums or marketplaces. Stop leaking your home address through the GPS tags in your pictures.

### 📰 Journalists & Activists
Share images and recordings without exposing your device, your location or your sources.

### 🏠 Everyday Sharing
Selling something online or sending photos of your kids? Remove the hidden location trail first.

### 🏆 CTF & Security Practice
Compare a file before and after cleaning to learn exactly what metadata hides inside it.

---

## 📖 Usage

```bash
no-metadata                  # after ./install.sh
python3 no_metadata.py       # manual install
```

1. **Drag and drop** files or folders onto the window, or use **Add files…** / **Add folder…**
2. *(Optional)* Untick "Save next to the original" to choose a different output folder
3. Click **Remove metadata**
4. Find your cleaned copies as `<name>_clean.<ext>`

---

## 🧠 How It Works

- **Images:** every frame is rebuilt from raw pixel data only, so EXIF, XMP, IPTC, PNG text chunks, GIF comments and thumbnails have nothing to ride along on. The image is then saved fresh.
- **Video / audio:** ffmpeg copies the streams without re-encoding (`-c copy`) while dropping global and per-stream metadata, chapters and data streams. There is no quality loss.

---

## 🔧 Requirements

- **OS:** Linux, macOS or Windows
- **Python:** 3.8 or higher, with Tkinter
- **Python packages:** pillow, tkinterdnd2 (installed automatically)
- **Optional:** ffmpeg, for video and audio files

---

## ⚠️ Limitations

Be honest about what metadata removal can and cannot do:

- **JPEGs are re-encoded** at quality 95, so there is a very small quality change. That is the price of a reliable strip.
- **Visible content still identifies you.** Faces, street signs, reflections and documents in frame are not metadata, and this tool can't remove them.
- **Your filename is not changed**, so rename files that contain names or places.
- **Unsupported formats** (HEIC, RAW, PDF, Office documents) are skipped with a message.
- **Verify important files** yourself: `exiftool cleaned_file.jpg` shows anything that remains.

---

## 🤝 Contributing

Contributions, bug reports and feature requests are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/heic-support`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

**Ideas:** HEIC support, PDF and Office document cleaning, a command-line mode, a before/after metadata viewer.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## ⚠️ Disclaimer

NO-METADATA is provided as-is to help protect **your own privacy**. It reduces what hidden data your files carry, but it can't guarantee anonymity. Review the limitations above and check sensitive files before sharing them.

---

## 👨‍💻 Author

**Kazim Khan**
- GitHub: [@kazim-45](https://github.com/kazim-45)
- Portfolio: [kazimportfolio](https://kazimportfolio.vercel.app)

---

## 🙏 Acknowledgments

- Image handling by [Pillow](https://python-pillow.org/)
- Media cleaning by [FFmpeg](https://ffmpeg.org/)
- Drag and drop by [tkinterdnd2](https://pypi.org/project/tkinterdnd2/)

---

**⭐ If this tool protected your privacy, consider giving it a star!**
