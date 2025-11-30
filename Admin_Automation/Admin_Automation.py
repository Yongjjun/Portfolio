"""
📄 Portfolio_Admin_Automation.py (Refactored Version)

본 스크립트는 실제 서비스 접근이나 사내 보안 자산에 연결되지 않은
'포트폴리오용' 예시 코드임.

실제 업무 시 사용된 Selenium + Tkinter 기반 QA 자동화 툴 구조를
보안 정보(도메인, XPATH, 요소명, 계정정보 등)를 제거하여 재구성한 것임.

※ 모든 URL / 요소명 / ID / Password 등은 더미(dummy) 값임.
※ 실제 실행은 불가능하며, 구조적 참고용임.
"""

import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import tkinter.font
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- ChromeOptions 설정 (함수화) ---
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # 창 숨김 모드 (백그라운드 실행)
    # options.add_argument('window-size=1920x1080') # 해상도 설정 필요 시 사용
    return webdriver.Chrome(options=options)


# ------------------------------------------
# [Core] 로그인 처리 함수 (Wait 적용)
# ------------------------------------------
def login_to_site(driver, site_url, username, password):
    try:
        driver.get(site_url)
        
        # [개선] time.sleep 대신 WebDriverWait 사용 (최대 10초 대기)
        wait = WebDriverWait(driver, 10)
        
        # body 태그가 로딩될 때까지 대기 (안정성 확보)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # 사이트별 분기 로직 (데모용 더미 로직)
        if "Admin" in driver.title:
            driver.find_element(By.NAME, 'email').send_keys(username)
            driver.find_element(By.NAME, 'password').send_keys(password)
            driver.find_element(By.CLASS_NAME, 'btn').click()
        else:
            # 예외 케이스 처리
            driver.find_element(By.ID, 'login_form_email').send_keys(username)
            driver.find_element(By.ID, 'login_form_password').send_keys(password)
            driver.find_element(By.NAME, 'commit').click()

        # 로그인 후 처리를 위한 짧은 대기
        time.sleep(1)
        
        if "Login failed" in driver.page_source:
            return False
        return True

    except (TimeoutException, WebDriverException, NoSuchElementException) as e:
        print(f"Error during login: {e}")
        return False


# ------------------------------------------
# [Core] 공통 어드민 진입 핸들러 (중복 제거 핵심)
# ------------------------------------------
def handle_admin_access(window, site_name, url, submenu_callback, username, password):
    """
    버튼 클릭 시 반복되던 [드라이버 생성 -> 로그인 -> 분기 처리]를 하나로 통합.
    """
    if not username or not password:
        messagebox.showwarning("경고", "먼저 로그인을 진행해주세요.")
        return

    try:
        driver = get_driver() # 드라이버 생성
        if login_to_site(driver, url, username, password):
            # 로그인 성공 시, 넘겨받은 서브메뉴 함수(callback) 실행
            submenu_callback(driver, window, site_name)
        else:
            messagebox.showerror("실패", f"{site_name} 로그인 실패.\nID/PW를 확인하세요.")
            driver.quit()
    except Exception as e:
        messagebox.showerror("에러", f"시스템 오류 발생: {str(e)}")


# ------------------------------------------
# [UI] 서브메뉴 생성기 (UI 코드 중복 제거)
# ------------------------------------------
def create_submenu_window(parent, title, driver, buttons_config):
    """
    서브메뉴 윈도우를 동적으로 생성하는 공통 함수
    buttons_config 구조: [{"text": "버튼명", "func": 실행함수, "prompt": "입력메시지"}, ...]
    """
    sub_win = tk.Toplevel(parent)
    sub_win.title(title)

    text_widget = scrolledtext.ScrolledText(sub_win, width=60, height=15)
    text_widget.pack(pady=10)

    btn_style = {
        'font': ('Arial', 12, 'bold'),
        'bg': '#4945A0', 'fg': 'white',
        'width': 25
    }

    for btn_info in buttons_config:
        # Lambda를 사용하여 실행 함수와 인자 바인딩
        cmd = lambda f=btn_info['func'], p=btn_info['prompt']: \
            f(driver, p, sub_win, text_widget)
            
        tk.Button(sub_win, text=btn_info['text'], command=cmd, **btn_style).pack(pady=5)

    tk.Button(sub_win, text="종료", command=lambda: [driver.quit(), sub_win.destroy()], **btn_style).pack(pady=20)


