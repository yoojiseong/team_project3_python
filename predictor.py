import joblib
import numpy as np
import utils
try:
    model = joblib.load('second_xgboost_tsunami_model.joblib')
    scaler = joblib.load('tsunami_scaler.joblib')
    print("[서비스 준비] 모델/스케일러 로드 성공.")
except FileNotFoundError as e:
    print(f"⚠️ 치명적 오류: 모델 파일({e.filename})을 찾을 수 없습니다.")
    exit()


def predict_tsunami(magnitude, depth, latitude, longitude, api_key):

    print(f"  [특성 수집 1/2] Elevation API 호출 (is_ocean, is_steep_slope)...")
    is_ocean, is_steep_slope = utils.get_elevation_features(latitude, longitude, api_key)
    print(f"    -> 완료: is_ocean={is_ocean}, is_steep_slope={is_steep_slope}")

    print(f"  [특성 수집 2/2] USGS API 호출 (단층 카운트)...")
    h_count, v_count = utils.get_usgs_fault_counts(latitude, longitude)
    print(f"    -> 완료: horizontal_count={h_count}, vertical_count={v_count}")

    X_new = np.array([[
        magnitude, depth, is_ocean, is_steep_slope, h_count, v_count
    ]])

    print("  [3/3] 데이터 스케일링 및 모델 예측...")
    X_scaled = scaler.transform(X_new)

    prediction = int(model.predict(X_scaled)[0])
    probability = float(model.predict_proba(X_scaled)[0][1])

    result = {
        "prediction": int(prediction),
        "tsunami_probability": round(probability * 100, 2),
        "features": {
            "magnitude": magnitude, "depth": depth, "is_ocean": is_ocean,
            "is_steep_slope": is_steep_slope,
            "horizontal_count_past_10y": h_count,
            "vertical_count_past_10y": v_count
        }
    }
    return result