from flask import Flask, request, jsonify
import numpy as np # 모델 입력 데이터 처리에 필요할 수 있습니다.
import joblib # scikit-learn 모델 등을 저장하고 로드할 때 사용 (예시)
from predictor import predict_tsunami

# TODO: 실제 배포 환경에서는 환경 변수에서 로드하는 것이 좋습니다.
GOOGLE_API_KEY = "AIzaSyCQt1-_LLhTfX_0l6JAZU1WwlZ1ldkTVTw"

# Flask 애플리케이션 생성
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def handle_prediction():
    # Spring Boot로부터 받은 JSON 데이터를 파싱
    data = request.get_json()

    # 데이터가 잘 들어왔는지 터미널에 출력 (디버깅용)
    print("Received data from Spring Boot:", data)

    # 필요한 데이터 추출
    # 프론트엔드에서 보낸 변수명과 일치해야 합니다.
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    magnitude = data.get('magnitude')
    depth = data.get('depth')

    # 데이터 유효성 검사
    if None in [latitude, longitude, magnitude, depth]:
        return jsonify({"error": "Missing data for prediction"}), 400

    try:
        result = predict_tsunami(magnitude, depth, latitude, longitude, GOOGLE_API_KEY)

        # Flask 서버의 콘솔에 최종 응답을 출력 (디버깅용)
        print("Sending response to Spring Boot:", result)
        return jsonify(result)

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": f"Prediction failed: {e}"}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("Flask 서버를 http://127.0.0.1:5000 에서 시작합니다...")
    print("=" * 50)
    app.run(debug=True, port=5000)