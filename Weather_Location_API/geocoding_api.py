# geocoding.py
import requests

def get_coordinates(address):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&addressdetails=1"

    headers = {
        # "실무에서는 .env 파일이나 환경변수로 키를 관리하지만, 포트폴리오 데모용이라 변수 처리했습니다"
        "User-Agent": "HarryGeocodingApp/1.0 (test1212123@example.com)"  # 이메일을 User-Agent에 추가
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"[ERROR] 요청 실패 - 상태 코드: {response.status_code}")
            print(f"응답 내용: {response.text}")
            return None, None, None

        try:
            data = response.json()
        except ValueError as ve:
            print("[ERROR] JSON 파싱 실패")
            print(f"응답 텍스트: {response.text}")
            return None, None, None

        if data:
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            full_address = data[0]["display_name"]
            return lat, lon, full_address
        else:
            print("주소 검색 결과 없음")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 요청 중 예외 발생: {e}")
        return None, None, None
