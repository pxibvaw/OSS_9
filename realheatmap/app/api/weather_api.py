#weather_api.py
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from realheatmap.app.models import WeatherRaw
from realheatmap.app.database import SessionLocal

print("✅ weather_api.py 실행 시작")

district_coords = {
    '강남구': (61, 126), '강동구': (62, 126), '강북구': (61, 130), '강서구': (58, 125),
    '관악구': (59, 123), '광진구': (62, 127), '구로구': (58, 125), '금천구': (59, 124),
    '노원구': (61, 131), '도봉구': (61, 131), '동대문구': (61, 128), '동작구': (59, 124),
    '마포구': (59, 127), '서대문구': (59, 127), '서초구': (61, 125), '성동구': (61, 127),
    '성북구': (61, 129), '송파구': (62, 126), '양천구': (58, 126), '영등포구': (58, 126),
    '용산구': (60, 126), '은평구': (59, 128), '종로구': (60, 127), '중구': (60, 127),
    '중랑구': (62, 128),
}

API_KEY = "QyVnZ3/x9BjwCZybXQEDteL9NVgvr84+70lwblm0TFT4pZsgyBOb3TLZzPsY556kAAFp/PWyLdSPWEhqrb5aiw=="
API_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

def test_debug():
    print("✅ get_weather_and_save 함수 있음")
    
def get_base_datetime():
    now = datetime.now()
    if now.minute < 45:
        now -= timedelta(hours=1)
    base_date = now.strftime('%Y%m%d')
    base_time = now.strftime('%H') + "00"
    return base_date, base_time

def get_weather_and_save(district_name: str):
    if district_name not in district_coords:
        return {"error": f"'{district_name}'는 유효한 구 이름이 아닙니다."}

    nx, ny = district_coords[district_name]
    base_date, base_time = get_base_datetime()

    params = {
        'serviceKey': API_KEY,
        'pageNo': '1',
        'numOfRows': '100',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': nx,
        'ny': ny
    }

    try:
        response = requests.get(API_URL, params=params)
        data = response.json()

        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        result = {'region': district_name}

        for item in items:
            if item['category'] in ['T1H', 'REH', 'WSD']:
                result[item['category']] = float(item['obsrValue'])

        # 저장 조건 확인
        if 'T1H' in result and 'REH' in result and 'WSD' in result:
            db: Session = SessionLocal()
            weather = WeatherRaw(
                region=district_name,
                temperature=result['T1H'],
                humidity=result['REH'],
                wind=result['WSD'],
                timestamp=datetime.now()
            )
            db.add(weather)
            db.commit()
            db.refresh(weather)
            db.close()

            return result
        else:
            return {"error": "필요한 항목(T1H, REH, WSD)이 누락되었습니다."}

    except Exception as e:
        return {"error": str(e)}