## ☀️ 실시간 위치 날씨 API 클라이언트

특정 위도($\text{lat}$)와 경도($\text{lon}$)를 기반으로 **WeatherAPI.com**에서 현재 날씨 정보를 조회하고, 그 결과를 사용자에게 친숙한 한국어로 제공하는 간단한 Python 유틸리티입니다.

## 🎯 프로젝트 배경 및 활용

이 프로젝트는 **테스트 업무**의 일환으로 진행되었으며, **지역 기반 데이터 호출 프로세스에 대한 심층적인 이해**를 목적으로 합니다.

* **테스트 대상:** **갤럭시 워치(Galaxy Watch)의 춘식이 워치페이스**
* **프로젝트 동기:** 워치페이스에 표시되는 **날씨 및 위치 정보가 어떤 API를 통해, 어떤 데이터 흐름으로 불러와지는지**를 파악하고 검증하기 위해 WeatherAPI 연동 과정을 직접 구현했습니다.
* **활용 가치:** 실제 웨어러블 디바이스 환경에서 **지역 기반 API의 통합 및 데이터 흐름**을 분석하고, 해당 기능의 테스트 시나리오를 설계하는 데 유용합니다.

---

## ✨ 주요 기능

* **위경도 기반 조회**: 입력된 위도와 경도(`lat`, `lon`)를 사용하여 정확한 위치의 실시간 날씨를 조회합니다.
* **섭씨 온도 제공**: 현재 섭씨 온도(`temp_c`)를 반환합니다.
* **날씨 상태 한국어 번역**: API의 영문 날씨 상태 텍스트를 '비', '눈', '맑음' 등 **한국어** 상태로 변환합니다.
* **견고한 오류 처리**: 네트워크 문제, 잘못된 API 키, JSON 파싱 오류 등 다양한 예외 상황을 처리하여 프로그램의 안정성을 높입니다.

---

## 🛠️ 환경 설정 및 사용법

### 1. 필수 라이브러리 설치

API 요청을 위해 `requests` 라이브러리가 필요합니다.

```bash
pip install requests

```
### 2. API 키 발급 및 설정
이 프로젝트는 WeatherAPI.com의 서비스를 사용합니다.

WeatherAPI.com에 접속하여 계정을 생성하고 API Key를 발급받으세요.

제공된 코드 파일에서 API_KEY 변수에 발급받은 키를 입력해야 합니다.

⚠️ Security Tip: 실제 프로젝트에서는 API Key를 코드에 직접 입력하지 않고 .env 파일이나 환경 변수로 관리하여 보안을 유지해야 합니다. (본 코드는 포트폴리오용 데모이므로 변수 처리하였습니다.)

```
# Finish_Weather.py 파일 내
API_KEY = "여기에 발급받은 실제 API 키를 입력하세요"
```
### 3. 코드 실행 예시
get_weather(lat, lon) 함수를 호출하여 날씨 정보를 얻을 수 있습니다.

```

# 'Finish_Weather.py' 파일에서 함수를 불러옵니다.
from Finish_Weather import get_weather

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

### 📝 코드 구성 요소 설명

| 파일/함수명 | 역할 및 설명 |
| :--- | :--- |
| **`API_KEY`** | WeatherAPI 서버 인증에 사용되는 고유 키 (보안상 제외됨) |
| **`get_weather(lat, lon)`** | 위경도(`lat`, `lon`) 기반 API 호출 및 데이터 파싱을 담당하는 핵심 로직 |
| **`classify_weather(text)`** | 영문 날씨 상태(Clear, Rain 등)를 한국어(맑음, 비)로 변환 |
| **`requests`** | HTTP 통신 및 JSON 데이터 처리를 위한 표준 라이브러리 |

