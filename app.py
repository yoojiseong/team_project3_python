from flask import Flask, request, jsonify
import numpy as np
import joblib
from predictor import predict_tsunami

# TODO: 실제 배포 환경에서는 환경 변수에서 로드하는 것이 좋습니다.
GOOGLE_API_KEY = "AIzaSyCQt1-_LLhTfX_0l6JAZU1WwlZ1ldkTVTw"

# Flask 애플리케이션 생성
app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def handle_prediction():
    # Spring Boot로부터 받은 JSON '리스트'를 파싱
    data = request.get_json()

    try:
        # --- ⬇️ [수정] 데이터 타입에 따라 분기 처리 ⬇️ ---

        # Case 1: 데이터가 '리스트'일 경우 (실시간 지진 API 호출)
        if isinstance(data, list):
            print(f"Received data LIST from Spring Boot. Count: {len(data)}")
            results = []

            for item in data:
                latitude = item.get('latitude')
                longitude = item.get('longitude')
                magnitude = item.get('magnitude')
                depth = item.get('depth')

                if None in [latitude, longitude, magnitude, depth]:
                    results.append({"error": "Missing data for one item"})
                    continue

                # 샘플 데이터 추가 전
                # result = predict_tsunami(magnitude, depth, latitude, longitude, GOOGLE_API_KEY)
                # results.append(result)
                # 샘플 데이터 추가 후
                prediction_result = predict_tsunami(magnitude, depth, latitude, longitude, GOOGLE_API_KEY)
                frontend_response = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "magnitude": magnitude,
                    "depth": depth,
                    "tsunamiProbability": prediction_result.get("tsunami_probability")
                }
                results.append(frontend_response)

            print(f"Sending {len(results)} results to Spring Boot:", results)
            return jsonify(results)  # '리스트'로 반환

        # Case 2: 데이터가 '딕셔너리(객체)'일 경우 (임시 지진 API 호출)
        elif isinstance(data, dict):
            print("Received single data OBJECT from Spring Boot:", data)

            latitude = data.get('latitude')
            longitude = data.get('longitude')
            magnitude = data.get('magnitude')
            depth = data.get('depth')

            if None in [latitude, longitude, magnitude, depth]:
                return jsonify({"error": "Missing data for prediction"}), 400

            # 샘플 데이터 추가 전
            # result = predict_tsunami(magnitude, depth, latitude, longitude, GOOGLE_API_KEY)

            # print("Sending single result to Spring Boot:", result)
            # return jsonify(result)  # '객체 1개'로 반환
            # 샘플 데이터 추가 후
            prediction_result = predict_tsunami(magnitude, depth, latitude, longitude, GOOGLE_API_KEY)
            frontend_response = {
                "latitude": latitude,
                "longitude": longitude,
                "magnitude": magnitude,
                "depth": depth,
                "tsunamiProbability": prediction_result.get("tsunami_probability")
            }

            print("Sending single result to Spring Boot:", frontend_response)
            return jsonify(frontend_response)

        # Case 3: 그 외 잘못된 형식
        else:
            return jsonify({"error": "Invalid data format. Expected JSON object or list."}), 400

    except Exception as e:
        print(f"Error during prediction: {e}")
        # (참고) 오류 스택 트레이스를 포함하면 디버깅에 더 좋습니다.
        # import traceback
        # print(traceback.format_exc())
        return jsonify({"error": f"Prediction failed: {e}"}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("Flask 서버를 http://127.0.0.1:5000 에서 시작합니다...")
    print("=" * 50)
    app.run(debug=True, port=5000)