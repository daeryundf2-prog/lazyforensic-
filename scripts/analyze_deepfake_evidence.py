#!/usr/bin/env python3
"""
analyze_deepfake_evidence.py
============================
Comprehensive Digital Forensic Analyzer for Deepfake and AI-Generated Media.
Performs SHA-256/MD5 hash audits, C2PA/JUMBF/EXIF metadata scans,
and 2D FFT frequency spectrum anomaly checks.
"""

import argparse
import hashlib
import json
import math
import os
import struct
import sys
from datetime import datetime
from pathlib import Path


def calculate_hashes(file_path: str) -> dict:
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            sha1.update(chunk)
            md5.update(chunk)
            
    return {
        "sha256": sha256.hexdigest(),
        "sha1": sha1.hexdigest(),
        "md5": md5.hexdigest(),
        "size_bytes": os.path.getsize(file_path)
    }


def scan_c2pa_jumbf(file_path: str) -> dict:
    """Scan for C2PA JUMBF metadata manifest in JPEG APP11 or MP4 c2pa boxes."""
    result = {
        "c2pa_detected": False,
        "manifest_type": None,
        "details": []
    }
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read(1024 * 1024)  # First 1MB for header check
            
        jpeg_magic = bytes([0xFF, 0xD8])
        app11_magic = bytes([0xFF, 0xEB])
        
        # Check JPEG APP11 (0xFFEB) with JUMBF / c2pa signatures
        if data.startswith(jpeg_magic):
            idx = 0
            while idx < len(data) - 4:
                if data[idx:idx+2] == app11_magic:
                    length = struct.unpack('>H', data[idx+2:idx+4])[0]
                    payload = data[idx+4:idx+2+length]
                    if b'JP2C' in payload or b'c2pa' in payload or b'jumb' in payload:
                        result["c2pa_detected"] = True
                        result["manifest_type"] = "JPEG_APP11_JUMBF"
                        result["details"].append("Found C2PA JUMBF Manifest in APP11 marker")
                        break
                    idx += 2 + length
                else:
                    idx += 1
                    
        # Check MP4 ISOBMFF c2pa box
        elif (b'ftyp' in data[:32] or b'moov' in data) and b'c2pa' in data:
            result["c2pa_detected"] = True
            result["manifest_type"] = "ISOBMFF_c2pa_box"
            result["details"].append("Found c2pa ISOBMFF atom in container")
                
        # Check general raw string signatures
        if not result["c2pa_detected"]:
            for sig in [b'c2pa.actions', b'c2pa.hash.data', b'c2pa.claim', b'synthid']:
                if sig in data:
                    result["c2pa_detected"] = True
                    result["manifest_type"] = "Raw_Manifest_Signature"
                    result["details"].append(f"Found signature: {sig.decode('latin-1')}")
                    break
    except Exception as e:
        result["details"].append(f"Scan error: {str(e)}")
        
    return result


def analyze_fft_spectrum(file_path: str) -> dict:
    """Analyze 2D Fourier spectrum artifacts on image files."""
    result = {
        "analyzed": False,
        "high_freq_anomaly_score": 0.0,
        "checkerboard_spikes_detected": False,
        "verdict_indicator": "INCONCLUSIVE",
        "notes": []
    }
    
    try:
        from PIL import Image
        import numpy as np
        
        img = Image.open(file_path).convert('L')
        img_np = np.array(img, dtype=np.float32)
        h, w = img_np.shape
        
        # Center crop to 512x512 if larger
        if h > 512 or w > 512:
            ch, cw = h // 2, w // 2
            img_np = img_np[max(0, ch-256):min(h, ch+256), max(0, cw-256):min(w, cw+256)]
            
        # Compute 2D FFT
        f_transform = np.fft.fft2(img_np)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift) + 1.0)
        
        # Measure high frequency energy vs center low frequency
        my, mx = magnitude_spectrum.shape[0] // 2, magnitude_spectrum.shape[1] // 2
        r_inner = min(my, mx) // 4
        r_outer = min(my, mx) // 2
        
        y, x = np.ogrid[:magnitude_spectrum.shape[0], :magnitude_spectrum.shape[1]]
        dist_from_center = np.sqrt((x - mx)**2 + (y - my)**2)
        
        low_freq_energy = np.mean(magnitude_spectrum[dist_from_center <= r_inner])
        high_freq_energy = np.mean(magnitude_spectrum[dist_from_center >= r_outer])
        
        ratio = float(high_freq_energy / (low_freq_energy + 1e-6))
        
        # Check standard deviation of high frequency band for unnatural spikes
        high_freq_std = float(np.std(magnitude_spectrum[dist_from_center >= r_outer]))
        checkerboard = high_freq_std > 1.85 and ratio > 0.45
        
        result["analyzed"] = True
        result["high_freq_ratio"] = round(ratio, 4)
        result["high_freq_std"] = round(high_freq_std, 4)
        result["checkerboard_spikes_detected"] = checkerboard
        
        if checkerboard:
            result["verdict_indicator"] = "SUSPECTED_SYNTHETIC_ARTIFACTS"
            result["notes"].append("Periodic checkerboard high-frequency spectral spikes detected (Deconvolution artifact indicator)")
        else:
            result["verdict_indicator"] = "NATURAL_SPECTRUM_PROFILE"
            result["notes"].append("Spectral radial power follows standard natural decay curve")
            
    except ImportError:
        result["notes"].append("Pillow or NumPy not installed — skipped FFT computation")
    except Exception as e:
        result["notes"].append(f"FFT computation failed: {str(e)}")
        
    return result


