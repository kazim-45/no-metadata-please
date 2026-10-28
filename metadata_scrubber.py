#!/usr/bin/env python3
"""
Metadata Scrubber - strip sensitive metadata from photos, images and media.

Removes things like GPS location, camera/phone model, serial numbers, author
names, timestamps, software tags, embedded thumbnails, comments and more.
Your original files are never modified: a cleaned copy "<name>_clean.<ext>"
is written next to the original (or to a folder you choose).

Requirements:
    pip install pillow
    ffmpeg on your PATH (optional, only needed for video/audio files)

Run:
    python metadata_scrubber.py
"""

import os
import queue
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover
    Image = None

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".bmp"}
MEDIA_EXTS = {
    ".mp4", ".m4v", ".mov", ".mkv", ".webm", ".avi",
    ".mp3", ".m4a", ".aac", ".flac", ".wav", ".ogg", ".opus",
}
ALL_EXTS = sorted(IMAGE_EXTS | MEDIA_EXTS)


# --------------------------------------------------------------------------
# Core cleaning logic (no GUI code below this line until the GUI section)
# --------------------------------------------------------------------------

def unique_output_path(src, out_dir):
    stem, ext = os.path.splitext(os.path.basename(src))
    folder = out_dir or os.path.dirname(os.path.abspath(src))
    candidate = os.path.join(folder, f"{stem}_clean{ext}")
    n = 2
    while os.path.exists(candidate):
        candidate = os.path.join(folder, f"{stem}_clean_{n}{ext}")
        n += 1
    return candidate


def describe_image_metadata(im):
    """Return a short human-readable summary of what metadata was present."""
    found = []
    try:
        exif = im.getexif()
        if len(exif):
            found.append(f"{len(exif)} EXIF tags")
        if exif.get_ifd(0x8825):
            found.append("GPS LOCATION")
        make_model = " ".join(str(exif.get(t, "")) for t in (0x010F, 0x0110)).strip()
        if make_model:
            found.append(f"device: {make_model}")
    except Exception:
        pass
    for key in im.info:
        if key in ("icc_profile", "transparency", "duration", "loop", "background",
                   "disposal", "version", "dpi", "jfif", "jfif_version",
                   "jfif_unit", "jfif_density", "progressive", "progression"):
            continue
        found.append(f"'{key}' data")
    if "xmp" in im.info or "XML:com.adobe.xmp" in im.info:
        found.append("XMP")
    return ", ".join(found) if found else "none detected"


def clean_image(src, dst, keep_icc=True):
    if Image is None:
        raise RuntimeError("Pillow is not installed (pip install pillow)")

    with Image.open(src) as im:
        fmt = im.format
        report = describe_image_metadata(im)
        icc = im.info.get("icc_profile") if keep_icc else None
        transparency = im.info.get("transparency")
        n_frames = getattr(im, "n_frames", 1)

        frames, durations = [], []
        if n_frames == 1:
            # Bake the EXIF rotation into the pixels so the photo still looks
            # right after the orientation tag is removed.
            frames.append(ImageOps.exif_transpose(im))
        else:
            for i in range(n_frames):
                im.seek(i)
                durations.append(im.info.get("duration", 100))
                frames.append(im.copy())
        loop = im.info.get("loop", 0)

        # Rebuild every frame from raw pixel data only: nothing else carries over.
        clean_frames = []
        for f in frames:
            c = Image.frombytes(f.mode, f.size, f.tobytes())
            if f.mode in ("P", "PA") and f.getpalette():
                c.putpalette(f.getpalette())
            clean_frames.append(c)

        first, rest = clean_frames[0], clean_frames[1:]
        kw = {}
        if icc:
            kw["icc_profile"] = icc

        if fmt == "JPEG":
            if first.mode not in ("RGB", "L", "CMYK"):
                first = first.convert("RGB")
            first.save(dst, "JPEG", quality=95, optimize=True, **kw)
        elif fmt == "PNG":
            if transparency is not None:
                kw["transparency"] = transparency
            first.save(dst, "PNG", optimize=True, **kw)
        elif fmt == "GIF":
            if transparency is not None:
                kw["transparency"] = transparency
            first.save(dst, "GIF", save_all=bool(rest), append_images=rest,
                       duration=durations or 100, loop=loop, disposal=2, **kw)
        elif fmt == "WEBP":
            first.save(dst, "WEBP", quality=95, save_all=bool(rest),
                       append_images=rest, duration=durations or 100,
                       loop=loop, **kw)
        elif fmt == "TIFF":
            first.save(dst, "TIFF", compression="tiff_lzw", **kw)
        else:  # BMP and anything else Pillow can round-trip
            first.save(dst, fmt)
    return report


