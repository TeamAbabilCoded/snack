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
# 🔧 DEBUG LOG
# =========================

os.environ["FFREPORT"] = "file=ffmpeg_log.txt:level=32"

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

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    data = json.loads(result.stdout)

    return float(data["format"]["duration"])

def get_jakarta_time():

    jakarta = timezone(
        timedelta(hours=7)
    )

    return datetime.now(jakarta).strftime(
        "%H:%M:%S"
    )

def progress_bar(percent, length=20):

    filled = int(
        length * percent // 100
    )

    return (
        "█" * filled +
        "░" * (length - filled)
    )

# =========================
# ⚡ FFMPEG PROGRESS
# =========================

def run_ffmpeg_with_progress(
    command,
    duration,
    part
):

    start_time = time.time()

    process = subprocess.Popen(
        command,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True,
        universal_newlines=True
    )

    time_pattern = re.compile(
        r"time=(\d+):(\d+):(\d+\.\d+)"
    )

    fps_pattern = re.compile(
        r"fps=\s*(\d+)"
    )

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

            current_time = (
                int(h) * 3600 +
                int(m) * 60 +
                float(s)
            )

            percent = min(
                100,
                int(
                    (current_time / duration)
                    * 100
                )
            )

            if percent != last_percent:

                elapsed = (
                    time.time() - start_time
                )

                eta = (
                    (elapsed / percent)
                    * (100 - percent)
                    if percent > 0 else 0
                )

                eta_str = time.strftime(
                    "%M:%S",
                    time.gmtime(eta)
                )

                bar = progress_bar(percent)

                jam = get_jakarta_time()

                print(
                    f"\r🕒 {jam} | "
                    f"PART {part} | "
                    f"{bar} {percent}% | "
                    f"⚡ {fps_value} FPS | "
                    f"⏱️ ETA {eta_str}",
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

    total_duration = int(
        get_video_duration(filepath)
    )

    current_time = 0
    part = 1
    outputs = []

    filename = os.path.splitext(
        os.path.basename(filepath)
    )[0]

    judul = judul.title()

    # =========================
    # 📝 AUTO WRAP TITLE
    # =========================

    max_lines = 6

    wrapped_lines = textwrap.wrap(
        judul,
        width=24
    )

    if len(wrapped_lines) > max_lines:

        wrapped_lines = (
            wrapped_lines[:max_lines]
        )

        wrapped_lines[-1] += "..."

    line_count = len(wrapped_lines)

    # =========================
    # 🔠 DYNAMIC FONT SIZE
    # =========================

    if line_count <= 2:

        dynamic_fontsize = (
            config.FONT_SIZE
        )

    elif line_count <= 4:

        dynamic_fontsize = int(
            config.FONT_SIZE * 0.85
        )

    else:

        dynamic_fontsize = int(
            config.FONT_SIZE * 0.72
        )

    # =========================
    # 📍 TEXT POSITION
    # =========================

    start_y = 0.10

    line_spacing = (
        dynamic_fontsize + 12
    )

    # =========================
    # 🖼 LOGO TAMBAHAN
    # =========================

    logo_top_path = (
        "assets/logo_top.jpg"
    )

    use_logo_top = os.path.exists(
        logo_top_path
    )

    # =========================
    # 🔁 PROCESS LOOP
    # =========================

    while current_time < total_duration:

        duration = random.randint(
            config.MIN_DURATION,
            config.MAX_DURATION
        )

        remaining = (
            total_duration - current_time
        )

        if remaining <= config.MIN_DURATION:

            duration = remaining

        elif remaining < duration:

            duration = remaining

        if duration <= 0:
            break

        duration = int(duration)

        end_time = current_time + duration

        output_path = os.path.join(
            "cut",
            f"cut_{part}_{filename}.mp4"
        )

        text_part = f"PART {part}"

        # =========================
        # 🎨 GENERATE TITLE TEXT
        # =========================

        drawtext_lines = []

        for i, line in enumerate(
            wrapped_lines
        ):

            safe_line = escape_text(line)

            y_pos = (
                f"h*{start_y}+"
                f"{i * line_spacing}"
            )

            drawtext_lines.append(

                f"drawtext="
                f"fontfile={config.FONT_PATH}:"
                f"text='{safe_line}':"
                f"fontcolor=white:"
                f"fontsize={dynamic_fontsize}:"
                f"x=(w-text_w)/2:"
                f"y={y_pos}:"
                f"borderw=2:"
                f"bordercolor=black:"
                f"shadowcolor=black:"
                f"shadowx=2:"
                f"shadowy=2"
            )

        judul_drawtext = ",".join(
            drawtext_lines
        )

        # =========================
        # 🎬 FULL TEXT OVERLAY
        # =========================

        drawtext = (

            judul_drawtext +

            ","

            f"drawtext="
            f"fontfile={config.FONT_PATH}:"
            f"text='{text_part}':"
            f"fontcolor=white:"
            f"fontsize={config.FONT_SIZE_PART}:"
            f"x=(w-text_w)/2:"
            f"y=h*0.82:"
            f"borderw=2:"
            f"bordercolor=black:"
            f"shadowcolor=black:"
            f"shadowx=2:"
            f"shadowy=2"
        )

        extra_overlay = ""

        base_label = "[base]"

        if use_logo_top:

            extra_overlay = (

                f"[2:v]"
                f"scale=120:-1,"
                f"format=rgba,"
                f"colorchannelmixer="
                f"aa=0.8[wm2];"

                f"[base][wm2]"
                f"overlay=W-w-40:40[tmp1];"
            )

            base_label = "[tmp1]"

        # =========================
        # 🎥 VIDEO FILTER
        # =========================

        vf_filter = (

            f"[0:v]"
            f"trim=start={current_time}:"
            f"end={end_time},"

            "setpts=PTS-STARTPTS,"

            "crop=ih:ih:(iw-ih)/2:0,"

            # ringan untuk Android
            "scale=720:720,"

            "pad=720:1280:0:"
            "(1280-720)/2:"
            "color=black[base];"

            f"[0:a]"
            f"atrim=start={current_time}:"
            f"end={end_time},"

            "asetpts=PTS-STARTPTS[aout];"

            + extra_overlay +

            f"[1:v]"
            f"scale={config.WM_SIZE}:-1,"

            "format=rgba,"

            f"colorchannelmixer="
            f"aa={config.WM_OPACITY}[wm];"

            f"{base_label}[wm]"
            f"overlay="
            f"{config.WM_POS_X}:"
            f"{config.WM_POS_Y},"

            + drawtext +

            "[vout]"
        )

        # =========================
        # 🎥 INPUTS
        # =========================

        inputs = [
            "-i", filepath,
            "-i", "assets/logo.png"
        ]

        if use_logo_top:

            inputs += [
                "-i",
                logo_top_path
            ]

        # =========================
        # 🎬 FFMPEG COMMAND
        # =========================

        command = [

            "ffmpeg",

            "-y",

            "-hide_banner",

            "-loglevel",
            "warning",

            *inputs,

            "-filter_complex",
            vf_filter,

            "-map", "[vout]",

            "-map", "[aout]",

            # encoder paling kompatibel
            "-c:v", "libx264",

            # preset ringan Android
            "-preset", "ultrafast",

            # kualitas
            "-crf", "28",

            # kompatibel hp lama
            "-pix_fmt", "yuv420p",

            "-profile:v", "baseline",

            "-level", "3.0",

            # bitrate aman
            "-maxrate", "2M",

            "-bufsize", "4M",

            # audio
            "-c:a", "aac",

            "-b:a", "96k",

            "-ar", "44100",

            "-ac", "2",

            # fast start
            "-movflags",
            "+faststart",

            # thread kecil
            "-threads", "1",

            output_path
        ]

        result_code = (
            run_ffmpeg_with_progress(
                command,
                duration,
                part
            )
        )

        if result_code != 0:

            print(
                f"❌ PART {part} gagal"
            )

        elif (
            os.path.exists(output_path)
            and
            os.path.getsize(output_path)
            > 1000
        ):

            caption = (
                f"{judul} - Part {part}"
            )

            outputs.append(
                (
                    output_path,
                    caption
                )
            )

            print(
                f"✅ Part {part} berhasil "
                f"({duration} detik)"
            )

        else:

            print(
                f"❌ PART {part} gagal"
            )

        current_time += duration

        part += 1

    return outputs