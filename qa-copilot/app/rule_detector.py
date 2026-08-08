QA_RULES = {
    "Validation": {
        "trigger": "사용자 입력 필드가 존재하는 경우",
        "purpose": "입력값의 형식과 무결성을 검증하여 기본 기능의 안정성을 확보",
        "reason": "입력값의 형식, 필수 여부 및 허용 범위를 검증할 필요가 있음",
        "generated_tests": [
            "필수 입력",
            "형식 검증",
            "길이 검증",
            "허용 문자 검증"
        ],
        "keywords": [
            "입력", "이메일", "비밀번호", "이름", "전화번호", "검색어"
        ],
        "output": "입력값 검증 테스트 케이스",
        "priority": 5
    },

    "Boundary Value": {
        "trigger": "최소/최대 길이 또는 범위 제한이 존재하는 경우",
        "purpose": "경계 조건에서 발생하기 쉬운 결함을 탐지",
        "reason": "입력값에 최소·최대 또는 범위 제한이 존재하여 경계값 검증이 필요함",
        "generated_tests": [
            "최소-1",
            "최소",
            "최소+1",
            "최대-1",
            "최대",
            "최대+1"
        ],
        "keywords": [
            "최소", "최대", "이상", "이하", "자", "글자", "개수", "범위"
        ],
        "output": "경계값 테스트 케이스",
        "priority": 5
    },

    "Equivalence Partition": {
        "trigger": "입력값을 유효/무효 그룹으로 구분할 수 있는 경우",
        "purpose": "대표값을 선정하여 효율적으로 테스트를 수행",
        "reason": "입력값을 유효/무효 등의 그룹으로 분류하여 대표값을 검증할 필요가 있음",
        "generated_tests": [
            "정상 입력",
            "비정상 입력"
        ],
        "keywords": [
            "형식", "유효", "무효", "허용", "제한"
        ],
        "output": "동등 분할 테스트 케이스",
        "priority": 4
    },

    "Negative Test": {
        "trigger": "예외 상황 또는 잘못된 입력이 가능한 경우",
        "purpose": "예외 처리와 오류 메시지를 검증",
        "reason": "비정상적인 입력이나 예외 상황에 대한 시스템의 처리 결과를 검증할 필요가 있음",
        "generated_tests": [
            "공백",
            "NULL",
            "특수문자",
            "잘못된 형식",
            "허용되지 않은 값"
        ],
        "keywords": [
            "오류", "실패", "예외", "잘못된", "빈 값", "공백"
        ],
        "output": "예외 처리 테스트 케이스",
        "priority": 5
    },

    "Business Rule": {
        "trigger": "정책, 업무 규칙 또는 제약사항이 존재하는 경우",
        "purpose": "요구사항에 정의된 정책을 검증",
        "reason": "서비스의 정책 및 업무 조건이 요구사항대로 적용되는지 검증할 필요가 있음",
        "generated_tests": [
            "권한 검증",
            "중복 검사",
            "연령 제한",
            "가입 조건",
            "결제 정책"
        ],
        "keywords": [
            "정책", "제한", "조건", "중복", "권한", "승인"
        ],
        "output": "비즈니스 규칙 테스트 케이스",
        "priority": 5
    },

    "State Transition": {
        "trigger": "기능의 상태가 변경되는 경우",
        "purpose": "상태 변화에 따른 시스템 동작을 검증",
        "reason": "상태 변화 전후의 시스템 동작과 허용되지 않은 상태 전이를 검증할 필요가 있음",
        "generated_tests": [
            "로그인 → 로그아웃",
            "임시저장 → 게시",
            "주문 → 결제완료"
        ],
        "keywords": [
            "변경", "저장", "삭제", "승인", "완료", "상태"
        ],
        "output": "상태 전이 테스트 시나리오",
        "priority": 4
    },

    "Regression": {
        "trigger": "기능 변경 또는 신규 기능 추가가 있는 경우",
        "purpose": "변경 사항이 기존 기능에 미치는 영향을 확인",
        "reason": "변경 사항으로 인해 기존 기능에 발생할 수 있는 영향을 확인할 필요가 있음",
        "generated_tests": [
            "영향 기능 추천",
            "회귀 테스트 대상 추천"
        ],
        "keywords": [
            "변경", "수정", "개선", "추가", "영향"
        ],
        "output": "회귀 테스트 추천 목록",
        "priority": 5
    },

    "Platform": {
        "trigger": "Web, Android, iOS, Smart TV 등 여러 플랫폼을 지원하는 경우",
        "purpose": "플랫폼 간 기능 및 UI의 일관성을 검증",
        "reason": "플랫폼 및 OS별 환경 차이로 인한 동작 차이를 검증할 필요가 있음",
        "generated_tests": [
            "플랫폼별 기능 비교",
            "UI 비교",
            "OS별 동작 확인"
        ],
        "keywords": [
            "Android", "iOS", "Web", "TV", "Tablet", "Browser"
        ],
        "output": "플랫폼별 테스트 시나리오",
        "priority": 3
    },

    "Accessibility": {
        "trigger": "접근성 지원이 필요한 기능인 경우",
        "purpose": "다양한 사용자 환경에서도 서비스를 사용할 수 있도록 검증",
        "reason": "스크린 리더, 키보드 등 다양한 접근성 환경에서 기능이 정상 동작하는지 검증할 필요가 있음",
        "generated_tests": [
            "VoiceOver",
            "TalkBack",
            "키보드 탐색",
            "명암 대비"
        ],
        "keywords": [
            "접근성", "VoiceOver", "TalkBack", "Screen Reader"
        ],
        "output": "접근성 테스트 시나리오",
        "priority": 3
    },

    "Security": {
        "trigger": "인증, 권한, 개인정보 또는 민감한 데이터 처리가 존재하는 경우",
        "purpose": "보안 취약점과 권한 검증을 수행",
        "reason": "인증·권한 및 민감한 데이터 처리 과정에서 보안 문제가 발생하지 않는지 검증할 필요가 있음",
        "generated_tests": [
            "인증",
            "권한",
            "SQL Injection",
            "XSS",
            "세션 검증"
        ],
        "keywords": [
            "로그인", "인증", "토큰", "세션", "권한", "개인정보"
        ],
        "output": "보안 테스트 시나리오",
        "priority": 5
    }
}


def detect_rules(requirement: str) -> list[str]:
    detected_rules = []

    for rule, rule_info in QA_RULES.items():
        keywords = rule_info["keywords"]

        if any(keyword in requirement for keyword in keywords):
            detected_rules.append(rule)

    return detected_rules