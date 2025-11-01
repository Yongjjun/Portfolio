import requests
import json

# WeatherAPI 키
API_KEY = "0b54164b5cac4d88b6281309250405"  # 발급받은 API 키 입력


# 날씨 상태에 대한 한글 번역 딕셔너리
def classify_weather(condition_text):
    condition_text = condition_text.lower()

    if any(keyword in condition_text for keyword in ["rain", "drizzle"]):
        return "비"
    elif any(keyword in condition_text for keyword in ["snow", "blizzard", "sleet"]):
        return "눈"
    elif any(keyword in condition_text for keyword in ["sunny", "clear"]):
        return "맑음"
    elif any(keyword in condition_text for keyword in ["cloud", "overcast"]):
        return "구름 조금"
    elif any(keyword in condition_text for keyword in ["thunder", "storm"]):
        return "구름 많음"
    elif any(keyword in condition_text for keyword in ["mist", "fog", "haze"]):
        return "흐림"
    else:
        return condition_text  # 그대로 출력 (디버깅용)


# 날씨 정보를 가져오는 함수
def get_weather(lat, lon):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat},{lon}&aqi=no"

    try:
        response = requests.get(url)

        # 상태 코드 확인
        if response.status_code != 200:
            return {"error": f"HTTP Error {response.status_code}"}

        # 응답 내용 확인
        data = response.json()  # JSONDecodeError 발생할 수 있음

        # 응답 내용이 비어있는지 확인
        if not data:
            return {"error": "빈 응답"}

        # 데이터에서 온도와 날씨 상태 추출
        temp = data["current"]["temp_c"]  # 섭씨 온도
        raw_condition = data["current"]["condition"]["text"].lower()  # 날씨 상태 (소문자로 변환)

        # 날씨 상태를 한글로 변환
        weather_korean = classify_weather(raw_condition)  # 매핑된 값 없으면 그대로 출력
        return {"temperature": temp, "weather": weather_korean}

    except requests.exceptions.RequestException as e:
        return {"error": f"요청 오류: {str(e)}"}
    except json.decoder.JSONDecodeError as e:
        return {"error": f"JSON 파싱 오류: {str(e)}"}
    except KeyError as e:
        return {"error": f"잘못된 응답 형식: {str(e)}"}
    except Exception as e:
        return {"error": f"알 수 없는 오류: {str(e)}"}
