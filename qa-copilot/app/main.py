
from rule_detector import detect_rules


requirement = input("요구사항을 입력하세요: ")

rules = detect_rules(requirement)

print("\n🔍 QA Thinking Trace")
print("-" * 30)

if rules:
    for rule in rules:
        print(f"✅ {rule}")
else:
    print("⚠️ 적용 가능한 QA Rule을 찾지 못했습니다.")