# ------------------------------------------
# [Logic] 개별 기능 로직 (더미)
# ------------------------------------------
def request_number_and_process(driver, prompt, window, text_widget):
    number = simpledialog.askstring("입력", prompt, parent=window)
    text_widget.insert(tk.END, f"입력하신 {number}에 대한 처리 결과입니다.\n(샘플 데이터)\n\n")

def penalty_test(driver, prompt, window, text_widget):
    userid = simpledialog.askstring("입력", prompt, parent=window)
    text_widget.insert(tk.END, f"{userid} 계정에 패널티를 부여했습니다.\n\n")

def cs_whitelist(driver, prompt, window, text_widget):
    number = simpledialog.askstring("입력", prompt, parent=window)
    text_widget.insert(tk.END, f"{number}를 화이트리스트에 등록했습니다.\n\n")

def account_search(driver, prompt, window, text_widget):
    accountid = simpledialog.askstring("입력", prompt, parent=window)
    text_widget.insert(tk.END, f"{accountid} 계정 정보 조회 완료.\n- Status: Active\n\n")


# ------------------------------------------
# [UI] 각 서브메뉴 정의 (설정값만 관리)
# ------------------------------------------
def show_submenu1(driver, window, title):
    buttons = [
        {"text": "사내 번호 관리", "func": request_number_and_process, "prompt": "전화번호 입력"},
        {"text": "패널티 테스트 관리", "func": penalty_test, "prompt": "유저 ID 입력"},
        {"text": "화이트리스트 관리", "func": cs_whitelist, "prompt": "등록할 번호 입력"},
    ]
    create_submenu_window(window, title, driver, buttons)

def show_submenu2(driver, window, title):
    buttons = [
        {"text": "계정 조회", "func": account_search, "prompt": "검색할 계정 입력"},
    ]
    create_submenu_window(window, title, driver, buttons)

def show_submenu3(driver, window, title):
    buttons = [
        {"text": "SMS 발송내역 조회", "func": request_number_and_process, "prompt": "전화번호 입력"},
    ]
    create_submenu_window(window, title, driver, buttons)


# ------------------------------------------
# [UI] 메인 메뉴
# ------------------------------------------
def main_menu(user_id, user_pw):
    root = tk.Tk()
    root.title("사이트 선택")
    root.geometry("400x350")

    btn_style = {
        'font': ('Arial', 14, 'bold'),
        'width': 25, 
        'height': 2, 
        'bg': 'lightgray'
    }

    # 통합 핸들러(handle_admin_access)를 호출하도록 변경
    tk.Button(root, text="Real 톡 어드민", 
              command=lambda: handle_admin_access(root, "Real 톡", "https://example.com/admin", show_submenu1, user_id, user_pw), 
              **btn_style).pack(pady=10)
              
    tk.Button(root, text="Real 어카운트 어드민", 
              command=lambda: handle_admin_access(root, "Real 어카운트", "https://example.com/account", show_submenu2, user_id, user_pw), 
              **btn_style).pack(pady=10)

    tk.Button(root, text="Sandbox 톡 어드민", 
              command=lambda: handle_admin_access(root, "Sandbox ", "https://example.com/sandbox", show_submenu3, user_id, user_pw), 
              **btn_style).pack(pady=10)

    tk.Button(root, text="종료", command=root.destroy, **btn_style).pack(pady=10)

    root.mainloop()


# ------------------------------------------
# [UI] 로그인 창
# ------------------------------------------
def login_window():
    login_win = tk.Tk()
    login_win.title("로그인")
    login_win.geometry("400x250")

    # 폰트 설정 (시스템 기본 폰트로 변경하여 호환성 확보)
    font_style = ('Arial', 12)

    tk.Label(login_win, text="LDAP ID", font=font_style).pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="Password", font=font_style).pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)

    def on_login(event=None):
        user_id = username_entry.get()
        user_pw = password_entry.get()

        if user_id and user_pw:
            login_win.destroy()
            # 입력받은 ID/PW를 메인 메뉴로 전달
            main_menu(user_id, user_pw)
        else:
            messagebox.showwarning("경고", "ID & Password를 입력하세요")

    tk.Button(login_win, text="로그인", font=('Arial', 14, 'bold'), command=on_login).pack(pady=20)

    login_win.bind('<Return>', on_login)
    login_win.mainloop()


# ------------------------------------------
# 실행
# ------------------------------------------
if __name__ == "__main__":
    login_window()
