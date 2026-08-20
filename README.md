# LazyForensic (v1.0.0)

Google Antigravity + **Gemini 3.7 Flash** 용 실전형 **디지털 포렌식 및 침해사고 대응(DFIR)** 플러그인.

## 🚀 주요 기능 및 스킬

### 1. 침해사고 & 이벤트 로그 (EVTX)
*   **`dfir-evtx-hunter`**: Rust 기반 **Hayabusa** 및 **Chainsaw**를 연동하여 4,000+ Sigma 룰 기반으로 이벤트 로그를 5초 이내에 스캔하고 MITRE ATT&CK 타임라인 생성.

### 2. 파일시스템 & 아티팩트 (NTFS / MFT / Prefetch)
*   **`forensic-mft-parser`**: **Dissect** 및 **EZ-Tools (MFTECmd, PECmd)**를 통해 `$MFT`, `$LogFile`, Prefetch, Shimcache를 분석하여 삭제 파일 및 실행 이력 복원.
*   **`forensic-audit`**: 파일 타임스탬프(MACB) 및 SHA-256/MD5 무결성 검증.

### 3. 메신저 & 모바일 DB 포렌식
*   **`kakao-db-decryptor`**: Android/PC 암호화 카카오톡 SQLite DB(`KakaoTalk.db` / `EvaSQLite`) 복호화 및 대화 내역 추출.
*   **`kakao-chat-extractor`**: 모바일/PC 텍스트 내보내기(.txt) 파싱.

### 4. 메모리 포렌식 (RAM Triage)
*   **`memory-triage`**: **MemProcFS** 및 **Volatility 3**를 연동하여 가상 드라이브 마운트 및 은닉 프로세스, 코드 인젝션, 네트워크 소켓 분석.

### 5. 증거 무결성 보호 훅 (Lifecycle Hooks)
*   `PreToolUse` (Evidence Write-Lock): 원본 증거 파일(`*.raw`, `*.evtx`, `*.E01`) 수정 시도 원천 차단.
*   `PostToolUse` (SHA-256 Audit Log): 산출물 생성 시 해시 체크포인트를 `audit_trail.jsonl`에 자동 기록.

---

## 🛠️ 빠른 시작

```powershell
# 1. DFIR 외부 바이너리(Hayabusa, Chainsaw, EZ-Tools) 자동 설치
powershell -ExecutionPolicy Bypass -File scripts/download_dfir_binaries.ps1

# 2. EVTX 위협 헌팅
hayabusa.exe csv-timeline -d "C:\Evidence\Logs" -o "C:\Output\timeline.csv"

# 3. Dissect로 디스크 이미지 아티팩트 파싱
python scripts/parse_ntfs_artifacts.py "disk.raw" --artifact prefetch --output prefetch.json
```
