# 구현하지 않은 능력 (v1.0.1 정직 선언)

이 목록은 광고와 구현의 차이를 고정한다. `plugin.json`/`README.md`는 이 문서를 따른다.
v1.0.1: 검증 체인·훅 배관·카카오 파서의 결함을 수리하고, 무라이선스 제3자 트리를 제거했다.

## DLP

`dlp-leakage-detector`는 분석관이 이미 확보한 로그를 맞추는 체크리스트다. 자동 유출 탐지 엔진이 없다.

다음 패스 후보: 사용자가 준 CSV를 표로 옮기는 보조(탐지 아님).

## 카카오톡

`kakao-chat-extractor`는 모바일/PC **텍스트 내보내기**만 읽는다. SQLite `chat_logs`나 백업 DB 파서는 없다.
`kakao-db-decryptor`는 **래퍼**이며 `kakaodecrypt.py` 없음, SQLCipher 복호화 미제공. 별도 도구 필요.
PC 파서는 실제 "대화내용 저장" 포맷(`===` 헤더 + `[오후 2:15] 닉네임 : 메시지`)과 레거시 합성 포맷을 읽는다.
첨부 판정은 확정 표기(사진/동영상/`파일:`/`파일 전송`)뿐이다. 시스템 이벤트와 인식 불가 행은 `type` 필드로 보존된다.

## 파일시스템 고급 분석

`$MFT`, `$SI` vs `$FN`, Timestomping 판정, Maya, MOV `mvhd`는 없다. `forensic-audit`는 `os.stat`과 해시만 본다.
`forensic-mft-parser`/`dfir-evtx-hunter`/`memory-triage`는 **bring-your-own-binary 래퍼**다. Dissect/Hayabusa/Chainsaw/MemProcFS/Volatility 바이너리는 미포함, 미설치 시 결과 생성 안 함 — 스킬은 명령 생성 전 `scripts/check_tool.py` 게이트를 실행하도록 지시한다(글이 아닌 메커니즘).
`parse_ntfs_artifacts.py`는 실패 시 `error` 필드 + exit 3으로 끝난다. "레코드 0건"과 파싱 실패를 혼동하지 말 것.
`scripts/download_dfir_binaries.ps1`은 별도 다운로드 래퍼이며 SHA256 검증은 수동이다(`-VerifyHash`는 계산만 수행).

## 검증 게이트 (verify_report / hallucination_guard)

`verify_report.py`의 해시 grounding은 **파일 단위 집합 비교**다. 해시 A를 파일 B 서술에 붙이는 결합 오류는 잡지 못한다.
법령 조문은 korean_law MCP 응답과의 자동 대조가 불가능하다. 출처 표기 없는 조문 인용은 WARN일 뿐, 조문 텍스트 진위는 검증하지 않는다.
`hallucination_guard.mjs`는 **PostToolUse 사후 게이트**다 — 파일이 이미 쓰인 뒤 검사하며, 실제 차단은 호스트가 `failurePolicy: FAIL_CLOSED`(exit 1)을 지원할 때 작동한다. exit 코드 규약: 차단 1, 통과 0, 검증 불가(보고서 미발견) 0+경고, python 전무 0+설치 안내(FAIL_OPEN).
python이 아예 없는 Windows에서는 검증 자체가 불가능해 경고 후 통과한다 — 이 경우 게이트는 사실상 비활성이다.

## 증거 무결성 Hook

`evidence_guard.mjs`는 **best-effort 가드**다. stdin JSON(1.5초 데드라인) + 환경변수 + CLI 인자의 경로/명령 **필드만** 검사하며, 호스트가 stdin을 주지 않거나, 매처 밖의 도구를 쓰거나, 직접 `python open(..., 'w')` 등 호스트 미후킹 경로로 쓰면 우회된다. OS 수준 읽기전용(`chmod 444`)을 대체하지 않는다.
보고서 본문(content)은 검사하지 않는다 — 본문 언급만으로 쓰기가 막히는 과차단을 막기 위함이다.
PostToolUse 감사 로그는 `<cwd>/.lazyforensic/audit_trail.jsonl` 단일 파일이다. 해시가 `null`이면 2GiB 초과로 의도적으로 건너뛴 것이다(부재≠실패).

## 제거된 제3자 트리 (라이선스)

무라이선스 제3자 콘텐츠 — `mengto-skills/`(Meng To/DesignCode 카탈로그), `design-systems/`(VoltAgent 브랜드 카탈로그, 제3자 상표), `vendor/antv-infographic/`, `skills/slopslap/`(upstream private), 그리고 이들에 의존하던 UI 피커 스킬(`ui-studio`, `design-system`, `frontend-ui-ux`) — 은 배포 라이선스 검증을 끝내지 못해 **제거**했다. `NOTICE` 참고. HTML 뷰어 스타일은 인라인 CSS로 직접 작성한다. 필요하면 권리를 확보해 별도 옵션 팩으로 재도입한다.

## 법령 MCP

소스는 `korean-law-mcp/`에 있다. 빌드와 `LAW_OC`가 없으면 조회하지 않는다. 법률 자문 엔진이 아니다. 이 레포에서 `fly deploy`를 하지 않는다.

## Manim

`video-editor/manim-video/REFERENCE.md`는 참고 문서다. 교육 영상 렌더 파이프라인이 아니다.
