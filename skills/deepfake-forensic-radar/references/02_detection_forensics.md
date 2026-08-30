# 딥페이크 탐지 알고리즘 및 물리·생체 포렌식 불변량 전수 분석

## 1. 딥페이크 탐지 알고리즘 및 벤치마크
- **DeepfakeBench** (SJTU/OpenDataLab): 30개 이상의 탐지기와 15개 벤치마크(FF++, Celeb-DF, DF40) 표준화 통합 플랫폼. [SCLBD/DeepfakeBench](https://github.com/SCLBD/DeepfakeBench)
- **UnivFD** (Univ. of Wisconsin): CLIP-ViT 백본을 동결하고 선형 프로브만 학습하여 미학습 디퓨전/GAN 모델에 대해 **92.3% 제로샷 AUC** 달성. [Yuheng-Li/UniversalFakeDetect](https://github.com/Yuheng-Li/UniversalFakeDetect)
- **DIRE / DistilDIRE**: DDIM Inversion 후 재구성 오차 $\text{DIRE}(x) = |x - \mathcal{R}(x)|$를 측정하여 디퓨전 모델에 대해 **97.8% AUC** 기록. [ZhendongWang6/DIRE](https://github.com/ZhendongWang6/DIRE)
- **NPR** (CVPR 2024): 업샘플링 보간 레이어가 남기는 인접 픽셀 간 비자연적 수학적 잔재 추출 (91.4% AUC). [chuangchuangtan/NPR-DeepfakeDetection](https://github.com/chuangchuangtan/NPR-DeepfakeDetection)
- **F3-Net**: 주파수 대역 분할(FAD) 및 국소 주파수 통계(LFS)로 DCT 고주파 지문 포착. [weixiang/F3-Net](https://github.com/weixiang/F3-Net)
- **SPSL**: 2D 푸리에 변환 위상 스펙트럼($\Phi(u,v)$) 불연속성 검출. [clfm/SPSL](https://github.com/clfm/SPSL)
- **FakeShield**: MLLM 기반 위조 판별 + 픽셀 위조 히트맵 마스크 + 소명 텍스트 동시 출력.
- **LipForensics**: 시공간 ResNet을 통해 양순음 발음 시 입술 모션 불규칙성 검출 (압축에 극도로 강인). [ControlNet/LipForensics](https://github.com/ControlNet/LipForensics)
- **FakeCatcher**: 32개 안면 관심영역(ROI)에서 rPPG 혈류 펄스를 추출하여 위상 일관성 검증.

## 2. 물리·생체 불변량 6대 포렌식 측정 체계
1. **rPPG 혈류 펄스 (FakeCatcher / DeepRhythm)**: 심장 박동에 따른 0.75~2.5 Hz 미세 혈류 색상 변화를 32개 ROI에서 측정. 이마와 뺨의 위상 반전 및 상관계수 붕괴 포착.
2. **각막 반사광(Corneal Specular Reflection) 기하학**: 양안 각막의 광원 반사 벡터 평행성 ($\vec{L}_L \cdot \vec{L}_R \approx 1.0$) 검증. 생성 모델의 양안 3D 광선 추적 불일치 검출 (Hu et al.).
3. **동공 윤곽 기하학**: Fourier Descriptor 기반 동공 경계면의 비타원형/다각형 왜곡률 측정.
4. **2D FFT 방사상 전력 스펙트럼 붕괴**: /f^\alpha$ 전력법칙 이탈 및 전치 합성곱에 의한 규칙적 체커보드 스파이크 검출.
5. **음소-시소(Lip) 동기화**: 양순음(/p/,/b/,/m/) 발음 시 음향 파형과 입술 닫힘 간 50~150ms 시공간 오프셋 측정.
6. **PRNU 센서 지문 결핍**: 카메라 하드웨어 고유 광반응 불균일성(PRNU) 잡음의 부재 검증.

## 3. 벤치마크 정량 성능 비교표
| 탐지 모델 | 기법 분류 | FF++ (c23) AUC | Celeb-DF v2 AUC | GenImage AUC | 교차 일반화 | 압축 내구성 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Xception** | 공간 CNN | 99.2% | 65.5% | 62.1% | 낮음 (과적합) | 취약 |
| **F3-Net** | 주파수 (DCT) | 98.8% | 78.5% | 71.0% | 보통 | 우수 |
| **SPSL** | 위상 스펙트럼 | 97.9% | 79.2% | 72.8% | 보통 | 우수 |
| **UnivFD** | CLIP-ViT 프로브 | 91.5% | 86.4% | **92.3%** | **매우 높음** | 높음 |
| **DIRE** | 디퓨전 재구성 오차| 88.2% | 81.0% | **97.8%** | **디퓨전 최상**| 높음 |
| **NPR** | 인접 픽셀 보간 | 98.6% | 85.2% | 91.4% | **높음** | 높음 |
| **FakeCatcher** | 생체 혈류 신호 | 91.0% | 88.6% | N/A (비디오) | **높음** | 압축 시 취약 |
| **LipForensics** | 시공간 립 다이내믹스| 97.1% | 84.8% | N/A (토킹헤드)| **매우 높음** | **극도로 우수** |
