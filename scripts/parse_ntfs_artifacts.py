#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_ntfs_artifacts.py - Dissect 기반 디스크 이미지 및 NTFS/아티팩트 무설치 파서
"""

import os
import sys
import json
import argparse
from datetime import datetime

def run_dissect_query(target_path: str, artifact_type: str) -> list:
    """Fox-IT Dissect 프레임워크를 활용한 아티팩트 추출"""
    try:
        from dissect.target import Target
    except ImportError:
        print("[!] Dissect 프레임워크가 설치되어 있지 않습니다. pip install dissect 를 실행하십시오.", file=sys.stderr)
        return []

    results = []
    try:
        target = Target.open(target_path)
        if artifact_type == "users":
            for user in target.users():
                results.append({
                    "username": getattr(user, "name", "N/A"),
                    "home": getattr(user, "home", "N/A"),
                    "sid": getattr(user, "sid", "N/A")
                })
        elif artifact_type == "prefetch":
            for pf in target.prefetch():
                results.append({
                    "executable": getattr(pf, "name", "N/A"),
                    "run_count": getattr(pf, "run_count", 0),
                    "last_run": str(getattr(pf, "last_run", "N/A"))
                })
        elif artifact_type == "eventlogs":
            for record in target.eventlogs():
                results.append({
                    "timestamp": str(getattr(record, "ts", "N/A")),
                    "provider": getattr(record, "provider", "N/A"),
                    "event_id": getattr(record, "event_id", "N/A"),
                    "computer": getattr(record, "computer", "N/A")
                })
        elif artifact_type == "shimcache":
            for shim in target.shimcache():
                results.append({
                    "path": getattr(shim, "path", "N/A"),
                    "last_modified": str(getattr(shim, "last_modified", "N/A")),
                    "exec_flag": getattr(shim, "exec_flag", "N/A")
                })
    except Exception as e:
        print(f"[!] Dissect query error on '{target_path}': {e}", file=sys.stderr)

    return results

def main():
    parser = argparse.ArgumentParser(description="Fox-IT Dissect 기반 디스크 아티팩트 파서")
    parser.add_argument("target", help="분석 대상 디스크 이미지 (E01, RAW, VHDX, VMDK) 또는 루트 경로")
    parser.add_argument("--artifact", "-a", choices=["users", "prefetch", "eventlogs", "shimcache"], default="prefetch", help="추출할 아티팩트 유형")
    parser.add_argument("--output", "-o", help="결과 JSON 저장 경로")

    args = parser.parse_args()
    
    if not os.path.exists(args.target):
        print(f"Error: Target not found: {args.target}", file=sys.stderr)
        sys.exit(1)
        
    print(f"[*] Extracting artifact '{args.artifact}' from '{args.target}'...")
    data = run_dissect_query(args.target, args.artifact)
    
    output_json = {
        "target": args.target,
        "artifact": args.artifact,
        "count": len(data),
        "extracted_at": datetime.now().isoformat(),
        "records": data
    }
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_json, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved {len(data)} records to: {args.output}")
    else:
        print(json.dumps(output_json, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
