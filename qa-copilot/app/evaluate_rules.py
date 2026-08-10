from rule_detector import detect_rules


TEST_DATASET = [
    {
        "id": "TC-001",
        "requirement": "비밀번호는 최소 8자 이상이어야 한다.",
        "expected": ["Boundary Value"],
    },
    {
        "id": "TC-002",
        "requirement": "이메일 주소는 올바른 형식으로 입력해야 한다.",
        "expected": ["Validation"],
    },
    {
        "id": "TC-003",
        "requirement": "이름은 필수 입력 항목이다.",
        "expected": ["Validation"],
    },
    {
        "id": "TC-004",
        "requirement": "Android와 iOS에서 동일한 기능을 제공해야 한다.",
        "expected": ["Platform"],
    },
    {
        "id": "TC-005",
        "requirement": "만 14세 미만 사용자는 회원가입을 할 수 없다.",
        "expected": ["Business Rule"],
    },
    {
        "id": "TC-006",
        "requirement": "사용자가 로그아웃하면 로그인 화면으로 이동한다.",
        "expected": ["State Transition"],
    },
    {
        "id": "TC-007",
        "requirement": "비밀번호가 올바르지 않은 경우 오류 메시지를 표시한다.",
        "expected": ["Negative Test"],
    },
    {
        "id": "TC-008",
        "requirement": "비밀번호는 8자 이상 20자 이하이며 영문과 숫자를 포함해야 한다.",
        "expected": ["Validation", "Boundary Value"],
    },
    {
        "id": "TC-009",
        "requirement": "이메일 형식이 올바르지 않으면 오류 메시지를 표시하고 가입을 진행할 수 없다.",
        "expected": ["Validation", "Negative Test"],
    },
    {
        "id": "TC-010",
        "requirement": "사용자는 중복된 이메일로 회원가입할 수 없으며 중복 시 안내 메시지를 표시한다.",
        "expected": ["Business Rule", "Negative Test"],
    },
    {
        "id": "TC-011",
        "requirement": "게시글을 임시 저장한 후 다시 작성할 수 있으며 게시 완료 시 작성 상태가 변경된다.",
        "expected": ["State Transition"],
    },
    {
        "id": "TC-012",
        "requirement": "상품 정보를 수정하면 상품 상세 화면과 목록 화면에 변경된 정보가 반영되어야 한다.",
        "expected": ["Regression"],
    },
    {
        "id": "TC-013",
        "requirement": "로그인 기능은 Web, Android, iOS에서 동일하게 제공되어야 한다.",
        "expected": ["Platform", "Validation"],
    },
    {
        "id": "TC-014",
        "requirement": "로그인 실패가 5회 발생하면 추가 로그인을 제한한다.",
        "expected": ["Business Rule", "Negative Test"],
    },
    {
        "id": "TC-015",
        "requirement": "사용자가 필요한 정보를 모두 입력하지 않은 경우 다음 단계로 진행할 수 없어야 한다.",
        "expected": ["Validation", "Negative Test"],
    },
    {
        "id": "TC-016",
        "requirement": "정상적으로 인증된 사용자만 개인 정보를 조회할 수 있어야 한다.",
        "expected": ["Security", "Business Rule"],
    },
    {
        "id": "TC-017",
        "requirement": "결제가 완료된 주문은 다시 결제할 수 없어야 한다.",
        "expected": ["Business Rule", "State Transition"],
    },
    {
        "id": "TC-018",
        "requirement": "화면 크기가 달라져도 주요 기능을 동일하게 사용할 수 있어야 한다.",
        "expected": ["Platform", "Accessibility"],
    },
    {
        "id": "TC-019",
        "requirement": "기존 회원의 프로필 변경 이후 관련 화면에서도 변경된 정보가 동일하게 표시되어야 한다.",
        "expected": ["Regression"],
    },
    {
        "id": "TC-020",
        "requirement": "사용자가 이전 단계로 돌아간 후 다시 다음 단계로 이동해도 입력한 정보가 유지되어야 한다.",
        "expected": ["State Transition", "Validation"],
    },
    
]

def evaluate_case(case):
    actual = detect_rules(case["requirement"])

    expected = set(case["expected"])
    actual = set(actual)

    return expected == actual

for case in TEST_DATASET:
    result = evaluate_case(case)

    status = "PASS" if result else "FAIL"

    print(
        f"{case['id']} | {status} | "
        f"Expected: {case['expected']} | "
        f"Actual: {detect_rules(case['requirement'])}"
    )