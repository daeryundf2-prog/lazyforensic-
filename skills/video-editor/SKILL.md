---
name: video-editor
description: CCTV, 블랙박스, 동영상 증거물의 구간 발췌(Trim), 오디오 파형/필름스트립 시각화(Timeline View), 화질 보정(Color Grade), 법원 제출용 타임스탬프·자막 합성 번인을 수행하는 AI 비디오 에디팅 스킬.
---

# video-editor — 포렌식 동영상 편집 & 필름스트립 시각화 스킬

이 스킬은 장시간의 CCTV, 블랙박스, 음성/영상 녹화본에서 **핵심 사건 구간을 무손실로 정밀 발췌(Trim)**하고, **오디오 파형 + 비디오 필름스트립 타임라인 이미지**를 생성하며, 법원/수사기관 제출을 위한 **자막/타임코드 오버레이 및 화질 개선**을 수행합니다.

---

## 🎯 주요 실행 시나리오 (Triggers)
- "이 동영상에서 14분 20초부터 16분 10초 구간만 잘라내서 저장해줘"
- "영상의 오디오 파형과 필름스트립을 결합한 타임라인 이미지 만들어줘"
- "어두운 CCTV/블랙박스 영상 밝기와 대비를 보정해서 선명하게 만들어줘"
- "영상에 정확한 시간대 자막과 텍스트를 입혀서 제출용 클립으로 렌더링해줘"

---

## 🛠️ 핵심 도구 및 실행 가이드

### 1. 필름스트립 + 오디오 파형 시각화 (`timeline_view.py`)
* 특정 시간대의 비디오 프레임과 오디오 파형, 침묵 구간을 결합한 고해상도 타임라인 이미지를 생성합니다:
```bash
python C:\Users\HP\.gemini\config\plugins\lazyforensic\skills\video-editor\helpers\timeline_view.py "<동영상경로>" <시작초> <종료초> -o timeline_strip.png --n-frames 12
```

### 2. 정밀 컷팅 및 렌더링 파이프라인 (`render.py`)
* 오디오 팝 노이즈 방지(30ms 오디오 페이드) 및 무손실 스트림 복사를 통해 클립을 합성/추출합니다:
```bash
# EDL(Edit Decision List) JSON 기반 렌더링
python C:\Users\HP\.gemini\config\plugins\lazyforensic\skills\video-editor\helpers\render.py edl.json -o final_evidence.mp4 --build-subtitles
```

### 3. 영상 화질 개선 및 저조도 보정 (`grade.py`)
* 어두운 야간 영상, 저조도 CCTV 영상의 감마/대비/채도를 자동 보정하여 가독성을 높입니다:
```python
from helpers.grade import auto_grade_for_clip
# ffmpeg 컬러 그레이딩 필터 체인 도출
filter_str, stats = auto_grade_for_clip("cctv_night.mp4", start=0.0, duration=30.0)
```

---

## 📋 포렌식 증거물 가공 시 준수 사항 (Evidence Integrity)
1. **원본 보존의 원칙**: 원본 비디오 파일은 절대 수정하지 않으며, 발췌/가공본은 별도 파일명(`_extracted.mp4`, `_enhanced.mp4`)으로 생성합니다.
2. **가공 이력 기록**: 발췌 구간(시작~종료 시각), 적용된 필터(밝기/대비 보정값), 오디오 트랜스크립트 원문을 감정 보고서에 명기합니다.
