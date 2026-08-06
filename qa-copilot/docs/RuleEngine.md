| Rule                  | Trigger                                 | Purpose                          | Generated Test                                          |
| --------------------- | --------------------------------------- | -------------------------------- | ------------------------------------------------------- |
| Validation            | 입력 필드가 존재하는 경우                          | 입력값의 무결성을 검증하여 기본적인 기능 정상 동작을 보장 | Required, Format, Length, Invalid Character             |
| Boundary Value        | 최소/최대 길이 또는 범위 제한이 존재하는 경우              | 경계 조건에서 발생하기 쉬운 결함을 발견           | Min-1, Min, Min+1, Max-1, Max, Max+1                    |
| Equivalence Partition | 입력값의 유효/무효 그룹을 구분할 수 있는 경우              | 동일한 특성을 가진 입력을 그룹화하여 효율적인 테스트 수행 | Valid Group, Invalid Group                              |
| Negative Test         | 사용자 입력 또는 예외 상황이 존재하는 경우                | 비정상 입력 및 예외 처리 로직 검증             | Empty, NULL, Special Character, Invalid Value           |
| Business Rule         | 업무 정책이나 제약 조건이 존재하는 경우                  | 요구사항에 정의된 비즈니스 정책 준수 여부 검증       | Age Restriction, Duplicate Check, Permission Validation |
| State Transition      | 기능의 상태가 변경되는 경우                         | 상태 변화에 따른 시스템 동작을 검증             | Login → Logout, Draft → Publish                         |
| Regression            | 다른 기능에 영향을 줄 수 있는 변경 사항이 존재하는 경우        | 변경으로 인한 기존 기능 영향 범위를 확인          | Related Feature Recommendation                          |
| Platform              | Web, Android, iOS, TV 등 여러 플랫폼을 지원하는 경우 | 플랫폼별 동작 및 UI 일관성 검증              | Cross Platform Scenario                                 |
| Accessibility         | 접근성 기능을 지원하는 경우                         | 다양한 사용 환경에서도 서비스를 사용할 수 있는지 검증   | Screen Reader, Keyboard Navigation                      |
| Security              | 인증, 권한, 개인정보, 입력값 처리가 존재하는 경우           | 보안 취약점 및 권한 검증                   | SQL Injection, XSS, Authentication, Authorization       |
