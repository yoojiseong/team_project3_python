from flask import Flask, request, jsonify
from predictor import predict_tsunami

GOOGLE_API_KEY = "AIzaSyCQt1-_LLhTfX_0l6JAZU1WwlZ1ldkTVTw"

app = Flask(__name__)


@app.route('/predict/tsunami', methods=['POST'])
def handle_prediction():
    print("\n--- /predict/tsunami 요청 수신 ---")
    try:
        data = request.json

        mag = data['mag1']
        dep = data['dep1']
        lat = data['lat1']
        lon = data['lon1']

        print(f"  입력 데이터: M{mag}, D{dep}, Lat{lat}, Lon{lon}")

        result = predict_tsunami(mag, dep, lat, lon, GOOGLE_API_KEY)

        print(f"  -> 최종 예측 결과: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"!!! /predict/tsunami 처리 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    print("=" * 50)
    print("Flask 서버를 http://127.0.0.1:5000 에서 시작합니다...")
    print("=" * 50)
    app.run(debug=True, port=5000)