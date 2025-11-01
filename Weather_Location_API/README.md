# ☀️ Weather Data Fetcher (날씨 정보 추출기)

특정 위도($\text{lat}$)와 경도($\text{lon}$)를 기반으로 **WeatherAPI.com**에서 현재 날씨 정보를 조회하고, 그 결과를 사용자에게 친숙한 한국어로 제공하는 간단한 Python 유틸리티입니다.

## ✨ 주요 기능

* **위경도 기반 조회**: 입력된 위도와 경도(`lat`, `lon`)를 사용하여 정확한 위치의 실시간 날씨를 조회합니다.
* **섭씨 온도 제공**: 현재 섭씨 온도(`temp_c`)를 반환합니다.
* **날씨 상태 한국어 번역**: WeatherAPI의 영문 날씨 상태 텍스트를 미리 정의된 키워드를 기반으로 '비', '눈', '맑음' 등 **한국어** 상태로 변환합니다.
* **견고한 오류 처리**: 네트워크 문제, 잘못된 API 키, JSON 파싱 오류 등 다양한 예외 상황을 처리하여 프로그램의 안정성을 높입니다.

## 🛠️ 환경 설정 및 사용법

### 1. 필수 라이브러리 설치

API 요청을 위해 `requests` 라이브러리가 필요합니다.

```bash
pip install requests

```
### 2. API 키 발급 및 설정
이 프로젝트는 WeatherAPI.com의 서비스를 사용합니다.

WeatherAPI.com에 접속하여 계정을 생성하고 API Key를 발급받으세요.

제공된 코드 파일(weather_fetcher.py 등)에서 API_KEY 변수에 발급받은 키를 입력해야 합니다.

```
# weather_fetcher.py 파일 내
API_KEY = "여기에 발급받은 실제 API 키를 입력하세요"
```
### 3. 코드 실행 예시
get_weather(lat, lon) 함수를 호출하여 날씨 정보를 얻을 수 있습니다.

```

# 'weather_fetcher.py' 파일에서 함수를 불러옵니다.
from weather_fetcher import get_weather 

# 예시: 서울특별시청 (위도: 37.5665, 경도: 126.9780)
seoul_lat = 37.5665
seoul_lon = 126.9780

weather_data = get_weather(seoul_lat, seoul_lon)

if "error" in weather_data:
    print(f"날씨 정보를 가져오는 데 실패했습니다: {weather_data['error']}")
else:
    print(f"--- 조회 성공 ---")
    print(f"현재 온도: {weather_data['temperature']}°C")
    print(f"날씨 상태: {weather_data['weather']}")

# 성공 시 예상 출력 예시:
# --- 조회 성공 ---
# 현재 온도: 25.0°C
# 날씨 상태: 맑음

```

### 4. 실행 화면
<img width="1309" height="626" alt="1" src="https://github.com/user-attachments/assets/d0790f1e-bee7-4a2e-bbf5-1d854035b5d4" />

# 📝 코드 구성 요소 설명
API_KEY : WeatherAPI 서버 인증에 사용되는 고유 키.

classify_weather(text) : API 응답의 영어 날씨 상태를 '비', '눈', '맑음' 등의 한국어로 변환합니다.

get_weather(lat, lon) : 핵심 로직으로, API 요청, 응답 처리, 데이터 추출 및 오류 처리를 모두 담당하여 최종 결과를 반환합니다.

requests, json : HTTP 요청 및 JSON 데이터 처리를 위한 표준 라이브러리입니다.
