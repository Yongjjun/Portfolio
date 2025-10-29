import pandas as pd

# data_preprocessor.py
def preprocess_data(df, column_name='요약'):
    if column_name not in df.columns:
        # 지정된 컬럼이 DataFrame에 없을 경우 에러 메시지 출력 후 빈 리스트 반환
        print(f"경고: DataFrame에 '{column_name}' 컬럼이 존재하지 않습니다. 사용 가능한 컬럼: {df.columns.tolist()}")
        # 실제 애플리케이션에서는 messagebox.showerror 등을 사용할 수 있습니다.
        return []

    descriptions = df[column_name].fillna("").tolist()
    return descriptions
