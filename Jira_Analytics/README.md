## 🧩 Jira Analytics
Jira 이슈 데이터를 분석하여 리포트로 시각화하는 Python 자동화 프로젝트

- 이 프로젝트는 개인적으로 기획부터 개발, 테스트까지 단독으로 수행함.
- QA 실무에서 발생하는 Jira 이슈 데이터를 기반으로, 어떤 영역에서 이슈가 집중적으로 발생하는지 파악하고 리스크 포인트를 도출하기 위해 제작함.
- 이 툴을 통해 키워드 데이터를 근거로 결함 다발 영역에 탐색적 테스트 리소스를 집중 투입하여 효율성 증대

## 🚀 주요 기능
- CSV 데이터 로드 | Jira 이슈 데이터를 CSV 형태로 불러옴

- 데이터 전처리 | 불필요한 컬럼(불용어 제거(ex 노출, 현상 등) 및 Null, 중복 데이터 처리

- 키워드 분석 | 이슈 제목 및 본문 내 주요 키워드 빈도 분석

- 통계 시각화 | 이슈 유형, 우선순위, 담당자별 분포 분석

- HTML 리포트 생성 | 분석 결과를 자동으로 HTML 및 워드 클라우드로 저장 (예: reports/jira_report.html)

## ⚙️ 기술 스택

- Language: Python 3.10+

- Libraries: pandas, tkinter, matplotlib (optional)

- Packaging: PyInstaller (단일 실행 파일로 변환 가능)

## 💡 실행 방법
python main.py

- CSV 파일 선택 창이 열림
- Jira 이슈 데이터 선택 후 “실행” → HTML 리포트 자동 생성
- 결과는 /reports/jira_report.html에 저장됨

## 📈 결과 예시
- 상위 10개 키워드에 해당하는 Jira 제목 노출 

[분석기를 통해 키워드별로 관련 이슈를 그룹화하여 보여주는 상세 리포트 화면]
<img width="562" height="390" alt="스크린샷 2025-11-25 오전 8 35 08" src="https://github.com/user-attachments/assets/f5fb7efb-a7ad-4af0-bbb4-11b586ea1b7d" />

<img width="597" height="735" alt="KakaoTalk_20251123_180451117" src="https://github.com/user-attachments/assets/4c0ddb20-02b8-439b-90de-f8c9f040fae1" />

## 🔒 보안 관련 참고

- 본 프로젝트의 결과물 예시는 보안을 위해 생성된 가상의 데이터(Dummy Dataset)를 사용하였습니다.

- 실제 사내 데이터는 포함되어 있지 않습니다.
