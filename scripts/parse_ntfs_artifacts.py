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
    """Fox-IT Dissect 프레임워크를 활용한 아티팩트 추출 (bring-your-own-binary 래퍼).
    E01/RAW는 dissect + ewf 플러그인 필요. 실패 시 빈 리스트 + stderr 힌트 (exit 코드는 호출자가 결정).
    """
    try:
        from dissect.target import Target
    except ImportError:
        print("[!] Dissect 프레임워크가 설치되어 있지 않습니다. pip install dissect 를 실행하십시오.", file=sys.stderr)
        print("    Hint: pip install dissect[full] 또는 pip install dissect.target", file=sys.stderr)
        return []

    # E01 사전 힌트
    lower = target_path.lower()
    if lower.endswith(('.e01', '.ex01', '.e0')):
        print("[i] E01 감지: ewf/ewf-mount 플러그인이 필요할 수 있습니다. dissect.volume.ewf 확인.", file=sys.stderr)

    results = []
    target = None
    try:
        # Target.open 은 디렉토리/마운트 경로와 일부 이미지를 처리. E01은 플러그인 없으면 예외.
        target = Target.open(target_path)
    except Exception as e:
        print(f"[!] Dissect Target.open 실패 on '{target_path}': {e}", file=sys.stderr)
        print("    Hint: 이미지가 E01이면 ewfmount 후 마운트 경로를 전달하거나, dissect[full] 설치 확인.", file=sys.stderr)
        return []

    try:
        if artifact_type == "users":
            for user in target.users():
                results.append({
                    "username": getattr(user, "name", "N/A"),
                    "home": getattr(user, "home", "N/A"),
                    "sid": getattr(user, "sid", "N/A")
                })
        elif artifact_type == "prefetch":
            # dissect 3.15+ 는 target.prefetch() 대신 plugins 호환성 필요 — try both
            func = getattr(target, "prefetch", None)
            if func is None:
                print("[!] target.prefetch() 미지원 Dissect 버전. dissect.target 3.15+ 권장.", file=sys.stderr)
            else:
                for pf in func():
                    results.append({
                        "executable": getattr(pf, "name", getattr(pf, "executable", "N/A")),
                        "run_count": getattr(pf, "run_count", 0),
                        "last_run": str(getattr(pf, "last_run", getattr(pf, "last_execution", "N/A")))
                    })
        elif artifact_type == "eventlogs":
            func = getattr(target, "eventlogs", None)
            if func is None:
                print("[!] target.eventlogs() 미지원. 대신 Hayabusa/Chainsaw로 .evtx 직접 분석 권장.", file=sys.stderr)
            else:
                for record in func():
                    results.append({
                        "timestamp": str(getattr(record, "ts", getattr(record, "timestamp", "N/A"))),
                        "provider": getattr(record, "provider", getattr(record, "source", "N/A")),
                        "event_id": getattr(record, "event_id", getattr(record, "event_id", "N/A")),
                        "computer": getattr(record, "computer", "N/A")
                    })
        elif artifact_type == "shimcache":
            func = getattr(target, "shimcache", None)
            if func is None:
                print("[!] target.shimcache() 미지원 Dissect 버전.", file=sys.stderr)
            else:
                for shim in func():
                    results.append({
                        "path": getattr(shim, "path", "N/A"),
                        "last_modified": str(getattr(shim, "last_modified", "N/A")),
                        "exec_flag": getattr(shim, "exec_flag", "N/A")
                    })
    except Exception as e:
        print(f"[!] Dissect query error on '{target_path}' artifact '{artifact_type}': {e}", file=sys.stderr)
    finally:
        # Target 정리 (열린 핸들 해제)
        try:
            if target is not None and hasattr(target, "close"):
                target.close()
        except Exception:
            pass

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
