# 🎬 Auto Video Cutter Shorts/Reels Generator (Termux)

Script Python untuk memotong video otomatis menjadi beberapa part Shorts/Reels/TikTok dengan watermark, judul otomatis, logo overlay, progress bar realtime, dan support GPU NVENC.

---

# ✨ Features

- 🎞 Auto split video menjadi beberapa part
- 📱 Output format vertical 1080x1920
- 🏷 Auto watermark logo
- 📝 Auto judul overlay
- ⚡ Support GPU NVENC
- 📊 Progress bar realtime
- 🔥 FFmpeg optimized
- 🎵 Audio otomatis ikut terpotong
- 🧩 Dynamic text layout

---

# 📂 Project Structure

```txt
project/
│
├── main.py
├── config.py
│
├── assets/
│   ├── logo.png
│   ├── logo_top.jpg
│   └── font.ttf
│
├── cut/
│
└── README.md
```

---

# 📦 Requirements

## Install Python

```bash
pkg update && pkg upgrade -y
pkg install python -y
```

---

## Install FFmpeg

```bash
pkg install ffmpeg -y
```

Cek apakah berhasil:

```bash
ffmpeg -version
ffprobe -version
```

---

# 🚀 Clone Repository

```bash
pkg install git -y

git clone https://github.com/TeamAbabilCoded/snack.git

cd snack
```

---

# 📥 Install Dependencies

Script ini menggunakan standard library Python.

Tidak ada package external yang wajib diinstall.

(Optional)

```bash
pip install -r requirements.txt
```

Isi requirements.txt:

```txt
# no external dependencies
```

---

# ⚙️ Configuration

Edit file `config.py`

Example:

```python
FONT_PATH = "assets/font.ttf"

FONT_SIZE = 60
FONT_SIZE_PART = 45

MIN_DURATION = 50
MAX_DURATION = 90

WM_SIZE = 140
WM_OPACITY = 0.7

WM_POS_X = "W-w-30"
WM_POS_Y = "H-h-30"

USE_GPU = False
```

---

# 📁 Assets

Masukkan file berikut ke folder `assets/`

| File | Fungsi |
|---|---|
| logo.png | watermark utama |
| logo_top.jpg | logo tambahan kanan atas |
| font.ttf | font text overlay |

---

# ▶️ Usage

Example:

```python
process_video("video.mp4", "Judul Video")
```

Run:

```bash
python main.py
```

---

# 📤 Output

Semua hasil video akan masuk ke folder:

```txt
cut/
```

Format output:

```txt
cut_1_namafile.mp4
cut_2_namafile.mp4
cut_3_namafile.mp4
```

---

# 📱 Output Format

- Resolution: `1080x1920`
- Format: `MP4`
- Codec: `H264`
- Audio: `AAC`

---

# ⚡ GPU Encoding (Optional)

Jika device support NVENC:

```python
USE_GPU = True
```

Cek encoder:

```bash
ffmpeg -encoders | grep nvenc
```

---

# 🛠 Troubleshooting

## ffmpeg not found

Install ulang:

```bash
pkg install ffmpeg
```

---

## Font error

Pastikan file:

```txt
assets/font.ttf
```

ada.

---

## Output gagal

Pastikan:
- video input valid
- ffmpeg terinstall
- storage permission termux sudah diberikan

---

# 🔓 Storage Permission

Jalankan:

```bash
termux-setup-storage
```

---

# 📜 License

MIT License

---

# ❤️ Credits
- Muhammad Khairil
- KarFeed
  
Powered by:
- Python
- FFmpeg
- Termux
