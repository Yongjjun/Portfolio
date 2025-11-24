from collections import Counter
import re
from wordcloud import WordCloud
import os
from konlpy.tag import Okt
from report_generator import generate_html_report

# 불용어 리스트 수정 (더 보편적인 한국어 불용어 추가)
stopwords = set([
    '하다', '있다', '이다', '것', '이', '그', '저', '수', '때', '등', '게', '없이',
    '이번', '지난', '다음', '일부', '어떤', '또한', '및', '또는', '그리고',
    '현상', '문제', '노출', '발생', '보임', '않음', '필요', '확인', '수정', '작업', '관련', '화면',
    '접속', '이용', '처리', '진행', '확인', '변경', '가능', '사용', '경우', '통해', '부분', '대한', '합니다',
    '안되', '아니', '없습니다', '있습니다', '됩니다', '있습니다', '노출되는'
]) # 불용어를 더 풍부하게 수정

def analyze_keywords(descriptions):
    okt = Okt() # 형태소 분석기 개체 생성
    words = []
    keyword_examples = {}

    for desc in descriptions:
        # 특수문자 제거
        cleaned = re.sub(r"[^가-힣0-9a-zA-Z ]", "", desc)

        # 명사만 추출
        nouns = okt.nouns(cleaned)

        # 추출된 명사 리스트를 순회
        for word in nouns:
            if word not in stopwords and len(word) > 1:
                # [수정] 빈도 분석을 위해 words 리스트에 추가
                words.append(word) 

                # [수정] 예시 문장 저장 로직
                if word not in keyword_examples:
                    keyword_examples[word] = []
                
                # (옵션) 같은 문장이 중복해서 들어가는 것 방지
                if desc not in keyword_examples[word]:
                    keyword_examples[word].append(desc)

    freq = Counter(words)

    # 워드클라우드를 바탕화면 'Jira report' 폴더에 저장
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    images_folder = os.path.join(desktop_path, "Jira report")

    # 폴더가 없으면 생성
    os.makedirs(images_folder, exist_ok=True)

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        # font_path='/System/Library/Fonts/AppleSDGothicNeo.ttc'  # 폰트 경로
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothic.ttf')  # <-- 이 줄을 추가합니다.

    )

    wordcloud.generate_from_frequencies(freq)

    # 워드클라우드 저장 경로 설정
    wordcloud_output_path = os.path.join(images_folder, "wordcloud.png")
    wordcloud.to_file(wordcloud_output_path)

    return freq, keyword_examples
