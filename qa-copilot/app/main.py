from rule_detector import detect_rules, QA_RULES


requirement = input("요구사항을 입력하세요: ")

rules = detect_rules(requirement)

print("\n🔍 QA Thinking Trace")
print("=" * 50)

if rules:
    for rule in rules:
        rule_info = QA_RULES[rule]

        print(f"\n✅ {rule}")

        print("\n목적:")
        print(rule_info["purpose"])

        print("\n생성 테스트:")

        for test in rule_info["generated_tests"]:
            print(f"- {test}")

        print(f"\nPriority: {rule_info['priority']}/5")

        print("-" * 50)

else:
    print("⚠️ 적용 가능한 QA Rule을 찾지 못했습니다.")