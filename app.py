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
    data_list = request.get_json()

    # 데이터가 잘 들어왔는지 터미널에 출력 (디버깅용)
    print(f"Received data list from Spring Boot. Count: {len(data_list)}")
    # print("Full data:", data_list) # 너무 길면 주석 처리

    # 예측 결과를 담을 빈 리스트
    results = []

    try:
        # --- ⬇️ [수정] 리스트를 순회하는 for 문 추가 ⬇️ ---
        for item in data_list:

            # 필요한 데이터 추출
            # (수정) data.get() -> item.get()
            latitude = item.get('latitude')
            longitude = item.get('longitude')
            magnitude = item.get('magnitude')
            depth = item.get('depth')

            # 데이터 유효성 검사
            if None in [latitude, longitude, magnitude, depth]:
                # 하나라도 유효하지 않으면 results에 에러 객체를 추가
                results.append({"error": "Missing data for one item"})
                continue  # 다음 아이템으로 넘어감

            # predictor.py의 predict_tsunami 함수 호출
            result = predict_tsunami(magnitude, depth, latitude, longitude, GOOGLE_API_KEY)

            # 결과 리스트에 예측 결과(딕셔너리) 추가
            results.append(result)

        # --- ⬆️ [수정] for 문 종료 ⬆️ ---

        # Flask 서버의 콘솔에 최종 응답 리스트를 출력 (디버깅용)
        print(f"Sending {len(results)} results to Spring Boot:", results)

        # (수정) result -> results (결과 '리스트'를 반환)
        return jsonify(results)

    except Exception as e:
        print(f"Error during prediction loop: {e}")
        return jsonify({"error": f"Prediction failed: {e}"}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("Flask 서버를 http://127.0.0.1:5000 에서 시작합니다...")
    print("=" * 50)
    app.run(debug=True, port=5000)