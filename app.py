from flask import Flask, request, jsonify
import logging

# [💡 모델 로딩에 필요한 라이브러리 (예시: scikit-learn 모델을 저장한 joblib)를 미리 임포트합니다.]
# import joblib

# Flask 애플리케이션 생성
app = Flask(__name__)

# 터미널에 로그를 출력하기 위한 기본 설정
logging.basicConfig(level=logging.INFO)

# ----------------------------------------------
# 나중에 학습된 모델 장착할 코드 부분 (1) - 서버 시작 시 모델 로드
# ----------------------------------------------
# 모델은 서버가 시작될 때 한 번만 로드하는 것이 효율적입니다.
# try:
#     # 모델 파일 경로를 지정하여 로드합니다. (예: 'my_trained_model.pkl')
#     MODEL = joblib.load('my_trained_model.pkl')
#     app.logger.info("Regression model loaded successfully.")
# except Exception as e:
#     app.logger.error(f"Failed to load model: {e}")
#     MODEL = None # 모델 로드 실패 시 None 설정
# ----------------------------------------------

# Spring Boot의 RegressionServiceImpl에서 호출하도록 설정된 엔드포인트
# URL 경로: /predict/regression
# 요청 방식: POST
@app.route('/predict/regression', methods=['POST'])
def predict_regression():
    # Spring Boot로부터 회귀 분석 요청을 받아 처리하고, 예측 결과를 다시 Spring Boot로 반환하는 함수
    try:
        # 1. Spring Boot가 보낸 JSON 데이터 받기
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Bad Request: No JSON data received'}), 400

        app.logger.info(f"Received data from Spring Boot: {data}")

        features = data.get('features')
        if features is None:
            return jsonify({'error': 'Bad Request: "features" key not found in JSON'}), 400

        # ----------------------------------------------
        # 나중에 학습된 모델 장착할 코드 부분 (2) - 예측 수행 로직
        # ----------------------------------------------
        # if MODEL:
        #     # features는 리스트 형태이므로, 모델 입력 형태에 맞게 조정해야 합니다.
        #     # 예: features = [[10.5, 20.0, 5.2, 15.7]]
        #     # prediction = MODEL.predict([features])[0]
        #     prediction = MODEL.predict([features])[0]
        # else:
        #     # 모델이 로드되지 않았을 경우 에러 처리
        #     app.logger.error("Model is not available for prediction.")
        #     return jsonify({'error': 'Internal Server Error: AI model not loaded'}), 500

        # 지금은 통신 테스트를 위해 단순히 고정된 더미(dummy) 값을 예측 결과로 사용합니다.
        prediction = 99.99
        # ----------------------------------------------


        # 3. Spring Boot로 보낼 응답 데이터 생성
        response_data = {
            # 위에서 계산된 실제 prediction 변수를 사용합니다.
            'predictedValue': prediction
        }

        app.logger.info(f"Sending response to Spring Boot: {response_data}")

        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500


# 이 파이썬 스크립트가 직접 실행될 때만 Flask 서버를 구동
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
