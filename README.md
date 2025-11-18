# AI 기반 실시간 쓰나미 예측 (Python/Flask AI 서버)

이 프로젝트는 3-Tier 아키텍처(React-Spring Boot-Flask)의 AI 예측을 담당하는 Python/Flask 마이크로서비스입니다. Spring Boot 메인 서버로부터 지진 데이터를 받아, 실시간 특성 공학(Feature Engineering)을 수행하고, 학습된 XGBoost 모델을 통해 쓰나미 발생 확률을 예측하여 반환합니다.

## 1. 데이터 수집 및 전처리

* **데이터**: USGS, Google Elevation API 등 다양한 소스로부터 과거 및 실시간 지진 데이터를 수집합니다.
* **전처리**:
    1.  초기 정제: 불필요 데이터 제거.
    2.  특성 공학 (해양/고도): Google Elevation API를 이용, 지진의 해양 발생 여부 및 주변 급경사 유무를 판단합니다.
    3.  특성 공학 (단층 이동): USGS API로 과거 지진 데이터를 분석, 새 지진 주변의 수평/수직 단층 이동 횟수를 집계합니다.
    4.  데이터 증강 및 정규화: 데이터셋을 보강하고 숫자 특성을 표준화합니다.

## 2. 모델 학습 및 평가

* **모델**: 로지스틱 회귀, XGBoost 등 다양한 모델을 실험했으며, 최종적으로 **XGBoost 모델**을 사용합니다.
* **특성**: 규모, 깊이, 해양여부, 급경사여부, 수평단층이동수, 수직단층이동수 6개 특성을 사용합니다.
* **학습/평가**: 과거 지진 데이터로 모델을 학습하고 정확도, 혼동 행렬 등으로 평가합니다.

## 3. 웹 서비스 배포 (API)

* **API**: 학습된 XGBoost 모델을 Flask 기반 웹 서비스로 배포합니다.
* **엔드포인트**: `POST /predict` 엔드포인트는 JSON 형식의 지진 데이터(규모, 깊이, 위도, 경도)를 입력받습니다.
* **실시간 예측**:
    1.  Google Elevation API로 해양여부, 급경사여부 특성을 가져옵니다.
    2.  USGS API로 단층 이동 횟수를 가져옵니다.
    3.  모델을 사용하여 쓰나미 발생 확률을 예측합니다.
* **출력**: 예측 결과(쓰나미 발생 여부)와 확률을 JSON으로 반환합니다.

## 4. 프로젝트 흐름도 (아키텍처)

[Spring Boot] -> [Flask API /predict] -> [predictor.py] -> [utils.py] -> [Google/USGS API]

                                                                       |
                                                                       v
                                                             [XGBoost Model] -> [Prediction]
                                                                       |
                                                                       v
[Spring Boot] <- [Flask API] <- [predictor.py] <--------------------
