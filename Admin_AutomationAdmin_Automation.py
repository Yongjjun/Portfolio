"""
📄 Portfolio_Admin_Automation.py

본 스크립트는 실제 서비스 접근이나 사내 보안 자산에 연결되지 않은
'포트폴리오용' 예시 코드임.

실제 업무 시 사용된 Selenium + Tkinter 기반 QA 자동화 툴 구조를
보안 정보(도메인, XPATH, 요소명, 계정정보 등)를 제거하여 재구성한 것임.

※ 모든 URL / 요소명 / ID / Password 등은 더미(dummy) 값임.
※ 실제 실행은 불가능하며, 구조적 참고용임.
"""

import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import tkinter.font
from tkinter import *
import sys
import os

# --- ChromeOptions 설정 ---
options = webdriver.ChromeOptions()
options.add_argument('headless')  # 창 숨김 모드 (백그라운드 실행)

# --- 로그인 정보 (전역 변수로 선언) ---
username = ''
password = ''


# ------------------------------------------
# 로그인 처리 함수
# ------------------------------------------
def login_to_site(driver, site_url, username, password):
    """
    사이트에 로그인하는 함수 (포트폴리오용 더미 로직)
    실제 코드에서는 특정 어드민 페이지에 접속하여
    ID/PW를 자동 입력 후 로그인하는 구조였음.
    """
    driver.get(site_url)
    try:
        # 사이트 구조에 따라 로그인 폼의 name/id/class 다름
        if driver.title == "Admin - Login Page":
            driver.find_element(By.NAME, 'email').send_keys(username)
            driver.find_element(By.NAME, 'password').send_keys(password)
            driver.find_element(By.CLASS_NAME, 'btn').click()
        else:
            driver.find_element(By.ID, 'login_form_email').send_keys(username)
            driver.find_element(By.ID, 'login_form_password').send_keys(password)
            driver.find_element(By.NAME, 'commit').click()

        time.sleep(2)

        # 로그인 실패 여부 확인
        if driver.title == "Admin - Login Page" or "Login failed" in driver.page_source:
            return False
        return True
    except NoSuchElementException:
        return False


# ------------------------------------------
# 페이지 이동
# ------------------------------------------
def navigate_to_page(driver, page_url):
    """특정 페이지로 이동"""
    driver.get(page_url)


# ------------------------------------------
# 사내 인증 요청 처리 (예시용)
# ------------------------------------------
def request_number_and_process(driver, prompt, window, text_widget):
    number = simpledialog.askstring("입력", prompt, parent=window)
    # 실제 업무에서는 전화번호 입력 후 인증 번호를 조회했음
    # 포트폴리오용이라 더미 출력만 남김
    text_widget.insert(tk.END, f"입력하신 번호 {number}에 대한 인증 요청 결과입니다.\n(샘플 데이터)\n\n")


# ------------------------------------------
# 패널티 테스트 (예시용)
# ------------------------------------------
def penalty_test(driver, prompt, window, text_widget):
    userid = simpledialog.askstring("입력", prompt, parent=window)
    # 실제 업무에서는 계정 검색 후 패널티 추가 로직이 있었음
    text_widget.insert(tk.END, f"{userid} 계정에 테스트용 패널티를 추가했습니다. (샘플)\n\n")


# ------------------------------------------
# 화이트리스트 등록 (예시용)
# ------------------------------------------
def cs_whitelist(driver, prompt, window, text_widget):
    number = simpledialog.askstring("입력", prompt, parent=window)
    text_widget.insert(tk.END, f"{number}를 화이트리스트에 추가했습니다. (샘플)\n\n")


# ------------------------------------------
# 계정 검색 (예시용)
# ------------------------------------------
def account_search(driver, prompt, window, text_widget):
    accountid = simpledialog.askstring("입력", prompt, parent=window)
    try:
        text_widget.insert(
            tk.END,
            f"{accountid} 계정 정보 조회 결과:\n- Account ID: demo_12345\n- Talk User ID: talk_user_demo\n\n"
        )
    except NoSuchElementException:
        text_widget.insert(tk.END, f"{accountid} 계정 정보를 찾을 수 없습니다.\n\n")


# ------------------------------------------
# 각 서브메뉴 (톡 어드민)
# ------------------------------------------
def show_submenu1(driver, window):
    submenu_window1 = tk.Toplevel(window)
    submenu_window1.title("Real 카카오톡 어드민 작업 선택")

    text_widget = scrolledtext.ScrolledText(submenu_window1, width=80, height=20)
    text_widget.pack(pady=10)

    # 버튼 디자인 설정
    button_style = {
        'font': ('한컴 말랑말랑', 16, 'bold'),
        'bg': '#4945A0',
        'fg': '#0000CD',
        'activebackground': '#4945A0',
        'activeforeground': 'yellow',
        'width': 20,
        'height': 1,
        'bd': 3,
        'relief': 'raised'
    }

    tk.Button(submenu_window1, text="사내 번호 관리",
              command=lambda: request_number_and_process(driver, '전화번호 입력', submenu_window1, text_widget),
              **button_style).pack(pady=20)
    tk.Button(submenu_window1, text="패널티 테스트 관리",
              command=lambda: penalty_test(driver, '유저 ID 입력', submenu_window1, text_widget),
              **button_style).pack(pady=20)
    tk.Button(submenu_window1, text="화이트리스트 관리",
              command=lambda: cs_whitelist(driver, '등록할 번호 입력', submenu_window1, text_widget),
              **button_style).pack(pady=20)
    tk.Button(submenu_window1, text="종료", command=submenu_window1.destroy, **button_style).pack(pady=20)


