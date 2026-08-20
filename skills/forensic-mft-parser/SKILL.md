---
name: forensic-mft-parser
description: "MFTECmd 및 Dissect를 활용한 NTFS $MFT, $LogFile, Prefetch, Shimcache 파싱 및 삭제/실행 파일 추적 스킬. Triggers: mft 분석, prefetch 분석, mftecmd, pecmd, dissect, ntfs 분석, 삭제 파일 흔적."
---

# Forensic MFT & Execution Artifact Parser

NTFS 파일시스템의 핵심 구조인 `$MFT`, `$UsnJrnl:$J`, `$LogFile`과 프로그램 실행 아티팩트(`Prefetch`, `Amcache`, `Shimcache`)를 분석하여 파일 생성/삭제/이동 이력 및 악성코드 실행 시간을 정밀 복원합니다.

## 핵심 도구

1. **Dissect Python 아티팩트 파서 (무설치/순수 Python):**
   ```bash
   # Prefetch 실행 흔적 추출
   python scripts/parse_ntfs_artifacts.py "disk.raw" --artifact prefetch --output prefetch.json

   # 사용자 계정 및 Shimcache 추출
   python scripts/parse_ntfs_artifacts.py "disk.raw" --artifact shimcache --output shimcache.json
   ```

2. **Eric Zimmerman Tools (EZ Tools):**
   ```powershell
   # 1. $MFT 파싱
   MFTECmd.exe -f "C:\Evidence\C\`$MFT" --csv "C:\Output\MFT" --csvf mft_parsed.csv

   # 2. Prefetch 파싱 (실행 횟수, 마지막 실행 시각, 참조된 DLL 목록)
   PECmd.exe -d "C:\Evidence\C\Windows\Prefetch" --csv "C:\Output\Prefetch"
   ```
