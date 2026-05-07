from cutter import process_video
import os

print("Bot mulai jalan...")

judul = input("Masukkan Judul: ")

os.makedirs("video", exist_ok=True)
os.makedirs("cut", exist_ok=True)

files = [
    f for f in os.listdir("video")
    if f.lower().endswith((".mp4", ".mov", ".mkv", ".avi"))
]

if not files:
    print("Folder video kosong ❌")
else:
    for file in files:
        filepath = os.path.join("video", file)
        print(f"Proses file: {file}")

        results = process_video(filepath, judul)

        # hanya tampilkan hasil cut
        for output, caption in results:
            print(f"✅ Video selesai di cut: {output}")

print("\n🔥 Semua video selesai diproses dan tersimpan di folder 'cut'")