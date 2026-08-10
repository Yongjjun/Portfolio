# Rule Detector Evaluation Dataset

## Purpose

QA Rule Detector의 Rule Detection 성능을 평가하기 위한
가상의 요구사항 데이터셋.

## Dataset

총 20개

- Easy: 7
- Medium: 7
- Hard: 6

## Easy Dataset

| ID | Requirement | Expected Rule |
|---|---|---|
| TC-001 | 비밀번호는 최소 8자 이상이어야 한다. | Boundary Value |
| TC-002 | 이메일 주소는 올바른 형식으로 입력해야 한다. | Validation |
| TC-003 | 이름은 필수 입력 항목이다. | Validation |
| TC-004 | Android와 iOS에서 동일한 기능을 제공해야 한다. | Platform |
| TC-005 | 만 14세 미만 사용자는 회원가입을 할 수 없다. | Business Rule |
| TC-006 | 사용자가 로그아웃하면 로그인 화면으로 이동한다. | State Transition |
| TC-007 | 비밀번호가 올바르지 않은 경우 오류 메시지를 표시한다. | Negative Test |

## Medium Dataset

| ID | Requirement | Expected Rule |
|---|---|---|
| TC-008 | 비밀번호는 8자 이상 20자 이하이며 영문과 숫자를 포함해야 한다. | Validation, Boundary Value |
| TC-009 | 이메일 형식이 올바르지 않으면 오류 메시지를 표시하고 가입을 진행할 수 없다. | Validation, Negative Test |
| TC-010 | 사용자는 중복된 이메일로 회원가입할 수 없으며 중복 시 안내 메시지를 표시한다. | Business Rule, Negative Test |
| TC-011 | 게시글을 임시 저장한 후 다시 작성할 수 있으며 게시 완료 시 작성 상태가 변경된다. | State Transition |
| TC-012 | 상품 정보를 수정하면 상품 상세 화면과 목록 화면에 변경된 정보가 반영되어야 한다. | Regression |
| TC-013 | 로그인 기능은 Web, Android, iOS에서 동일하게 제공되어야 한다. | Platform, Validation |
| TC-014 | 로그인 실패가 5회 발생하면 추가 로그인을 제한한다. | Business Rule, Negative Test |

## Hard Dataset

| ID | Requirement | Expected Rule |
|---|---|---|
| TC-015 | 사용자가 필요한 정보를 모두 입력하지 않은 경우 다음 단계로 진행할 수 없어야 한다. | Validation, Negative Test |
| TC-016 | 정상적으로 인증된 사용자만 개인 정보를 조회할 수 있어야 한다. | Security, Business Rule |
| TC-017 | 결제가 완료된 주문은 다시 결제할 수 없어야 한다. | Business Rule, State Transition |
| TC-018 | 화면 크기가 달라져도 주요 기능을 동일하게 사용할 수 있어야 한다. | Platform, Accessibility |
| TC-019 | 기존 회원의 프로필 변경 이후 관련 화면에서도 변경된 정보가 동일하게 표시되어야 한다. | Regression |
| TC-020 | 사용자가 이전 단계로 돌아간 후 다시 다음 단계로 이동해도 입력한 정보가 유지되어야 한다. | State Transition, Validation |

## Baseline Evaluation

### Keyword-based Rule Detector

- Total Cases: 20
- Exact Match: 3
- Failed Cases: 17
- Exact Match Accuracy: 15%

### Observations

1. Keyword가 직접적으로 포함된 단순 요구사항은 정상적으로 탐지하는 경향이 있음.
2. 하나의 요구사항에 여러 QA Rule이 존재할 경우 불필요한 Rule이 추가되는 문제가 발생함.
3. 동일한 키워드가 문맥에 따라 다른 Rule을 의미하는 경우 오탐이 발생함.
4. 요구사항에 Rule을 나타내는 명시적 키워드가 없는 경우 Rule을 탐지하지 못하는 문제가 발생함.
5. 요구사항의 의미와 QA 관점을 판단하는 데 Keyword Matching만으로는 한계가 존재함.