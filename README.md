# LazyForensic (v1.0.0)

Google Antigravity + **Gemini 3.7 Flash** 용 포렌식 **보조** 플러그인 — 4 lanes (help/forensic/visual/legal). **Not a forensic acquisition or court-admissibility suite.** 증거 정리·텍스트 파싱·타임라인 렌더·보고서 초안에 집중하며, 획득/검증은 별도 검증된 도구로 수행해야 한다.

> **한계**: `docs/GAPS.md`와 `GEMINI.md`의 “하지 않는 일”을 먼저 읽는다. EVTX/MFT/Memory는 **bring-your-own-binary 래퍼**이며 바이너리 미포함. 카카오톡은 **텍스트 내보내기만** 지원.

## 🚀 주요 기능 및 스킬 (정직 표기)

### 1. 침해사고 & 이벤트 로그 (EVTX) — 래퍼
*   **`dfir-evtx-hunter`**: Hayabusa/Chainsaw **래퍼** (BYO binary). 4000+ Sigma 룰은 Hayabusa가 있을 때만. 자동 탐지·MITRE 확정 아님.

### 2. 파일시스템 & 아티팩트
*   **`forensic-mft-parser`**: Dissect/EZ-Tools **래퍼** (BYO binary). `$MFT`/`Prefetch`/`Shimcache`는 도구 있을 때만. 실패 시 빈 결과.
*   **`forensic-audit`**: `os.stat()` 표면 타임스탬프 + SHA-256/MD5. `$MFT`/`Timestomping` 판단 아님.

### 3. 메신저
*   **`kakao-db-decryptor`**: **제한적 래퍼** — SQLite 복호화 미제공. `kakao-chat-extractor`가 **텍스트 내보내기(.txt)만** 파싱.
*   **`kakao-chat-extractor`**: 모바일/PC 텍스트 내보내기 파싱 (UTF-8/UTF-16, 첨부 탐지).

### 4. 메모리 포렌식 — 래퍼
*   **`memory-triage`**: MemProcFS/Volatility 3 **래퍼** (BYO binary). 마운트/은닉 프로세스 자동 분석 아님.

### 5. 증거 무결성 보호 훅 (best-effort)
*   `PreToolUse` (Evidence Write-Lock, best-effort): `*.raw`/`*.evtx`/`*.E01`/`evidence/` 쓰기 시도 차단 시도. OS 읽기전용(`chmod 444`) 병행 필요.
*   `PostToolUse` (SHA-256 Audit Log): 산출물 해시 체크포인트를 `.lazyforensic/audit_trail.jsonl`에 기록. Chain-of-Custody 증명 아님.

---

## 🛠️ 빠른 시작

```powershell
# 1. DFIR 외부 바이너리(Hayabusa, Chainsaw, EZ-Tools) 별도 설치 — 선택, 미포함
powershell -ExecutionPolicy Bypass -File scripts/download_dfir_binaries.ps1
# 다운로드 후 SHA256 직접 검증 필요

# 2. EVTX 위협 헌팅 — hayabusa.exe가 있을 때만
hayabusa.exe csv-timeline -d "C:\Evidence\Logs" -o "C:\Output\timeline.csv"

# 3. Dissect 래퍼 — dissect 설치 시 (pip install dissect)
python scripts/parse_ntfs_artifacts.py "disk.raw" --artifact prefetch --output prefetch.json

# 4. 카카오 텍스트 내보내기 & 타임라인
python skills/kakao-chat-extractor/scripts/parse_kakao.py "카카오톡_대화.txt" --output parsed.json
python skills/forensic-timeline/scripts/generate_timeline.py --input events.json --output timeline.html
```
