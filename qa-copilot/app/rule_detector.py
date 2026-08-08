RULE_KEYWORDS = {
    "Validation": [
        "입력", "이메일", "비밀번호", "이름", "전화번호", "검색어"
    ],
    "Boundary Value": [
        "최소", "최대", "이상", "이하", "자", "글자", "개수", "범위"
    ],
    "Equivalence Partition": [
        "유효", "무효", "허용", "제한", "형식"
    ],
    "Negative Test": [
        "오류", "실패", "예외", "잘못된", "빈 값", "공백"
    ],
    "Business Rule": [
        "정책", "제한", "조건", "중복", "권한", "승인"
    ],
    "State Transition": [
        "변경", "저장", "삭제", "승인", "완료", "상태"
    ],
    "Regression": [
        "변경", "수정", "개선", "추가", "영향"
    ],
    "Platform": [
        "Android", "iOS", "Web", "TV", "Tablet", "Browser"
    ],
    "Accessibility": [
        "접근성", "VoiceOver", "TalkBack", "Screen Reader"
    ],
    "Security": [
        "로그인", "인증", "토큰", "세션", "권한", "개인정보"
    ],
}


def detect_rules(requirement: str) -> list[str]:
    detected_rules = []

    for rule, keywords in RULE_KEYWORDS.items():
        if any(keyword in requirement for keyword in keywords):
            detected_rules.append(rule)

    return detected_rules