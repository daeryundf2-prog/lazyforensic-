#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_timestamps.py
Digital Forensic File Timestamp & Metadata Tamper Auditor
Inspects MACB timestamps, checks creation vs modified inversion, and computes cryptographic hashes.
"""

import os
import sys
import hashlib
import argparse
from datetime import datetime

def format_ts(ts):
    if ts is None: return "N/A"
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def compute_hashes(filepath):
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            md5.update(chunk)
            sha256.update(chunk)
    return md5.hexdigest(), sha256.hexdigest()

def audit_file(filepath):
    if not os.path.exists(filepath):
        print(f"[-] File not found: {filepath}")
        return None

    stat = os.stat(filepath)
    c_time = getattr(stat, 'st_ctime', None)
    m_time = getattr(stat, 'st_mtime', None)
    a_time = getattr(stat, 'st_atime', None)
    size_bytes = stat.st_size

    try:
        md5_hash, sha256_hash = compute_hashes(filepath)
    except Exception as e:
        md5_hash, sha256_hash = f"Error: {e}", f"Error: {e}"

    # Inversion analysis
    inverted = False
    inversion_note = "정상 (생성시간 <= 수정시간)"
    if c_time and m_time:
        if c_time > m_time:
            inverted = True
            diff_sec = c_time - m_time
            inversion_note = f"⚠️ [생성일시 > 수정일시 역전 발견] (차이: 약 {int(diff_sec // 60)}분)\n     └ 원인 분석: 타 저장매체/인터넷에서 복사/다운로드 시 정상적으로 나타나는 현상 또는 속성 조작 가능성"

    result = {
        "file_path": os.path.abspath(filepath),
        "file_name": os.path.basename(filepath),
        "size_bytes": size_bytes,
        "created_time": format_ts(c_time),
        "modified_time": format_ts(m_time),
        "accessed_time": format_ts(a_time),
        "is_inverted": inverted,
        "analysis_note": inversion_note,
        "md5": md5_hash,
        "sha256": sha256_hash
    }
    return result

def print_audit_report(res):
    print("=" * 70)
    print("  [법무법인 대륜 디지털포렌식센터] 파일 타임스탬프 & 무결성 감정 리포트")
    print("=" * 70)
    print(f"  파일명       : {res['file_name']}")
    print(f"  전체 경로    : {res['file_path']}")
    print(f"  파일 크기    : {res['size_bytes']:,} Bytes")
    print("-" * 70)
    print(f"  생성 일시(C) : {res['created_time']}")
    print(f"  수정 일시(M) : {res['modified_time']}")
    print(f"  접근 일시(A) : {res['accessed_time']}")
    print("-" * 70)
    print(f"  무결성 MD5   : {res['md5']}")
    print(f"  무결성 SHA256: {res['sha256']}")
    print("-" * 70)
    print(f"  [감정 분석 의견]")
    print(f"  {res['analysis_note']}")
    print("=" * 70)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Forensic File Timestamp & Tamper Auditor")
    parser.add_argument('file', help="Target file path to audit")
    args = parser.parse_args()

    res = audit_file(args.file)
    if res:
        print_audit_report(res)
