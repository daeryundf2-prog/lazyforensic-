#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_kakao.py
KakaoTalk Chat Log Parser
Supports Mobile & PC KakaoTalk text exports, extracts messages, dates, users, attachments.
"""

import re
import sys
import json
import argparse
from datetime import datetime

DATE_HEADER_REGEX = re.compile(r'^-+\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일.*-+$')
MOBILE_MSG_REGEX = re.compile(r'^\[(.+?)\]\s*\[(오전|오후)\s*(\d{1,2}):(\d{2})\]\s*(.*)$')
PC_MSG_REGEX = re.compile(r'^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s*([^:]+?)\s*:\s*(.*)$')

def parse_kakao_file(filepath):
    messages = []
    current_date = "1970-01-01"

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue

            # Check date header
            date_match = DATE_HEADER_REGEX.match(line_str)
            if date_match:
                y, m, d = date_match.groups()
                current_date = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
                continue

            # Check Mobile format
            mob_match = MOBILE_MSG_REGEX.match(line_str)
            if mob_match:
                user, ampm, hour, minute, content = mob_match.groups()
                h = int(hour)
                if ampm == "오후" and h != 12:
                    h += 12
                elif ampm == "오전" and h == 12:
                    h = 0
                ts = f"{current_date} {h:02d}:{int(minute):02d}:00"
                messages.append({
                    "timestamp": ts,
                    "sender": user,
                    "message": content,
                    "has_attachment": ("사진" in content or "동영상" in content or "파일:" in content)
                })
                continue

            # Check PC format
            pc_match = PC_MSG_REGEX.match(line_str)
            if pc_match:
                ts, user, content = pc_match.groups()
                messages.append({
                    "timestamp": ts,
                    "sender": user,
                    "message": content,
                    "has_attachment": ("파일 전송" in content or "사진" in content or "동영상" in content)
                })
                continue

            # Multiline continuation
            if messages:
                messages[-1]["message"] += "\n" + line_str

    return messages

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="KakaoTalk Log Parser")
    parser.add_argument('input', help="KakaoTalk text export file")
    parser.add_argument('--output', help="Output JSON file path")
    parser.add_argument('--keyword', help="Filter messages containing keyword")
    args = parser.parse_args()

    msgs = parse_kakao_file(args.input)
    if args.keyword:
        kw = args.keyword.lower()
        msgs = [m for m in msgs if kw in m['message'].lower() or kw in m['sender'].lower()]

    print(f"[+] Total parsed messages: {len(msgs)}")
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(msgs, f, ensure_ascii=False, indent=2)
        print(f"[+] Saved to: {args.output}")
    else:
        for m in msgs[:10]:
            print(f"[{m['timestamp']}] {m['sender']}: {m['message'][:60]}")
