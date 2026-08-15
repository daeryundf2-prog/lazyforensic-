---
name: forensic-timeline
description: JSON 이벤트 목록을 인터랙티브 HTML 타임라인으로 렌더링한다. $MFT, 이벤트 로그, 메신저를 직접 수집하지 않는다. --input 이 없으면 종료한다.
---

# forensic-timeline: JSON → HTML 타임라인

이 스킬은 **이미 정규화된 이벤트 JSON**을 HTML로 시각화한다.  
PC 아티팩트, `$MFT`, 이벤트 로그, DLP를 자동 수집하거나 합성하지 않는다.

## 입력 스키마

JSON 배열. 각 객체:

- `timestamp` (문자열, 그대로 표시. 타임존 변환 없음)
- `category`: `critical` | `file` | `web` | `chat` | `system`
- `description`
- `details` (선택)

`--input` 없이 실행하면 종료 코드 2. 샘플 USB/카카오 유출 사건을 만들지 않는다.

## 실행

```bash
python skills/forensic-timeline/scripts/generate_timeline.py --input events.json --output timeline.html --title "사건 타임라인"
```

## 한계

- HTML 출력은 입력 JSON의 시각화일 뿐이다.
- XSS 방지를 위해 필드 값을 escape 한다.
- 법원 제출 적격성, 무결성, 원본 아티팩트 대체 주장을 하지 않는다.
