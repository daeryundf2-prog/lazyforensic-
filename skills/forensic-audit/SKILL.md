---
name: forensic-audit
description: 파일 시스템($MFT, $SI vs $FN), 미디어(MOV, MP4, EXIF), 3D 모델(Maya .mb) 등의 메타데이터 및 생성시간 vs 수정시간 역전, Timestomping, 속성 조작 가능성을 과학수사 기법으로 정밀 감정하는 포렌식 감사 스킬.
---

# forensic-audit: 디지털 파일 타임스탬프 & 위변조 정밀 감정

이 스킬은 파일의 타임스탬프 불일치, 생성일시 > 수정일시 역전 현상, NTFS `$MFT` 아티팩트 및 내부 메타데이터를 분석하여 **파일 위변조, 조작 가능성, 작성 일시의 진위**를 과학적으로 감정합니다.

## 🎯 주요 실행 시나리오 (Triggers)
- "만든 날짜가 수정한 날짜보다 앞선 게 당연한가요?", "생성시간보다 수정시간이 빠를 수 있나?"
- "작성일시 조작 가능성 분석", "메타데이터 위변조 감정"
- "Maya .mb 파일 작성일시 분석", "동영상(.mov/.mp4) 촬영 일시 조작 여부 감정"
- "$MFT $SI vs $FN 불일치 분석", "Timestomping 여부 판별"

---

## 🔬 타임스탬프 과학수사 감정 원리 (Forensic Principles)

### 1. 생성시간(Created) > 수정시간(Modified) 역전 메커니즘
* **정상 시나리오 (파일 복사/이동/다운로드)**:
  - 파일이 다른 PC, 외장 드라이브, 인터넷(웹/메신저)에서 현재 PC로 **복사(Copy)되거나 다운로드**될 때, 파일 시스템은 **생성일자(Created Date)를 '현재 복사/다운로드된 시점'**으로 새로 부여합니다.
  - 반면, **수정일자(Modified Date)는 '원본 파일이 마지막으로 편집·저장된 시점'**을 그대로 보존합니다.
  - 따라서 **[생성시간이 수정시간보다 미래(최신)]인 현상은 파일 복사/이동 시 지극히 정상적인 포렌식 현상**입니다.
* **비정상/조작 시나리오 (Timestomping)**:
  - 전용 속성 변조 도구(Attribute Changer, NewFileTime 등)를 사용해 `$STANDARD_INFORMATION`의 타임스탬프만 인위적으로 과거 시점으로 되돌린 경우, `$FILE_NAME` 속성의 타임스탬프와 불일치가 발생합니다.

### 2. 미디어 및 전용 포맷 내부 메타데이터 교차 검증
* **QuickTime / MP4 (MOV, MP4)**:
  - 컨테이너 헤더의 `mvhd` (Movie Header Atom), `tkhd` (Track Header Atom) 내 Creation Time (UTC 기준) 추출.
* **Maya 3D 바이너리 (.mb / .ma)**:
  - 파일 헤더/푸터에 기록된 Maya Application Version, Last Saved Timestamp, User Machine Name 파싱.
* **아래아한글 (.hwp / .hwpx)** & **오피스 (.docx / .xlsx)**:
  - `DocInfo` 스트림 / `core.xml` 내부의 `dcterms:created`, `dcterms:modified`, `cp:lastModifiedBy` 추출.

---

## 📋 감정 의견서 표준 양식 도출 (Expert Opinion)

감정 요청 시 다음 4개 항목을 필히 포함하여 답변합니다:
1. **분석 대상 및 추출된 타임스탬프 명세표** (파일시스템 vs 메타데이터 비교)
2. **기술적 발생 원인 분석** (단순 파일 이동/복사인지, 인위적 변조 흔적인지)
3. **위변조 가능성에 대한 최종 감정의견** (법원 제출용 신뢰성 높은 결론 문장)
4. **추가 입증을 위한 보완 수집 권고** ($MFT, USN Journal, LNK, JumpList, Event Log 등)
