#!/usr/bin/env python
"""
    A script to automate my audio-encoding setup.
    
    Dependencies:
        - ffmpeg    (https://www.ffmpeg.org/download.html)
"""

import argparse
import glob
import json
import mimetypes
import os
import subprocess

__author__ = "NightfallMemories"
__license__ = 'MIT'
__version__ = '1.0.0'

ignored_types = ["aac", "ac3", "opus"]
desired_languages = ["jpn"] # alpha-3 codes

mimetypes.add_type('video/x-matroska', '.mkv')
mimetypes.add_type('audio/x-matroska', '.mka')

def main():
    files = (glob.glob("**/*", recursive=True) if args.recursive else glob.glob("*"))
    for f in files:
        mime_type = mimetypes.types_map.get(os.path.splitext(f)[-1], "")
        if not mime_type.startswith("audio") and not mime_type.startswith("video") and not f.endswith(".mkv"):
            continue
        print(f"Checking the file \"{f}\"...")
        audio_tracks = get_audio_tracks(f)
        print(f"--Audio tracks found: {len(audio_tracks)}")
        for index, audio in enumerate(audio_tracks):
            if audio.get("language") not in desired_languages:
                print(f"--The audio track {index} ({audio.get("language")}) isn't in the desired languages: {", ".join(desired_languages)}.")
                continue
            if audio.get("codec") in ignored_types:
                print(f"--The audio track {index} ({audio.get("codec").upper()}) is in the ignored codecs list: {", ".join(ignored_types).upper()}.")
                continue
            encode_opus(f, audio, index)

        
def encode_opus(f, audio, index):
    try:
        subprocess.run(["ffmpeg", "-i", f, "-stats", "-loglevel", "error", "-map", f"0:{audio.get("stream_index")}","-c:a", "libopus", "-b:a", f"{args.bitrate}", f"{os.path.splitext(f)[0]}.opus"])
        print(f"--The audio track {index} ({audio.get("codec").upper()}) ({audio.get("language")}) was successfully encoded to OPUS.")
    except Exception as e:
        print(e)
    
def get_audio_tracks(f):
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index,codec_name:stream_tags=language", "-of", "json", f], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if not result.stdout:
        print(result.stderr)
        return []
    metadata = json.loads(result.stdout)
    audio = []
    if "streams" in metadata:
        for stream in metadata["streams"]:
            index = stream.get("index", 0)
            codec_name = stream.get("codec_name", "unknown")
            language = stream.get("tags", {}).get("language", "und")
            audio.append({"stream_index": index, "codec": codec_name, "language": language})
    return audio

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-R", "--recursive", action="store_true", default=False, help="Encode files recursively (default: %(default)s)")
    parser.add_argument("-B", "--bitrate", action="store", type=int, default=192000, help="Bitrate for opus encoding. Usually 192kbps for FLAC 2.0 and 256kbps for FLAC 5.0+. (default: %(default)s)")
    args = parser.parse_args()
    main()
    