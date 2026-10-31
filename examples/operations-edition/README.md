# 5권 운영 실습 — 변경 판단과 유효 결과 원가

모든 입력·금액·판정은 교육용 가상 자료입니다. 실제 모델을 호출하거나 수업 예약·발송·결제를 실행하지 않습니다. Python 3 표준 라이브러리만 사용하고 계정·관리자 키·추가 설치가 필요 없습니다.

이 폴더에서 실행합니다.

한 번에 받는 ZIP을 사용한다면 빈 폴더에 압축을 푸세요. ZIP에는 `examples/operations-edition/` 구조가 들어 있으므로 압축을 푼 최상위 폴더에서 `cd examples/operations-edition`을 실행한 뒤 아래 명령을 입력합니다.

```text
python operations_lab.py
python -m unittest -v test_operations_lab.py
```

상위 폴더에서 명령을 실행한다면 먼저 이 폴더를 작업 디렉터리로 선택하세요. 프로그램은 입력 파일을 수정하지 않고 JSON 결과를 화면에 출력합니다.

## 공통 사례와 범위

CLASS-01 도자기 입문 수업, S-01 스튜디오 A실, 2026년 11월 3일 14:00~15:00, 35,000원이라는 2권 사전 검토의 고정 원본을 유지합니다. 1권 문안 변경 실습의 DOC-01-v2와는 별도 자료입니다. 기존 운영판의 40,000원 충돌 사례는 별도의 원본 충돌 연습이며, 이 평가 자료에 적용하지 않습니다. `existing_result`도 이전 검토 결과를 뜻하며 예약 성공을 뜻하지 않습니다.

- `fixtures/eval_cases.csv`: 정답과 중요 실패 여부를 먼저 고정한 12개 사례. 상태와 가격 필드를 정확 비교합니다. 문장 표현·전체 업무 품질을 평가하는 도구는 아닙니다.
- `fixtures/eval_results.csv`: A와 B의 **미리 만든 가상 출력**. A는 9/12, B는 11/12이지만 B가 잔여 0회에서 검토 준비를 허용하므로 보류합니다. 이것은 특정 모델 성능 비교가 아닙니다.
- `fixtures/costs.csv`: 방식별 가상 결과 20건. `api_krw`에는 그 결과를 만들다 실패·재시도한 비용까지 합쳐 적습니다. 검수·재작업 시간을 모두 `review_minutes`에 포함하고, 포기한 2건의 비용도 빼지 않습니다. 고유 결과는 최종 상태로 한 번만 적습니다.
- `fixtures/local_usage.csv`, `report_snapshot.csv`: 지연 보고의 원리를 배우는 합성 CSV. 실제 공급자 API 응답 형식이 아닙니다. 실제 집계 보고와 연결하려면 기간·워크스페이스·통화·포함 항목을 맞춘 별도 어댑터가 필요합니다.

## 예상 답과 해석

- 변경: `hold`, A 9/12 → B 11/12, B 중요 실패 Q05. `fixtures/eval_results.csv`의 **연습용 사본**에서 B의 Q05 상태를 `blocked`, 가격을 빈 값으로 바꾸면 `eligible_for_human_review`가 됩니다. 비교기가 바뀐 입력에 반응하는지 보는 실험이며 모델이나 제품을 고친 것이 아닙니다. 실제 개선에서는 원인인 코드·프롬프트를 수정하고 같은 사례 전체의 출력을 새로 생성해 평가합니다. 자동 운영 승인이나 안전 보장이 아닙니다.
- 누락 실험: `eval_results.csv`에서 B의 Q12 출력 행만 지우고 `eval_cases.csv`의 Q12 정답 행은 유지하세요. 미실행 사례가 남아 비교를 완료할 수 없어야 합니다. 정답 행까지 지우면 누락 탐지를 시험하는 조건이 달라집니다.
- A: API 400원, 검수 30분, 시간당 12,000원 가정 → 총 6,400원 / 유효 결과 18건 = 355.56원.
- B: API 250원, 검수 50분 → 총 10,250원 / 18건 = 569.44원.
- 보고: 09:00 갱신 자료에는 REQ-01·02만 들어 있습니다. 09:30 REQ-03은 미반영으로 남기며 사라진 요청이나 사용 가능한 예산으로 보지 않습니다.
- 호출 전 예산 제한은 별도 운영 서비스의 책임입니다. 이 계산기는 모니터링·비용 대사 실습이며 실제 비용 상한을 강제하지 않습니다.

`approval_fingerprint`는 승인 당시 버전·도구 버전·인자가 달라졌음을 탐지하는 원리만 보여줍니다. 해시만으로 승인자의 신원·권한·유효기간·변조 방지·외부 쓰기 원자성이 생기지 않습니다. 실제 승인 상태는 서버에서 관리하고 변경된 인자로 실행하려면 다시 검토해야 합니다.

## 공식 참고자료 — 2026-10-31 확인

- [OpenAI 평가 설계](https://developers.openai.com/api/docs/guides/evaluation-best-practices#design-your-eval-process): 업무별 사례·성공 기준, 변경마다 평가.
- [OpenAI 승인 대기 작업 버전 관리](https://openai.github.io/openai-agents-python/human_in_the_loop/#versioning-pending-tasks): 모델·프롬프트·도구 변경 시 저장한 상태와 코드 경로의 버전 일치 확인.
- [Claude Usage and Cost Analytics API — Data freshness](https://platform.claude.com/docs/en/manage-claude/usage-cost-analytics-api#data-freshness): 현재 문서상 보통 4시간 이내, 최대 24시간 갱신 지연과 월말 이후 약 7일까지 값 변경 가능. 과거 사용량 보고를 실시간 잔여 예산으로 사용하지 않습니다.
- [동 문서 — Authentication](https://platform.claude.com/docs/en/manage-claude/usage-cost-analytics-api#authentication): 제품별 권한과 키가 다릅니다. API 연동은 해당 권한을 가진 독자의 선택 사항이며 이 실습의 선행 조건이 아닙니다. 관리자 자격증명을 브라우저나 책의 파일에 넣지 않습니다.

위 API의 출시일을 추정하지 않습니다. 현재 문서는 beta API와 별도의 legacy 보고 API를 구분합니다. 실제 연동 시 최신 문서를 다시 확인하세요.
