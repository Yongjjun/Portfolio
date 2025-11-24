# 🛠️ Admin Auth Automation Tool (GUI)

> **자동화 프로그램 개발을 통한 QA 업무 효율 개선 프로젝트 (Portfolio Demo)**

<br>

## 📌 개요 (Overview)
QA 업무 중 반복적으로 수행되는 **어드민 페이지 로그인 및 데이터 검증 절차를 자동화**하기 위해 개발한 Python 기반 GUI 프로그램입니다.
**Tkinter**로 직관적인 GUI를 구성하고, **Selenium**을 활용해 웹 브라우저 제어를 자동화했습니다.

### ⚠️ Security Note
본 프로젝트는 보안 이슈(Security Compliance)로 인해 실제 계정/URL/로직은 **모두 더미(Dummy) 데이터로 대체**되었으며, 포트폴리오용으로 **코드 구조와 기술 스택, 설계 의도**를 중심으로 재구성되었습니다.

<br>

## ⚙️ 주요 기능 (Key Features)
- **로그인 자동화:** ID/Password 입력 후 버튼 클릭 시 WebDriver 자동 실행 및 로그인 처리
- **직관적 UI (GUI):** Tkinter 기반 인터페이스로 비개발자도 쉽게 사용 가능
- **상태 모니터링:** 로그인 프로세스 및 진행 상황을 실시간 로그(Log) 창에 표시
- **Selenium 연동:** Explicit Wait(WebDriverWait)를 적용한 안정적인 브라우저 제어

<br>

## 🧩 기술 스택 (Tech Stack)

| 구분 | 사용 기술 |
| :--- | :--- |
| **Language** | Python 3.11 |
| **GUI** | Tkinter |
| **Automation** | Selenium WebDriver |
| **Image Processing** | Pillow (PIL) |
| **Browser** | Google Chrome (Headless option supported) |

<br>

## 🚀 실행 방법 (How to Run)

1. **ChromeDriver 설정**
   - 본인의 Chrome 버전에 맞는 드라이버 설치 또는 자동 관리자 사용

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt

3. **실행**
   ```bash
   python Portfolio_Admin_Automation.py

## 📷 프로그램 실행 화면
<img width="471" height="318" alt="Imgae" src="https://github.com/user-attachments/assets/00e5e8a6-371c-424d-997d-a40eeb225ae3" />
