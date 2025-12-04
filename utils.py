import requests
import time
import json
from datetime import datetime, timedelta, timezone
from calendar import monthrange
from geopy.distance import geodesic
from geopy.point import Point

SLOPE_RADIUS_KM = 60
SLOPE_THRESHOLD_METERS = 2000
USGS_RADIUS_KM = 200
USGS_MIN_MAGNITUDE = 6.0
USGS_SEARCH_YEARS = 10

#주변 반경 지점 설정 함수(60km)
def get_surrounding_points(lat, lon, radius_km):
    center_point = Point(lat, lon)
    points = {'center': (lat, lon)}
    bearings = [0, 90, 180, 270]; names = ['north', 'east', 'south', 'west']
    for name, bearing in zip(names, bearings):
        destination = geodesic(kilometers=radius_km).destination(center_point, bearing)
        points[name] = (destination.latitude, destination.longitude)
    return points

# 위도 , 경도를 가져와 is_ocean , is_steep_slope 컬럼 데이터 가져오는 함수
def get_elevation_features(lat, lon, api_key):
    is_ocean, is_steep_slope = 0, 0
    if api_key == "YOUR_GOOGLE_API_KEY_HERE":
         print("  [오류] Elevation API 키가 설정되지 않았습니다. (0, 0) 반환.")
         return 0, 0
    try:
        points_to_check = get_surrounding_points(lat, lon, SLOPE_RADIUS_KM)
        locations_list = [
            points_to_check['center'], points_to_check['north'],
            points_to_check['east'], points_to_check['south'], points_to_check['west']
        ]
        locations_str = "|".join([f"{lt},{ln}" for lt, ln in locations_list])
        url = "https://maps.googleapis.com/maps/api/elevation/json"
        params = {'locations': locations_str, 'key': api_key}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK':
            results = data['results']
            if not results: return 0, 0
            center_elevation = results[0]['elevation']
            if center_elevation < 0: is_ocean = 1
            surrounding_elevations = [res['elevation'] for res in results[1:]]
            for elev in surrounding_elevations:
                if abs(center_elevation - elev) > SLOPE_THRESHOLD_METERS:
                    is_steep_slope = 1
                    break
        return is_ocean, is_steep_slope
    except Exception as e:
        print(f"  [오류] Elevation API 실패: {e}. (0, 0) 반환.")
        return 0, 0

# USGS에서 위도 경도 기준 1. 근 2년동안 2. 반경 200KM이내에 단층 구조 카운트 갯수 가져오기
def get_usgs_fault_counts(lat, lon):
    horizontal_count, vertical_count = 0, 0
    try:
        now = datetime.now(timezone.utc)
        year, month = now.year, now.month
        _, last_day = monthrange(year, month)
        endtime = f"{year}-{month:02d}-{last_day}"
        starttime = f"{year - USGS_SEARCH_YEARS}-{month:02d}-01" 
        search_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            'format': 'geojson', 'starttime': starttime, 'endtime': endtime,
            'latitude': lat, 'longitude': lon, 'maxradiuskm': USGS_RADIUS_KM,
            'minmagnitude': USGS_MIN_MAGNITUDE
        }
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status() 
        data = response.json()
        found_quakes = data.get('features', [])
        if not found_quakes: return 0, 0

        for quake in found_quakes:
            detail_url = quake['properties'].get('detail')
            if not detail_url: continue 
            time.sleep(0.1) 
            detail_response = requests.get(detail_url, timeout=10)
            detail_response.raise_for_status()
            detail_data = detail_response.json()
            products = detail_data['properties'].get('products', {})
            rake_value = None
            all_products = products.get('moment-tensor', []) + products.get('focal-mechanism', [])
            if not all_products: continue 
            best_product = None
            for p in all_products:
                if 'gcmt' in p.get('id','').lower(): best_product = p; break
            if best_product is None:
                for p in all_products:
                     if 'us' in p.get('id','').lower() or p.get('code','').lower() == 'us': best_product = p; break
            if best_product is None: best_product = all_products[0]
            if best_product:
                props = best_product.get('properties', {})
                rake_str = props.get('nodal-plane-1-rake')
                if rake_str is None: rake_str = props.get('rake')
                if rake_str is not None: rake_value = float(rake_str)
            if rake_value is not None:
                if (45 <= rake_value <= 135) or (-135 <= rake_value <= -45):
                    vertical_count += 1
                else:
                    horizontal_count += 1
        return horizontal_count, vertical_count
    except Exception as e:
        print(f"  [오류] USGS API 실패: {e}. (0, 0) 반환.")
        return 0, 0