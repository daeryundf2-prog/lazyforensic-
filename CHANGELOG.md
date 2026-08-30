# Changelog

이 레포의 실제 변경을 기록한다. 형식은 Keep a Changelog 를 따르고, 항목은 커밋 해시로 추적한다.

## [Unreleased] — 2026-08-30

### Added — Guard Pack (GUARD_PACK_VERSION 1.0.0) 및 통합 불변식

- `scripts/markdown_structure_guard.mjs` 신설 + `hooks.json` PostToolUse(문서 쓰기·bash 리다이렉트)에 FAIL_CLOSED 배선: 생성 중 스트리핑(빈 링크 `[](`, 빈 불릿 `-  : `, 빈 강조, 고아 `$수식`, 미닫힘 코드펜스, 표 열 불일치)을 쓰기 직후 탐지해 재작성 강제. `--check` 일괄 모드는 CI 단계로도 편입. NTFS 속성명(`$MFT` 등)·인라인 코드 내 `$`는 오탐 제외.
- `test/test_integration_invariants.py` 신설(레포 전체, 7개): (1) 모든 `skills/*/SKILL.md`가 GEMINI.md에 라우팅 등록돼 있는지(예외 목록 명시), (2) GEMINI.md가 참조하는 경로 실존, (3) Forensic 레인 헤더 수-표 행 수 일치, (4) 문서화된 python 명령의 스크립트 실존, (5) 문서화된 CLI 플래그의 스크립트 등록(--plot-fft 사례 재발 방지, 25개 문서화 명령 대상), (6) skills 트리 스트리핑 흔적 0건, (7) GAPS.md 정직 문서 유지.
- CI 개선: `unittest discover` → `pytest`(기존 러너는 함수형 테스트를 수집하지 못해 CI가 절반만 검증하고 있었다), markdown guard CI 단계 추가.
- `scripts/sync_guard_pack.sh` 신설 — 캐노니컬 가드(lazyforensic) → lazyantigravity/lazyothers 동기화.
- 리뷰 발견 즉시 수정: `02`의 `$1/f^\alpha$` 수식 잔존 손상 복원, `skills/lazyforensic/SKILL.md` 표 4행 열 불일치 복원, `ai-trace-detector`가 GEMINI.md/README에 미등록이던 통합 누락 등록(15레인).
- 훅 배선 테스트 강화: markdown guard의 문서 쓰기·bash 양쪽 FAIL_CLOSED 배선까지 검증.

### Added — deepfake-forensic-radar 통합 보강 (335b1c6 후속 정비)

- `GEMINI.md` Forensic 라우팅 테이블에 `deepfake-forensic-radar` 등록(13→14) — 스킬 추가 직후 라우팅 문서가 갱신되지 않아 호스트가 딥페이크 요청을 라우팅하지 못하던 통합 누락 수정
- `README.md` 지원 표에 딥페이크 1차 감사 행 추가
- `test_deepfake_forensic_radar.py` 보강: JPEG APP11/MP4 c2pa 박스 감지, SKILL.md에 문서화된 CLI 플래그 실존 검증(문서-구현 드리프트 가드), 레퍼런스 파일 스트리핑 가드(빈 불릿/빈 링크 텍스트 탐지), GEMINI.md 라우팅 행 존재 검증

### Fixed — deepfake-forensic-radar 레퍼런스·스크립트 결함

- `01_generation_synthesis.md`: ComfyUI 13대 노드의 저장소명이 전부 공란으로 스트리핑된 결함 복원(13개 링크), 원문 누락 모델 14종 보충(Sora, Vidu, SimSwap, Ghost, XTTS-v2, StyleTTS2, Mini-Omni, VoiceCraft, V-Express, AniPortrait, Champ, MimicMotion, AnimateAnyone, LivePortrait-Realtime) 및 가중치 파일명(`inswapper_128.onnx` 등) 복원
- `02_detection_forensics.md`: 누락 탐지기 6종 보충(FreqNet, LGrad, RECCE, SBI, VIGIL, CNNDetection), 벤치마크 데이터셋 9종 섹션 신설, 출처 없는 정량 AUC 그리드(예: DIRE GenImage 97.8%)를 근거 있는 수치(UnivFD 92.3%, NPR 91.4%) + 정성 평가표로 교체 — 근거-결론 분리 원칙 정합화
- `03_c2pa_watermarks.md`: 스트리핑된 필드명(`c2pa.actions`, `c2pa.hash.data`)과 도구 링크 텍스트(c2pa-rs, c2pa-js, stable_signature, tree-ring-watermark) 복원
- `04_legal_and_court.md`: " 타임스탬프" 공란 → 전자소송(ECFS) 이력·파일시스템 타임스탬프 명시
- `05_evasion_and_limits.md`: 메신저 전송 방식 항목의 플랫폼명(Telegram 사진 모드/파일 모드) 복원
- `analyze_deepfake_evidence.py`: SKILL.md에만 문서화되고 구현되지 않았던 `--plot-fft` 플래그 구현(matplotlib 선택 의존, 실패 시 exit 2), 비디오 컨테이너 FFT를 ffmpeg 1프레임 추출로 지원, 항상 0.0이던 죽은 필드 `high_freq_anomaly_score` 제거, "해시 일치 시 법적 증거능력 인정" 과단정 문구를 무결성 확인서 수준으로 교정, MD5/SHA-1 충돌 취약성 주석 추가, 미사용 `math` import 제거

