# main_gui.py
import customtkinter as ctk
from PIL import Image, ImageTk
from Finish_Map import get_map
from Finish_Weather import get_weather
from customtkinter import CTkImage
import os
import sys

# 이미지 경로 처리
if getattr(sys, 'frozen', False):
    # PyInstaller로 패키징된 경우
    app_path = sys._MEIPASS  # 실행 파일의 임시 폴더 경로
else:
    # 개발 중인 경우
    app_path = os.path.dirname(__file__)

# 다국어 폰트 설정
def get_cut_font(size=14):
    font_candidates = ["Noto Sans CJK KR", "Nanum Gothic", "Malgun Gothic", "AppleGothic", "Nanum Brush Script"]
    for f in font_candidates:
        try:
            return ctk.CTkFont(family=f, size=size)
        except:
            continue
    return ctk.CTkFont(size=size)

weather_icons = {
    "맑음": "sunny.png",
    "흐림": "blur.png",
    "구름 조금": "little_cloud.png",
    "구름 많음" : "many_cloud.png",
    "비": "rain.png",
    "눈": "snow.png"
}

# 기본 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("🌤 날씨 API 정보")
app.geometry("500x500")

# 주소 입력 프레임
input_frame = ctk.CTkFrame(app, fg_color="transparent")
input_frame.pack(pady=20)

entry = ctk.CTkEntry(input_frame, placeholder_text="분당구 삼평동", font=get_cut_font(size=14))  # 수정됨
entry.pack(side="left", padx=5)

# 이미지 경로
image_folder = os.path.join(app_path, "images")  # images 폴더 경로

# 아이콘 버튼
def 조회():
    address = entry.get()
    if not address:
        label_result.configure(text="⚠️ 주소를 입력해주세요.")
        return
    label_info.pack_forget()
    try:
        lat, lon, real_address = get_map(address)

        if lat and lon:
            weather_info = get_weather(lat, lon)
            if "error" not in weather_info:
                temp = weather_info["temperature"]
                weather = weather_info["weather"]

                # 날씨 아이콘 설정
                icon_img_name = os.path.join(image_folder, weather_icons.get(weather, "default.png"))
                if os.path.exists(icon_img_name):
                    icon_image = Image.open(icon_img_name).resize((200, 200))
                    icon_ctk_image = CTkImage(light_image=icon_image, size=(200, 200))  # CTkImage로 설정
                    icon_label.configure(image=icon_ctk_image, text="")
                    icon_label.image = icon_ctk_image  # CTkImage 객체를 저장

                else:
                    icon_label.configure(image=None, text=weather)

                # 결과 출력
                label_result.configure(
                    text=f"📍  {real_address}\n\n 🌡️ 온도 : {temp}°C\n\n🌤️ 날씨 : {weather}"
                )
            else:
                label_result.configure(text="🚫 날씨 정보를 불러올 수 없습니다.")
        else:
            label_result.configure(text="❌ 주소를 찾을 수 없습니다.")
    except Exception as e:
        label_result.configure(text=f"⚠️ 오류 발생: {str(e)}")

# 돋보기 아이콘 버튼
if os.path.exists("search_icon.png"):
    search_img = Image.open("search_icon.png").resize((20, 20))
    search_photo = ImageTk.PhotoImage(search_img)
    search_btn = ctk.CTkButton(input_frame, image=search_photo, text="🔍 검색", width=30, command=조회)
    search_btn.pack(side="left")
else:
    search_btn = ctk.CTkButton(input_frame, text="🔍 검색", command=조회)
    search_btn.pack(side="left")

# 초기 안내 문구 라벨 (결과 라벨 위쪽에)
label_info = ctk.CTkLabel(app, text="원하는 지역을 입력해 주세요.\n(예: 성남시, 분당구, 삼평동)", font=get_cut_font(size=14))
label_info.pack(pady=(150))  # 위쪽 여백 넉넉히

# 날씨 아이콘 라벨
icon_label = ctk.CTkLabel(app, text="", font=get_cut_font(size=16))  # 수정됨
icon_label.pack(pady=10)

# 결과 텍스트 라벨
label_result = ctk.CTkLabel(app, text="", font=get_cut_font(size=14))  # 수정됨
label_result.pack(pady=10)

app.mainloop()