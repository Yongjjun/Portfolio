# Jira 이슈 키워드 분석기

from data_preprocessor import preprocess_data
import tkinter as tk
from tkinter import filedialog, messagebox, ttk # ttk 모듈 추가 (Progressbar 등을 위해)
import pandas as pd
import os
from analyzer import analyze_keywords
from report_generator import generate_html_report

# 전역 변수로 상태 라벨 정의 (어디서든 접근 가능하도록)
status_label = None

# CSV 파일을 불러오는 함수
def load_csv():
    global status_label # 전역 변수임을 명시

    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not filepath:
        messagebox.showwarning("경고", "파일을 선택하지 않았습니다.")
        return

    # 1. 진행 상황 표시 시작
    if status_label:
        status_label.config(text="데이터 로딩 및 분석 중...", fg="blue")
        root.update_idletasks() # GUI 업데이트 강제 적용

    try:
        # CSV 파일을 읽고 데이터를 전처리합니다.
        df = pd.read_csv(filepath)
        descriptions = preprocess_data(df, column_name='요약')

        if not descriptions:
            messagebox.showwarning("경고", "분석할 데이터가 없습니다. CSV 파일과 '요약' 컬럼을 확인하세요.")
            if status_label:
                status_label.config(text="준비 완료", fg="white")
            return

        # 2. 키워드 분석
        if status_label:
            status_label.config(text="키워드 분석 중...", fg="red")
            root.update_idletasks()

        keyword_freq, keyword_examples = analyze_keywords(descriptions)

        # 3. 리포트 저장 경로 선택 및 생성
        # 사용자에게 리포트 저장 폴더를 묻는 다이얼로그
        report_save_dir = filedialog.askdirectory(
            initialdir=os.path.join(os.path.expanduser("~"), "Desktop"), # 기본 경로를 바탕화면으로 설정
            title="리포트를 저장할 폴더를 선택하세요"
        )

        if not report_save_dir:
            messagebox.showwarning("경고", "리포트 저장 폴더를 선택하지 않았습니다.")
            if status_label:
                status_label.config(text="준비 완료", fg="black")
            return

        # 'Jira report' 폴더 생성
        output_folder = os.path.join(report_save_dir, "Jira report")
        os.makedirs(output_folder, exist_ok=True)

        output_path = os.path.join(output_folder, "Jira_QA_report.html")

        if status_label:
            status_label.config(text="리포트 생성 중...", fg="white")
            root.update_idletasks()

        generate_html_report(keyword_freq, keyword_examples, output_path)

        # 4. 완료 메시지 및 상태 업데이트
        messagebox.showinfo("완료", f"리포트가 성공적으로 생성되었습니다.\n경로: {output_path}")
        if status_label:
            status_label.config(text="리포트 생성 완료!", fg="green")

    except pd.errors.EmptyDataError:
        messagebox.showerror("에러", "선택한 CSV 파일이 비어 있습니다.")
        if status_label:
            status_label.config(text="에러 발생", fg="red")
    except KeyError as e:
        messagebox.showerror("에러", f"CSV 파일에 필요한 컬럼이 없습니다: {e}. '요약' 컬럼이 있는지 확인하세요.")
        if status_label:
            status_label.config(text="에러 발생", fg="red")
    except Exception as e:
        messagebox.showerror("에러", f"파일을 처리하는 중 오류가 발생했습니다: {e}")
        if status_label:
            status_label.config(text="에러 발생", fg="red")
    finally:
        # 에러 발생 또는 완료 후 최종 상태 메시지
        if status_label and status_label['text'] not in ["리포트 생성 완료!", "에러 발생"]:
            status_label.config(text="준비 완료", fg="black")


# GUI 창 생성 함수
def create_gui():
    global root, status_label # 전역 변수임을 명시 (root는 나중에 load_csv에서 사용될 수 있음)
    root = tk.Tk()
    root.title("Jira 키워드 분석 도구")
    root.geometry("450x250") # 창 크기 약간 확장

    # 상태 표시 라벨
    status_label = tk.Label(root, text="Jira CSV 파일을 선택해주세요.", fg="white", font=("Helvetica", 14))
    status_label.pack(pady=20)

    # CSV 파일 불러오기 버튼
    load_button = tk.Button(root, text="Jira CSV 파일 불러오기", command=load_csv,
                            font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="black")
    load_button.pack(pady=10) # 버튼 간격 추가

    # 추가 정보 라벨
    info_label = tk.Label(root, text="분석 후 바탕화면 'Jira report' 폴더에 리포트가 생성됩니다.", fg="white")
    info_label.pack(pady=10)


    root.mainloop()


if __name__ == "__main__":
    create_gui()
