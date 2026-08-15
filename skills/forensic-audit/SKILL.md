---
name: forensic-audit
description: os.stat() 생성/수정/접근 시각과 MD5/SHA-256 해시를 출력한다. $MFT, $SI vs $FN, Maya, MOV mvhd, Timestomping 판정은 하지 않는다.
---

# forensic-audit: OS 표면 타임스탬프와 해시

이 스킬은 `os.stat()`가 보여주는 MAC 시각과 파일 해시만 점검한다.

## 하는 일

- 생성/수정/접근 시각 (로컬 타임존 오프셋 포함)
- SHA-256 (무결성 비교용)
- MD5 (레거시 호환, 단독 증거로 쓰지 말 것)
- 생성시각 > 수정시각이면 **복사/다운로드에서 흔한 현상**으로 기록. 조작 단정 금지.

## 하지 않는 일

- NTFS `$MFT` `$STANDARD_INFORMATION` vs `$FILE_NAME`
- Timestomping 판정
- MOV/MP4 `mvhd`, EXIF, Maya `.mb`, HWP/Office `core.xml`

그런 분석이 필요하면 EnCase, X-Ways, MFTECmd 등 전용 도구를 쓰고, 이 스크립트 결과를 그 대체물로 인용하지 않는다.

## 실행

```bash
python skills/forensic-audit/scripts/audit_timestamps.py "대상파일.ext"
```
