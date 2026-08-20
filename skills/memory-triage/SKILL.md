---
name: memory-triage
description: "MemProcFS 및 Volatility 3를 활용한 휘발성 메모리(RAM) 덤프 분석, 프로세스 은닉/인젝션/소켓 연결 추적 스킬. Triggers: 메모리 포렌식, ram 덤프, memprocfs, volatility, 프로세스 인젝션, 악성코드 메모리 분석."
---

# Volatile Memory Triage (MemProcFS & Volatility 3)

물리 메모리 덤프(`.raw`, `.dmp`, `.vmem`)에서 실행 중이던 은닉 프로세스, 네트워크 연결, 메모리 인젝션(Hollowing/Reflective DLL), 레지스트리 하이브를 분석합니다.

## 핵심 도구

1. **MemProcFS (가상 드라이브 마운트):**
   ```powershell
   # 메모리 덤프를 M:\ 드라이브로 마운트하고 자동 포렌식 분석 실행
   MemProcFS.exe -device "C:\Evidence\memory.raw" -mount M: -forensic 1
   ```
   - `M:\sys\proc\`: 프로세스별 가상 메모리 및 로드된 DLL
   - `M:\sys\net\`: 연결 소켓 및 IP/Port
   - `M:\forensic\csv\`: 자동 추출된 타임라인 및 YARA 탐지 결과

2. **Volatility 3 (심층 플러그인 분석):**
   ```powershell
   vol.py -f memory.raw windows.pslist
   vol.py -f memory.raw windows.malfind
   vol.py -f memory.raw windows.netscan
   ```