def clean_media(src, dst):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found - install it to clean video/audio files")
    cmd = [
        ffmpeg, "-y", "-loglevel", "error", "-i", src,
        "-map", "0",                # keep all video/audio/subtitle streams
        "-map_metadata", "-1",      # drop global + per-stream metadata
        "-map_chapters", "-1",      # drop chapters
        "-dn",                      # drop data streams (GPS tracks, etc.)
        "-c", "copy",               # no re-encoding, no quality loss
        "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact",
        dst,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        if os.path.exists(dst):
            os.remove(dst)
        raise RuntimeError(result.stderr.strip().splitlines()[-1] if result.stderr else "ffmpeg failed")
    return "all container metadata, chapters and data streams removed"


def clean_file(src, out_dir, keep_icc):
    ext = os.path.splitext(src)[1].lower()
    dst = unique_output_path(src, out_dir)
    if ext in IMAGE_EXTS:
        report = clean_image(src, dst, keep_icc)
    elif ext in MEDIA_EXTS:
        report = clean_media(src, dst)
    else:
        raise RuntimeError(f"unsupported file type '{ext}'")
    return dst, report


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Metadata Scrubber")
        self.geometry("720x560")
        self.minsize(600, 460)
        self.files = []
        self.msgs = queue.Queue()
        self.out_dir = tk.StringVar(value="")
        self.same_folder = tk.BooleanVar(value=True)
        self.keep_icc = tk.BooleanVar(value=True)
        self._build()
        self.after(100, self._poll)

    def _build(self):
        pad = {"padx": 10, "pady": 5}

        ttk.Label(self, text="Strip location, device info and other hidden data from your files.",
                  font=("TkDefaultFont", 11, "bold")).pack(anchor="w", **pad)

        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, **pad)
        self.listbox = tk.Listbox(mid, selectmode="extended", height=8)
        sb = ttk.Scrollbar(mid, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=sb.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        btns = ttk.Frame(mid)
        btns.pack(side="left", fill="y", padx=(10, 0))
        ttk.Button(btns, text="Add files…", command=self.add_files).pack(fill="x", pady=2)
        ttk.Button(btns, text="Remove selected", command=self.remove_selected).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear", command=self.clear).pack(fill="x", pady=2)

        opts = ttk.LabelFrame(self, text="Options")
        opts.pack(fill="x", **pad)
        ttk.Checkbutton(opts, text="Save cleaned copy next to the original",
                        variable=self.same_folder, command=self._toggle_out).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=8, pady=2)
        self.out_entry = ttk.Entry(opts, textvariable=self.out_dir, state="disabled")
        self.out_entry.grid(row=1, column=0, sticky="ew", padx=8, pady=2)
        self.out_btn = ttk.Button(opts, text="Choose folder…", command=self.choose_out, state="disabled")
        self.out_btn.grid(row=1, column=1, padx=8, pady=2)
        ttk.Checkbutton(opts, text="Keep colour profile (ICC) - not personal data, keeps colours accurate",
                        variable=self.keep_icc).grid(row=2, column=0, columnspan=3, sticky="w", padx=8, pady=2)
        opts.columnconfigure(0, weight=1)

        self.go = ttk.Button(self, text="Remove metadata", command=self.start)
        self.go.pack(fill="x", **pad)
        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=10)

        self.log = ScrolledText(self, height=10, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True, **pad)
        self._log("Originals are never changed. Cleaned copies are named <name>_clean.<ext>.")
        if Image is None:
            self._log("WARNING: Pillow not installed - run: pip install pillow")
        if not shutil.which("ffmpeg"):
            self._log("Note: ffmpeg not found, so video/audio files can't be cleaned (images are fine).")

    # -- helpers
    def _log(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _toggle_out(self):
        state = "disabled" if self.same_folder.get() else "normal"
        self.out_entry.config(state=state)
        self.out_btn.config(state=state)

    def choose_out(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self.out_dir.set(d)

    def add_files(self):
        exts = " ".join(f"*{e}" for e in ALL_EXTS)
        paths = filedialog.askopenfilenames(
            title="Select images or media",
            filetypes=[("Supported files", exts), ("All files", "*.*")])
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert("end", p)

    def remove_selected(self):
        for i in reversed(self.listbox.curselection()):
            self.listbox.delete(i)
            del self.files[i]

    def clear(self):
        self.listbox.delete(0, "end")
        self.files.clear()

    # -- processing
    def start(self):
        if not self.files:
            messagebox.showinfo("Nothing to do", "Add some files first.")
            return
        out_dir = None if self.same_folder.get() else self.out_dir.get().strip()
        if out_dir is not None and not os.path.isdir(out_dir):
            messagebox.showerror("Output folder", "Please choose a valid output folder.")
            return
        self.go.config(state="disabled")
        self.progress.config(maximum=len(self.files), value=0)
        files = list(self.files)
        threading.Thread(target=self._worker, args=(files, out_dir, self.keep_icc.get()),
                         daemon=True).start()

    def _worker(self, files, out_dir, keep_icc):
        ok = 0
        for f in files:
            name = os.path.basename(f)
            try:
                dst, report = clean_file(f, out_dir, keep_icc)
                ok += 1
                self.msgs.put(("log", f"✔ {name}\n    found: {report}\n    saved: {dst}"))
            except Exception as e:
                self.msgs.put(("log", f"✘ {name}: {e}"))
            self.msgs.put(("step", None))
        self.msgs.put(("done", f"Finished: {ok}/{len(files)} file(s) cleaned."))

    def _poll(self):
        try:
            while True:
                kind, val = self.msgs.get_nowait()
                if kind == "log":
                    self._log(val)
                elif kind == "step":
                    self.progress.step(1)
                elif kind == "done":
                    self._log(val)
                    self.go.config(state="normal")
        except queue.Empty:
            pass
        self.after(100, self._poll)


if __name__ == "__main__":
    App().mainloop()
