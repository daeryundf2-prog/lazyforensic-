---
name: forensic-video
description: ffmpeg/ffprobe/yt-dlp가 있으면 프레임을 뽑고 컨테이너 태그를 읽는다. 촬영일시 조작의 법정 증명이 아니다.
---

# forensic-video — 동영상 증거물 분석 & 멀티모달 시각 감정 스킬

이 스킬은 CCTV, 차량용 블랙박스, 스마트폰 녹화본(`.mov`, `.mp4`, `.avi`), 온라인 영상 URL의 동영상 증거물을 분석합니다. `ffmpeg` 및 `yt-dlp`를 통해 프레임 단위 추출, 자막/오디오 전사(STT), QuickTime/MP4 메타데이터 감정을 수행하며 Gemini의 멀티모달 비전(`view_file`)으로 프레임을 직접 확인하고 쟁점 행위를 감정합니다.

---

## 🎯 주요 실행 시나리오 (Triggers)
- "이 동영상/CCTV/블랙박스 영상 분석해줘", "동영상에서 무슨 일이 일어났는지 타임라인으로 정리해줘"
- "유튜브 영상/URL 보고 내용 요약하고 프레임 캡처해줘"
- "0116.mov 파일 메타데이터 및 촬영일시 조작 여부 감정해줘"
- "영상에서 특정 인물이 등장하는 시간대 프레임 추출해줘"

---

## 🛠️ 작업 표준 절차 (SOP)

### 1단계: 환경 및 도구 확인
* Python 및 `ffmpeg` / `ffprobe` / `yt-dlp` 상태 점검:
```bash
python skills/forensic-video/scripts/setup.py --check
```

### 2단계: 프레임 추출 및 오디오 전사 실행
* 비디오 URL 또는 로컬 파일 경로를 투입하여 주요 프레임과 자막을 추출합니다:
```bash
# 기본 모드 (장면 전환 감지 + 프레임 캡처)
python skills/forensic-video/scripts/watch.py "<동영상경로_또는_URL>" --resolution 720

# 특정 시간대(예: 1분 30초 ~ 2분 10초) 집중 분석
python skills/forensic-video/scripts/watch.py "<동영상경로>" --start 01:30 --end 02:10 --detail balanced

# 특정 쟁점 타임스탬프 프레임 캡처
python skills/forensic-video/scripts/watch.py "<동영상경로>" --timestamps 14:02:10,14:05:33
```

### 3단계: Gemini 시각 검수 (`view_file`)
* 출력된 프레임 이미지 목록의 절대 경로(`file:///...`)를 `view_file` 도구로 직접 읽어, 인물의 행동, 차량 번호판, 주변 상황, 화면 내 시간 표시(OSD)를 정밀 분석합니다.

### 4단계: 동영상 메타데이터 & 무결성 해시 감정 (선택)
* 원본 촬영일시, 카메라 인코더 정보, 파일시스템 생성/수정시간 불일치 여부를 감정합니다:
```bash
python skills/forensic-video/scripts/forensic_video_audit.py "<동영상경로>"
```

---

## 📊 감정 결과 보고서 출력 항목
1. **증거물 기본 정보**: 파일명, 해시값(SHA-256), 컨테이너 촬영일시 vs 파일시스템 일시 비교
2. **시계열 행위 타임라인 표**: `[시간(분:초)]` - `[추출 프레임]` - `[시각/음성 분석 내용]`
3. **관찰**: ffprobe 태그·프레임 목록. 인위적 편집 여부나 촬영 시점을 확정하지 않는다.