### Fixed — 외부 리뷰 후속 수정 (검증 게이트)

2026-08-30 외부 코드 리뷰(보안 7/10, 종합 7.5/10)에서 확인된 결함 수리. 테스트는 guard pack 추가분과 합산해 최종 96개.

### Fixed — 검증 게이트 (P1)

- `hooks.json` PostToolUse 매처에 `write|edit|apply_patch` 추가 — 호스트 Write/Edit 경로로 수정한 보고서는 검증 게이트를 아예 통과하지 않던 배선 불일치 (PreToolUse와 정렬)
- `verify_report.py`: 보고서에 해시가 있는데 `--evidence`가 없으면 WARN(통과) 대신 **FAIL**로 격상 — '감사 생략 + 조작 해시'라는 핵심 위협이 WARN으로 게이트를 통과하던 구멍. README의 "근거 없는 해시 → FAIL" 주장이 이제 무조건 참

### Fixed — 검증 게이트 (P2)

- `verify_report.py`: 줄바꿈·공백으로 분할된 64hex 해시 검출(표 정렬·하드랩 우회 차단), "오전 9시 30분" 식 한국어 시각 인식(이전은 날짜만 추출해 거짓 시각이 grounding을 통과), 콜론식 시각 병기 유지
- `generate_timeline.py` UTF-8 stdio 누락 보강 — e3fa4e6("all CLI scripts")에서 이 스크립트만 빠져 있었다
- evidence_guard: 읽기전용 검사 명령(sha256sum/파서 실행 등)의 증거 '읽기' 허용 — 가드가 evidence/ 관례를 권하면서 감사 워크플로 자체를 막던 모순 해소. 쓰기 신호(리다이렉트·cp·mv·tee·dd·sed -i)와 `python -c` 인라인 코드는 여전히 차단
- evidence_guard 보호 확장자에 .mem/.vmem/.img/.l01/.ad1/.aff/.aff4/.vmdk/.vhd 추가


## [1.0.1] — 2026-08-29

2026-08 종합 리뷰(문서·정직성 9/10, korean-law-mcp 8/10, 스킬 6/10, 스크립트·훅 4/10, 패키징 3/10)에서 발견된 결함을 수리한 시리즈. 리뷰에서 "치명적"으로 분류된 5가지가 모두 해소됐다.

### Fixed — 검증 체인 (플래그십)

- `audit_timestamps.py --json` 플래그 추가 — 문서화된 체인(`--json > audit.json` → `verify_report.py --evidence`)이 처음으로 실제로 순환한다 (422679c)
- `verify_report.py`: UTF-16/CP949 자동 감지(PowerShell Out-File 입력 포함), 금지문구 부정 문맥 허용("유출의심 아님" 오탐 제거), 라벨 붙은 MD5/SHA-1 grounding, 한국식 날짜 형식 인식, 타임라인 검사 전역→줄 단위, `제X조` 인용 추출 경고 (7db94f5)
- 검증 게이트가 `.lazyforensic/audit_trail.jsonl`(이 플러그인 자신의 감사 로그)을 근거 파일로 조회 — 두 파이프라인 연결 (7db94f5)

### Fixed — 훅 배관 (Linux/Windows 에서 FAIL_CLOSED 가 죽어 있던 문제)

- stdin JSON을 `fstatSync().size` 판정 대신 1.5초 데드라인 비동기 읽기로 교체 — POSIX 파이프에서 size가 항상 0이어 두 가드 모두 아무것도 검사하지 않던 치명 버그 (7db94f5)
- 경로 추출을 `\S` 기반으로 — ASCII `\w` 정규식이 한글/공백 파일명을 놓쳐 한글 보고서가 검증을 스킵하던 문제 (7db94f5)
- JSON 소스 독립 파싱, `\/` 이스케이프 우회 차단, `py -3`/`python`/`python3` 탐색 + Windows Store 별칭 오탐 배제, exit 규약 문서화 (7db94f5)
- evidence_guard: 보고서 본문(content) 스캔 제거로 과차단 해소, `cp x evidence/` 상대 경로 차단 추가, 감사 로그 이중 미러 폐지, 2GiB 초과는 `sha256: null` 명시 기록, 스트리밍 해시 (7db94f5)
- hooks.json PostToolUse에 bash 매처 추가 — `python gen.py > 보고서.md` 우회 경로도 동일 게이트 (7db94f5)

