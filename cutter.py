import subprocess
import os
import config
import random
import json
import textwrap
import re
import time
from datetime import datetime, timedelta, timezone

# =========================
# 🔧 UTILS
# =========================

def escape_text(text):
    return text.replace("\\", "\\\\") \
               .replace(":", "\\:") \
               .replace("'", "\\'") \
               .replace(",", "\\,") \
               .replace("[", "\\[") \
               .replace("]", "\\]")

def get_video_duration(filepath):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        filepath
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])

def get_jakarta_time():
    jakarta = timezone(timedelta(hours=7))
    return datetime.now(jakarta).strftime("%H:%M:%S")

def progress_bar(percent, length=20):
    filled = int(length * percent // 100)
    return "█" * filled + "░" * (length - filled)

def run_ffmpeg_with_progress(command, duration, part):
    start_time = time.time()

    process = subprocess.Popen(
        command,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True,
        universal_newlines=True
    )

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    fps_pattern = re.compile(r"fps=\s*(\d+)")

    last_percent = -1
    fps_value = "0"

    while True:
        line = process.stderr.readline()
        if not line:
            break

        fps_match = fps_pattern.search(line)
        if fps_match:
            fps_value = fps_match.group(1)

        match = time_pattern.search(line)
        if match:
            h, m, s = match.groups()
            current_time = int(h)*3600 + int(m)*60 + float(s)

            percent = min(100, int((current_time / duration) * 100))

            if percent != last_percent:
                elapsed = time.time() - start_time
                eta = (elapsed / percent) * (100 - percent) if percent > 0 else 0
                eta_str = time.strftime("%M:%S", time.gmtime(eta))

                bar = progress_bar(percent)
                jam = get_jakarta_time()

                print(
                    f"\r🕒 {jam} | PART {part} | {bar} {percent}% | ⚡ {fps_value} FPS | ⏱️ ETA {eta_str}",
                    end=""
                )

                last_percent = percent

    process.wait()
    print()

    return process.returncode


# =========================
# 🎬 MAIN PROCESS
# =========================

def process_video(filepath, judul):

    os.makedirs("cut", exist_ok=True)

    total_duration = int(get_video_duration(filepath))
    current_time = 0
    part = 1
    outputs = []

    # ✅ ambil nama TANPA ekstensi
    filename = os.path.splitext(os.path.basename(filepath))[0]

    judul = judul.title()

    wrapped_lines = textwrap.wrap(judul, width=20)

    if len(wrapped_lines) > 3:
        wrapped_lines = wrapped_lines[:3]

    while len(wrapped_lines) < 3:
        wrapped_lines.append("")

    judul_1 = escape_text(wrapped_lines[0])
    judul_2 = escape_text(wrapped_lines[1])
    judul_3 = escape_text(wrapped_lines[2])

    line_count = len([j for j in wrapped_lines if j.strip() != ""])

    if line_count == 1:
        dynamic_fontsize = config.FONT_SIZE
        y1 = "h*0.14"
        y2 = "h*0.14"
        y3 = "h*0.14"

    elif line_count == 2:
        dynamic_fontsize = int(config.FONT_SIZE * 0.9)
        y1 = "h*0.13"
        y2 = f"h*0.13+{dynamic_fontsize+8}"
        y3 = y2

    else:
        dynamic_fontsize = int(config.FONT_SIZE * 0.9)
        y1 = "h*0.12"
        y2 = f"h*0.12+{dynamic_fontsize+8}"
        y3 = f"h*0.12+{(dynamic_fontsize+8)*2}"

    # ===== LOGO TAMBAHAN =====
    logo_top_path = "assets/logo_top.jpg"
    use_logo_top = os.path.exists(logo_top_path)

    while current_time < total_duration:

        duration = random.randint(config.MIN_DURATION, config.MAX_DURATION)
        remaining = total_duration - current_time

        if remaining <= config.MIN_DURATION:
            duration = remaining
        elif remaining < duration:
            duration = remaining

        if duration <= 0:
            break

        duration = int(duration)
        end_time = current_time + duration

        # ✅ output selalu MP4
        output_path = os.path.join("cut", f"cut_{part}_{filename}.mp4")

        text_part = f"PART {part}"

        drawtext = (
            f"drawtext=fontfile={config.FONT_PATH}:text='{judul_1}':"
            f"fontcolor=white:fontsize={dynamic_fontsize}:"
            f"x=(w-text_w)/2:y={y1}:borderw=1:bordercolor=white:shadowcolor=black:shadowx=2:shadowy=2,"

            f"drawtext=fontfile={config.FONT_PATH}:text='{judul_2}':"
            f"fontcolor=white:fontsize={dynamic_fontsize}:"
            f"x=(w-text_w)/2:y={y2}:borderw=1:bordercolor=white:shadowcolor=black:shadowx=2:shadowy=2,"

            f"drawtext=fontfile={config.FONT_PATH}:text='{judul_3}':"
            f"fontcolor=white:fontsize={dynamic_fontsize}:"
            f"x=(w-text_w)/2:y={y3}:borderw=1:bordercolor=white:shadowcolor=black:shadowx=2:shadowy=2,"

            f"drawtext=fontfile={config.FONT_PATH}:text='{text_part}':"
            f"fontcolor=white:fontsize={config.FONT_SIZE_PART}:"
            f"x=(w-text_w)/2:y=h*0.82:borderw=2:bordercolor=white:shadowcolor=black:shadowx=2:shadowy=2"
        )

        extra_overlay = ""
        base_label = "[base]"

        if use_logo_top:
            extra_overlay = (
                f"[2:v]scale=160:-1,format=rgba,colorchannelmixer=aa=0.8[wm2];"
                f"[base][wm2]overlay=W-w-85:85[tmp1];"
            )
            base_label = "[tmp1]"

        vf_filter = (
            f"[0:v]trim=start={current_time}:end={end_time},"
            "setpts=PTS-STARTPTS,"
            "crop=ih:ih:(iw-ih)/2:0,"
            "scale=1080:1080,"
            "pad=1080:1920:0:(1920-1080)/2:color=black[base];"

            f"[0:a]atrim=start={current_time}:end={end_time},"
            "asetpts=PTS-STARTPTS[aout];"

            + extra_overlay +

            f"[1:v]scale={config.WM_SIZE}:-1,"
            "format=rgba,"
            f"colorchannelmixer=aa={config.WM_OPACITY}[wm];"

            f"{base_label}[wm]overlay={config.WM_POS_X}:{config.WM_POS_Y},"

            + drawtext +
            "[vout]"
        )

        codec = "h264_nvenc" if getattr(config, "USE_GPU", False) else "libx264"

        inputs = [
            "-i", filepath,
            "-i", "assets/logo.png"
        ]

        if use_logo_top:
            inputs += ["-i", logo_top_path]

        command = [
            "ffmpeg",
            "-fflags", "+genpts",
            "-avoid_negative_ts", "make_zero",
            *inputs,
            "-filter_complex", vf_filter,
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", codec,
            "-preset", "p4" if codec == "h264_nvenc" else "veryfast",
            "-rc", "vbr" if codec == "h264_nvenc" else None,
            "-cq", "23" if codec == "h264_nvenc" else None,
            "-b:v", "0" if codec == "h264_nvenc" else None,
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",  # ✅ tambahan penting
            "-profile:v", "high",
            "-threads", "32",
            "-vsync", "2",
            "-c:a", "aac",
            "-y",
            output_path
        ]

        command = [c for c in command if c is not None]

        result_code = run_ffmpeg_with_progress(command, duration, part)

        if result_code != 0:
            print(f"❌ PART {part} gagal")
        elif os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            caption = f"{judul} - Part {part}"
            outputs.append((output_path, caption))
            print(f"✅ Part {part} berhasil ({duration} detik)")
        else:
            print(f"❌ Part {part} gagal, skip")

        current_time += duration
        part += 1

    return outputs