| Rule                  | 설명          | 예시                   |
| --------------------- | ----------- | -------------------- |
| Validation            | 입력값 검증      | 이메일 형식               |
| Boundary Value        | 최소/최대/경계값   | 비밀번호 7자, 8자, 9자      |
| Equivalence Partition | 유효/무효 그룹 분리 | 정상 이메일 / 비정상 이메일     |
| Negative Test         | 비정상 입력      | 공백, NULL             |
| Business Rule         | 정책 검증       | 미성년자 가입 제한           |
| State Transition      | 상태 변화       | 로그인 → 로그아웃           |
| Regression            | 영향 범위       | 로그인 변경 시 비밀번호 찾기 영향  |
| Platform              | 플랫폼 차이      | iOS / Android        |
| Accessibility         | 접근성         | VoiceOver, TalkBack  |
| Security              | 보안          | SQL Injection, XSS 등 |
