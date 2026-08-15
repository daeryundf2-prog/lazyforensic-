#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup.py
Preflight / Dependency Checker for forensic-video in LazyForensic.
Checks ffmpeg, ffprobe, yt-dlp, and API keys.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_BINARIES = ["ffmpeg", "ffprobe"]


def check_binaries() -> tuple[list[str], list[str]]:
    found = []
    missing = []
    for b in REQUIRED_BINARIES:
        if shutil.which(b) is not None:
            found.append(b)
        else:
            missing.append(b)

    # Check yt-dlp via PATH or python module
    if shutil.which("yt-dlp"):
        found.append("yt-dlp")
    else:
        py_scripts_ytdlp = Path(sys.executable).parent / "Scripts" / "yt-dlp.exe"
        if py_scripts_ytdlp.exists():
            found.append("yt-dlp")
        else:
            try:
                res = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode == 0:
                    found.append("yt-dlp")
                else:
                    missing.append("yt-dlp")
            except Exception:
                missing.append("yt-dlp")

    return found, missing


def get_status() -> dict:
    found, missing = check_binaries()
    has_keys = bool(os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"))
    
    can_proceed = len(missing) == 0
    return {
        "status": "ready" if can_proceed else "needs_install",
        "can_proceed": can_proceed,
        "found_binaries": found,
        "missing_binaries": missing,
        "has_api_keys": has_keys,
        "platform": platform.system(),
    }


def main():
    if "--check" in sys.argv:
        status = get_status()
        if status["can_proceed"]:
            sys.exit(0)
        else:
            sys.exit(2)

    if "--json" in sys.argv:
        print(json.dumps(get_status(), indent=2))
        return

    status = get_status()
    print("=" * 60)
    print("  [LazyForensic] Forensic Video Analysis Preflight")
    print("=" * 60)
    print(f"  OS Platform      : {status['platform']}")
    print(f"  Installed Tools  : {', '.join(status['found_binaries']) or 'None'}")
    if status["missing_binaries"]:
        print(f"  [!] Missing Tools : {', '.join(status['missing_binaries'])}")
        print("-" * 60)
        print("  [권장 설치 명령어]")
        if platform.system() == "Windows":
            print("  - winget install Gyan.FFmpeg")
            print("  - python -m pip install yt-dlp")
        elif platform.system() == "Darwin":
            print("  - brew install ffmpeg yt-dlp")
        else:
            print("  - sudo apt install ffmpeg && pip install yt-dlp")
    else:
        print("  [OK] All required video analysis tools (ffmpeg, ffprobe, yt-dlp) are ready!")
    print("=" * 60)


if __name__ == "__main__":
    main()