# ------------------------------------------
# 어카운트 어드민 서브메뉴
# ------------------------------------------
def show_submenu2(driver, window):
    submenu_window2 = tk.Toplevel(window)
    submenu_window2.title("Real 어카운트 어드민 작업 선택")

    text_widget = scrolledtext.ScrolledText(submenu_window2, width=80, height=20)
    text_widget.pack(pady=10)

    button_style = {
        'font': ('한컴 말랑말랑', 16, 'bold'),
        'bg': '#4945A0',
        'fg': '#990099',
        'activebackground': '#4945A0',
        'activeforeground': 'yellow',
        'width': 20,
        'height': 1,
        'bd': 3,
        'relief': 'raised'
    }

    tk.Button(submenu_window2, text="계정 조회",
              command=lambda: account_search(driver, '검색할 계정 입력', submenu_window2, text_widget),
              **button_style).pack(pady=20)
    tk.Button(submenu_window2, text="종료", command=submenu_window2.destroy, **button_style).pack(pady=20)


# ------------------------------------------
# 샌드박스 어드민 서브메뉴
# ------------------------------------------
def show_submenu3(driver, window):
    submenu_window3 = tk.Toplevel(window)
    submenu_window3.title("Sandbox 작업 선택")

    text_widget = scrolledtext.ScrolledText(submenu_window3, width=80, height=20)
    text_widget.pack(pady=10)

    button_style = {
        'font': ('한컴 말랑말랑', 16, 'bold'),
        'bg': '#4945A0',
        'fg': '#006600',
        'activebackground': '#4945A0',
        'activeforeground': 'yellow',
        'width': 20,
        'height': 1,
        'bd': 3,
        'relief': 'raised'
    }

    tk.Button(submenu_window3, text="SMS 발송내역 조회",
              command=lambda: request_number_and_process(driver, '전화번호 입력', submenu_window3, text_widget),
              **button_style).pack(pady=20)
    tk.Button(submenu_window3, text="종료", command=submenu_window3.destroy, **button_style).pack(pady=20)


# ------------------------------------------
# 메인 버튼 클릭 시 각 사이트 진입
# ------------------------------------------
def on_a_click(window):
    driver = webdriver.Chrome(options=options)
    success = login_to_site(driver, 'https://example.com/admin', username, password)
    if success:
        show_submenu1(driver, window)
    else:
        messagebox.showwarning("경고", "LDAP 혹은 비밀번호가 올바르지 않습니다.")
        driver.quit()


def on_b_click(window):
    driver = webdriver.Chrome(options=options)
    success = login_to_site(driver, 'https://example.com/account-admin', username, password)
    if success:
        show_submenu2(driver, window)
    else:
        messagebox.showwarning("경고", "LDAP 혹은 비밀번호가 올바르지 않습니다.")
        driver.quit()


def on_c_click(window):
    driver = webdriver.Chrome(options=options)
    success = login_to_site(driver, 'https://example.com/sandbox', username, password)
    if success:
        show_submenu3(driver, window)
    else:
        messagebox.showwarning("경고", "LDAP 혹은 비밀번호가 올바르지 않습니다.")
        driver.quit()


# ------------------------------------------
# 로그인 창
# ------------------------------------------
def login_window():
    login_win = tk.Tk()
    login_win.title("로그인")
    login_win.geometry("400x250")

    button_font = tkinter.font.Font(family='한컴 말랑말랑', size=20, slant="italic")

    tk.Label(login_win, text="LDAP", font=button_font).pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="비밀번호", font=button_font).pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)

    def on_login(event=None):
        global username, password
        username = username_entry.get()
        password = password_entry.get()

        if username and password:
            login_win.destroy()
            main_menu()
        else:
            messagebox.showwarning("경고", "LDAP & 비밀번호를 입력하세요")

    login_font = tkinter.font.Font(family='한컴 말랑말랑', size=15, slant="italic")
    tk.Button(login_win, text="로그인", font=login_font, command=on_login).pack(pady=20)

    login_win.bind('<Return>', on_login)
    login_win.mainloop()


# ------------------------------------------
# 메인 메뉴
# ------------------------------------------
def main_menu():
    def on_quit():
        root.destroy()

    root = tk.Tk()
    root.title("사이트 선택")
    root.geometry("480x300")

    button_style = {
        'font': ('한컴 말랑말랑', 16, 'bold'),
        'fg': 'brown',
        'activebackground': 'black',
        'activeforeground': 'yellow',
        'highlightthickness': 0,
        'width': 20,
        'height': 1,
        'bd': 0,
        'relief': 'raised'
    }

    tk.Button(root, text="Real 톡 어드민", command=lambda: on_a_click(root), **button_style).pack(pady=20)
    tk.Button(root, text="Real 어카운트 어드민", command=lambda: on_b_click(root), **button_style).pack(pady=20)
    tk.Button(root, text="Sandbox 톡 어드민", command=lambda: on_c_click(root), **button_style).pack(pady=20)
    tk.Button(root, text="종료", command=on_quit, **button_style).pack(pady=20)

    root.mainloop()


# ------------------------------------------
# 실행
# ------------------------------------------
if __name__ == "__main__":
    login_window()
