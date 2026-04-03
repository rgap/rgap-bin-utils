#!/usr/bin/env python3
"""Transcribe a video/audio file into plain text with pause markers

Usage:
    rgap_video_transcribe.py <input> <output> [--language=<lang>] [--pause-threshold=<sec>]
    rgap_video_transcribe.py -h

Arguments:
    input       Input video or audio file
    output      Output text file (.txt)

Options:
    --language=<lang>         ISO-639-1 language code [default: es]
    --pause-threshold=<sec>   Minimum silence gap to write "(...)" [default: 1.2]
"""

import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


MAX_UPLOAD_BYTES = 24 * 1024 * 1024  # keep a little margin under 25 MB


def run_command(command):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Command failed:\n%s\n\nSTDERR:\n%s" % (
                " ".join(command), result.stderr)
        )
    return result.stdout.strip()


def ffprobe_duration(path):
    output = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    return float(output)


def extract_audio(input_path, output_mp3_path):
    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "32k",
            str(output_mp3_path),
        ]
    )


def split_audio_if_needed(audio_path, chunks_dir):
    size = os.path.getsize(audio_path)
    if size <= MAX_UPLOAD_BYTES:
        return [audio_path]

    duration = ffprobe_duration(audio_path)
    num_chunks = int(math.ceil(size / MAX_UPLOAD_BYTES))
    chunk_seconds = max(60, int(math.ceil(duration / num_chunks)))

    pattern = str(Path(chunks_dir) / "chunk_%03d.mp3")

    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(audio_path),
            "-f",
            "segment",
            "-segment_time",
            str(chunk_seconds),
            "-reset_timestamps",
            "1",
            "-c",
            "copy",
            pattern,
        ]
    )

    chunk_files = sorted(Path(chunks_dir).glob("chunk_*.mp3"))
    chunk_files = [str(p) for p in chunk_files if p.is_file()
                   and p.stat().st_size > 0]

    if not chunk_files:
        raise RuntimeError(
            "Audio splitting failed: no chunk files were produced.")

    return chunk_files


def get_field(obj, name, default=None):
    if hasattr(obj, name):
        return getattr(obj, name)
    if isinstance(obj, dict):
        return obj.get(name, default)
    return default


def normalize_text(text):
    text = (text or "").strip()
    text = " ".join(text.split())
    return text


def ensure_sentence_spacing(text):
    replacements = {
        " ,": ",",
        " .": ".",
        " !": "!",
        " ?": "?",
        " ;": ";",
        " :": ":",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()


def transcribe_chunk(client, chunk_path, language):
    with open(chunk_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
            temperature=0,
        )

    duration = float(get_field(response, "duration", 0.0) or 0.0)
    raw_segments = get_field(response, "segments", []) or []

    segments = []
    for seg in raw_segments:
        start = float(get_field(seg, "start", 0.0) or 0.0)
        end = float(get_field(seg, "end", 0.0) or 0.0)
        text = normalize_text(get_field(seg, "text", ""))

        if end > start and text:
            segments.append(
                {
                    "start": start,
                    "end": end,
                    "text": text,
                }
            )

    if duration <= 0:
        duration = ffprobe_duration(chunk_path)

    return segments, duration


def merge_adjacent_segments(segments, max_gap=0.35):
    if not segments:
        return []

    merged = [segments[0].copy()]

    for seg in segments[1:]:
        prev = merged[-1]
        gap = seg["start"] - prev["end"]

        if gap <= max_gap:
            prev["end"] = seg["end"]
            prev["text"] = ensure_sentence_spacing(
                prev["text"] + " " + seg["text"])
        else:
            merged.append(seg.copy())

    return merged


def write_plaintext(output_path, segments, pause_threshold=1.2):
    with open(output_path, "w", encoding="utf-8") as out:
        previous_end = None
        first_written = False

        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            text = ensure_sentence_spacing(seg["text"])

            if previous_end is not None:
                gap = start - previous_end
                if gap >= pause_threshold:
                    out.write("\n\n(...)\n\n")
                else:
                    out.write(" ")

            out.write(text)
            first_written = True
            previous_end = end

        if first_written:
            out.write("\n")


def main(args):
    load_dotenv()  # loads variables from .env

    input_file = args["<input>"]
    output_file = args["<output>"]
    language = args["--language"]
    pause_threshold = float(args["--pause-threshold"])

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found in .env file.")

    client = OpenAI(api_key=api_key)

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")
        chunks_dir = os.path.join(tmpdir, "chunks")
        os.makedirs(chunks_dir, exist_ok=True)

        extract_audio(input_file, audio_path)
        chunk_paths = split_audio_if_needed(audio_path, chunks_dir)

        all_segments = []
        offset = 0.0

        for chunk_path in chunk_paths:
            segments, duration = transcribe_chunk(client, chunk_path, language)

            for seg in segments:
                all_segments.append(
                    {
                        "start": seg["start"] + offset,
                        "end": seg["end"] + offset,
                        "text": seg["text"],
                    }
                )

            offset += duration

        if not all_segments:
            raise RuntimeError("No transcript segments were returned.")

        merged_segments = merge_adjacent_segments(all_segments)
        write_plaintext(
            output_file,
            merged_segments,
            pause_threshold=pause_threshold,
        )

    print(f"Transcript written to: {output_file}")


if __name__ == "__main__":
    from docopt import docopt

    try:
        main(docopt(__doc__))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
