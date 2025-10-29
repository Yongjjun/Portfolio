import os
import html

# 리포트 생성 함수
def generate_html_report(keyword_freq, keyword_examples, output_path):
    top_keywords = keyword_freq.most_common(10)

    # HTML 리포트 내용 생성
    html_content = """
        <html>
        <head>
            <meta charset="utf-8">
            <title>Jira Keyword Report</title>
            <style>
                body {
                    font-family: 'Apple SD Gothic Neo', sans-serif;
                    margin: 40px;
                    background-color: #f9f9f9;
                    color: #333;
                }
                h1 {
                    color: #444;
                }
                img {
                    max-width: 100%;
                    margin-bottom: 30px;
                    border: 1px solid #ccc;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                }
                .keyword-block {
                    margin-bottom: 20px;
                    padding: 15px;
                    background: #fff;
                    border-left: 5px solid #5f9ea0;
                    box-shadow: 1px 1px 6px rgba(0,0,0,0.05);
                }
                .keyword-block h2 {
                    margin-top: 0;
                    color: #2e8b57;
                }
                .example {
                    color: #555;
                    margin-left: 15px;
                }
            </style>
        </head>
        <body>
            <h1>Top 10 Keywords</h1>
        """

    for keyword, count in top_keywords:
        examples = keyword_examples.get(keyword, ["예시 없음"])  # 예시가 없으면 기본값 추가
        # 키워드 자체도 이스케이프 처리하는게 안전
        safe_keyword = html.escape(keyword)
        html_content += f'<div class="keyword-block"><h2>{safe_keyword} ({count}회)</h2>'

        for example in examples:
            # 예시 텍스트에 html 이스케이프 처리
            safe_example = html.escape(example)
            html_content += f'<div class="example">- {safe_example}</div>'

        html_content += '</div>'

    html_content += """
        </body>
        </html>
        """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)



