---
name: dfir-evtx-hunter
description: "Hayabusa 및 Chainsaw를 활용한 윈도우 이벤트 로그(EVTX) 초고속 Sigma 룰 기반 위협 사냥 및 타임라인 생성 스킬. Triggers: evtx 분석, 이벤트로그, hayabusa, chainsaw, sigma 룰, 침해사고 조사, 계정 탈취."
---

# DFIR EVTX Threat Hunter (Hayabusa & Chainsaw)

Rust 기반의 네이티브 초고속 위협 사냥 엔진인 **Hayabusa**와 **Chainsaw**를 구동하여, 대용량 Windows Event Logs (`.evtx`)에서 악성 행위, 자격 증명 탈취(Mimikatz), 측면 이동(Lateral Movement), 권한 상승을 5초 이내에 탐지하고 MITRE ATT&CK 타임라인을 생성합니다.

## 핵심 도구

1. **Hayabusa 타임라인 & 메트릭:**
   ```powershell
   # 1. EVTX 디렉터리 전체 스캔 및 CSV 타임라인 생성
   hayabusa.exe csv-timeline -d "C:\Evidence\Logs" -o "C:\Output\evtx_timeline.csv" --profile standard --min-level medium

   # 2. 호스트 요약 메트릭 및 컴퓨터 정보 추출
   hayabusa.exe computer-metrics -d "C:\Evidence\Logs"
   ```

2. **Chainsaw 정밀 키워드/IOC 헌팅:**
   ```powershell
   # 특정 키워드/IP/해시 고속 탐색
   chainsaw.exe search "mimikatz" "C:\Evidence\Logs" --json
   ```

## 필수 준비
- 도구 부재 시: `powershell -ExecutionPolicy Bypass -File scripts/download_dfir_binaries.ps1` 실행으로 최신 바이너리 설치.