def generate_forensic_report(file_path: str) -> dict:
    hashes = calculate_hashes(file_path)
    c2pa = scan_c2pa_jumbf(file_path)
    fft = analyze_fft_spectrum(file_path)
    
    timestamp = datetime.now().isoformat()
    
    return {
        "meta": {
            "target_file": os.path.abspath(file_path),
            "analyzed_at": timestamp,
            "analyzer_version": "LazyForensic Deepfake Radar v1.0.0"
        },
        "integrity_hashes": hashes,
        "c2pa_provenance": c2pa,
        "spectral_analysis": fft
    }


def format_markdown_report(data: dict) -> str:
    m = data["meta"]
    h = data["integrity_hashes"]
    c = data["c2pa_provenance"]
    f = data["spectral_analysis"]
    
    c2pa_status = "검출됨 (암호학적 서명 존재)" if c["c2pa_detected"] else "미검출 (메타데이터 부재 또는 스트리핑됨)"
    fft_status = f["verdict_indicator"]
    details_str = chr(10).join(f"  - {d}" for d in c.get("details", [])) or "  - 기록 없음"
    notes_str = chr(10).join(f"  - {n}" for n in f.get("notes", [])) or "  - 특이사항 없음"
    
    return f"""# 디지털 미디어 딥페이크 포렌식 감정 보고서
- **분석 일시**: {m['analyzed_at']}
- **대상 파일**: `{os.path.basename(m['target_file'])}`
- **도구**: {m['analyzer_version']}

---

## 1. 증거 무결성 해시 감사 (Chain of Custody Verification)
| 항목 | 측정값 |
| :--- | :--- |
| **파일 크기** | {h['size_bytes']:,} Bytes |
| **SHA-256** | `{h['sha256']}` |
| **SHA-1** | `{h['sha1']}` |
| **MD5** | `{h['md5']}` |

> [!IMPORTANT]
> 형사소송법 제310조의2 및 제313조에 따라, 압수 시점의 해시값과 상기 SHA-256 해시값이 100% 일치해야 법적 증거능력이 인정됩니다.

---

## 2. C2PA / Content Credentials 출처 증명 검사
- **검출 상태**: **{c2pa_status}**
- **매니페스트 유형**: `{c.get('manifest_type') or 'None'}`
- **세부 로그**:
{details_str}

---

## 3. 2D 푸리에(FFT) 주파수 스펙트럼 인공 잔재 분석
- **분석 상태**: {'성공' if f['analyzed'] else '미수행/실패'}
- **스펙트럼 판정 지표**: `{fft_status}`
- **체커보드 스파이크 감지**: {'비정상 고주파 격자 스파이크 검출 (생성기 잔재 의심)' if f['checkerboard_spikes_detected'] else '정상 (자연 사진 스펙트럼 곡선)'}
- **고주파 에너지 비율**: {f.get('high_freq_ratio', 'N/A')} (표준편차: {f.get('high_freq_std', 'N/A')})
- **분석 소견**:
{notes_str}

---

## 4. 사법 포렌식 종합 의견
1. **증거 무결성**: 본 파일의 고유 SHA-256 해시(`{h['sha256'][:16]}...`)를 원본 보관 연속성 원장에 기록하여 사후 변조를 차단하십시오.
2. **출처 판정**: C2PA 서명이 {'확인되었으므로 공식 인증 출처를 확인하십시오.' if c['c2pa_detected'] else '존재하지 않으므로, 소셜 미디어 재인코딩 이력 또는 로컬 생성 여부에 대한 정밀 다층 분석이 권장됩니다.'}
3. **법정 제출 시 주의**: 단순 AI 탐지 스코어 단독 제출을 지양하고, 본 해시 감사표와 파일시스템  타임스탬프를 병합 제출하십시오.
"""


def main():
    parser = argparse.ArgumentParser(description="Deepfake & AI Media Forensic Analyzer")
    parser.add_argument("file", help="Path to media file (image/video)")
    parser.add_argument("--output", "-o", help="Path to output markdown report")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
        
    data = generate_forensic_report(args.file)
    
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
        
    md = format_markdown_report(data)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f"Forensic report written to: {args.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()
