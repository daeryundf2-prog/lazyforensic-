#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_kakao.py
Parse KakaoTalk mobile/PC text exports.

Does not read Kakao SQLite, chat_logs, Android/iOS backups, or UTF-16
chat databases. Mobile export lines have no seconds; those timestamps
end with :00.
"""

import argparse
import json
import re
import sys

DATE_HEADER_REGEX = re.compile(r"^-+\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일.*-+$")
MOBILE_MSG_REGEX = re.compile(r"^\[(.+?)\]\s*\[(오전|오후)\s*(\d{1,2}):(\d{2})\]\s*(.*)$")
PC_MSG_REGEX = re.compile(r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s*(.+)\s*:\s+(.*)$")


def read_kakao_text(filepath):
    with open(filepath, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-16")


def parse_kakao_text(text):
    messages = []
    current_date = None

    for line in text.splitlines():
        line_str = line.strip()
        if not line_str:
            continue

        date_match = DATE_HEADER_REGEX.match(line_str)
        if date_match:
            y, m, d = date_match.groups()
            current_date = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
            continue

        mob_match = MOBILE_MSG_REGEX.match(line_str)
        if mob_match:
            user, ampm, hour, minute, content = mob_match.groups()
            h = int(hour)
            if ampm == "오후" and h != 12:
                h += 12
            elif ampm == "오전" and h == 12:
                h = 0
            ts = (
                f"{current_date} {h:02d}:{int(minute):02d}:00"
                if current_date is not None
                else None
            )
            messages.append({
                "timestamp": ts,
                "timestamp_unknown": current_date is None,
                "sender": user,
                "message": content,
                "has_attachment": ("사진" in content or "동영상" in content or "파일:" in content),
                "second_precision": "export-has-no-seconds",
            })
            continue

        pc_match = PC_MSG_REGEX.match(line_str)
        if pc_match:
            ts, user, content = pc_match.groups()
            messages.append({
                "timestamp": ts,
                "timestamp_unknown": False,
                "sender": user,
                "message": content,
                "has_attachment": ("파일 전송" in content or "사진" in content or "동영상" in content),
                "second_precision": "as-exported",
            })
            continue

        if messages:
            messages[-1]["message"] += "\n" + line_str

    return messages


def parse_kakao_file(filepath):
    return parse_kakao_text(read_kakao_text(filepath))


def main(argv=None):
    parser = argparse.ArgumentParser(description="KakaoTalk text-export parser")
    parser.add_argument("input", help="KakaoTalk text export file")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--keyword", help="Filter messages containing keyword")
    args = parser.parse_args(argv)

    try:
        msgs = parse_kakao_file(args.input)
    except OSError as exc:
        print(f"[-] Failed to read input: {exc}", file=sys.stderr)
        return 2

    if args.keyword:
        kw = args.keyword.lower()
        msgs = [m for m in msgs if kw in m["message"].lower() or kw in m["sender"].lower()]

    print(f"[+] Total parsed messages: {len(msgs)}")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(msgs, f, ensure_ascii=False, indent=2)
        print(f"[+] Saved to: {args.output}")
    else:
        for m in msgs[:10]:
            preview = m["message"][:60].replace("\n", " ")
            print(f"[{m['timestamp']}] {m['sender']}: {preview}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