### Fixed — 포렌식 데이터 경로

- `parse_kakao.py` 재작성: 실제 PC "대화내용 저장" 포맷(`===` 헤더 + `[오후 2:15] 닉네임 : 메시지`) 지원 — 구버전은 합성 포맷만 읽어 실제 PC 내보내기가 0건으로 파싱됨. 첨부 판정을 확정 표기 전용으로("사진 좀 보내줘"가 `has_attachment:true`로 위장하던 결함), 시스템 이벤트/인식 불가 행을 `type` 레코드로 보존, CP949 지원, 콜론 포함 발신자 분할 수정 (422679c)
- `parse_ntfs_artifacts.py`: 파싱 실패가 "레코드 0건 + exit 0"으로 위장하던 결함 → `error` 필드 + exit 3, stdout JSON 전용화 (422679c)
- `generate_timeline.py`: 에러 메시지에만 존재하던 `--max-events` 플래그 실제 추가 (422679c)
- `download_dfir_binaries.ps1`: 중첩 폴더로 인한 무한 재다운로드 수정, 자산 미매칭 무음→경고 (422679c)
- `kakao-db-decryptor` SQL 예시 epoch 밀리초(`/1000`) 수정, `forensic_video_audit.py` POSIX ctime 라벨 수정, 감정서 템플릿에 Chain of Custody 섹션 추가 (422679c)
- 영상 스킬 `setup.py --check`가 무출력으로 exit 2 하던 UX 결함 — 리포트+설치 명령 출력 후 종료 코드 반환 (34fb062)

### Fixed — Windows 전반

- 한국어 출력 스크립트 전반이 cp1252/cp949 콘솔에서 `UnicodeEncodeError`로 크래시 — CI windows-latest에서 실제 발견, `sys.stdout/stderr.reconfigure(utf-8)`을 CLI 전체에 적용 (e3fa4e6)

### Added

- `scripts/check_tool.py` BYO 게이트 — 스킬 3종(EVTX/MFT/Memory)이 명령 생성 전 도구 존재를 실행으로 확인 (422679c)
- `parse_kakao.py --events-out` — 파싱→타임라인 수동 변환 단계 제거. 시각 미상·unparsed 레코드는 근거 없는 시각이므로 의도적으로 제외 (c898df2)
- GitHub Actions CI — Ubuntu/Windows 유닛 테스트 + stdin 파이프 가드 단언, 노드 문법 체크, korean-law-mcp 빌드+vitest (3a0c0b6)
- 테스트 35 → 79개: 두 가드의 첫 직접 회귀 테스트(test_guards.py), 실제 PC 포맷/CP949/첨부 오음성/검증 체인 E2E/Windows 인코딩 (7db94f5, 422679c, e3fa4e6, c898df2)

### Removed — 라이선스 미검증 제3자 트리 (b3f08d8)

배포 라이선스 검증을 끝내지 못해 다음을 제거했다. 상세 사유는 `NOTICE`.

- `mengto-skills/` (90MB, 127 스킬 — 라이선스 파일 전무)
- `design-systems/` (74 브랜드 토큰 — 제3자 상표·전용 폰트)
- `vendor/antv-infographic/` (파생 참고 문서 — 라이선스 파일 없음)
- `skills/slopslap/` (upstream `private:true`, 무라이선스)
- 의존 UI 피커 스킬 3종(`ui-studio`, `design-system`, `frontend-ui-ux`) + 카탈로그 인덱서
- korean-law-mcp 잔여물: 4.3MB demo.gif, upstream 세션 노트, `npx` 설치를 광고하던 낡은 `.claude-plugin/`

HTML 뷰어 스타일링은 인라인 CSS로 직접 작성하는 것으로 대체했다.

### Docs

- README 사용자 관점 재작성 — 요구사항/설치 2경로/법령 MCP 셋업(법제처 키 발급, 680MB 빌드)/복붙 검증된 4단계 워크플로/지원-미지원 표/트러블슈팅 (34fb062)
- `GEMINI.md`·`docs/GAPS.md`: "무조건 검증"을 사후 게이트로 정직 서술, 스킵 경로 기록, 스킬 카운트 정정 (b3f08d8)

## [1.0.0] — 2026-08 이전

초기 공개: Antigravity + Gemini용 포렌식 보조 플러그인 4 lanes(help/forensic/visual/legal), korean-law-mcp 번들.
