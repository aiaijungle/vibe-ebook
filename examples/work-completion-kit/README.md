# 업무 하나를 검토 가능한 결과물로 만드는 워크벤치 / Work completion kit

한국어: AI 바이블 1→2→4→3→5권에서 만든 업무 정의·근거·검사·변경·승인·운영·비용 기록을 한 프로젝트로 묶습니다. JSON을 읽어 문서 5개를 만들며 실제 예약·발송·결제·배포는 실행하지 않습니다. `ready_for_review`는 작성한 기록의 검토 준비 상태이고, 실제 사람의 승인·보안 검증·생산성 향상 증명이 아닙니다.

English: Turn one scoped task into five reviewable documents: task brief, evidence and checks, changes and approval, operations, and cost and iteration. This kit generates documents. It does not perform bookings, send messages, charge customers, deploy software, or grant real permissions.

## 오프라인 사용 / Offline use

1. ZIP을 빈 폴더에 풀고 `examples/work-completion-kit/workbench.html`을 브라우저로 엽니다. 로컬 JSON 기본값은 같은 폴더의 JS 파일로 제공되어 서버나 외부 계정이 필요 없습니다.
2. `project-example.json`은 먼저 살펴볼 **가상 완성 예시**입니다. `project-template.json`은 내 업무용 빈 양식입니다. 브라우저에서 로컬 JSON을 불러와 편집하거나 원본을 복사해 수정하세요.
3. 결과와 차단 항목을 확인하고 JSON 및 생성 문서를 직접 저장하세요. **자동 저장·서버 업로드는 없습니다.** 창을 닫기 전 수동으로 저장해야 합니다. 승인·검사 결과는 실제 확인한 경우에만 작성하세요.

Unzip into an empty directory and open the HTML file directly. Import a local JSON file, review/edit its records, then manually save your JSON and documents. There is no autosave or server upload. Save before closing. Never enter secrets, credentials, purchase passwords, personal customer data, or confidential source material.

일부 모바일 파일 미리보기는 JavaScript를 실행하지 않을 수 있으므로 브라우저에서 열어야 합니다. 실제 휴대폰에서의 파일 열기는 아직 검증하지 않았습니다. Some mobile file previews may not run JavaScript; open the file in a browser. Physical-device file opening has not been verified.

## 가상 예시를 읽는 법 / About the illustration

- `fictional: true`, 기준 시각 `2026-11-02T10:05:00+09:00`. CLASS-01 도자기 수업 / S-01 / 2026-11-03 14:00~15:00 / 35,000원은 앞 권의 고정 원본과 같습니다.
- 사례의 근거·수기 확인은 **완성 형식을 보여주는 교육용 예시**입니다. 실제 모델·셸 명령 실행을 주장하지 않습니다. 변경 검증은 `verification_mode: manual`로 수기 근거와 명령 검사가 해당하지 않는 이유를 적고, `commands`와 `exit_codes`는 빈 목록으로 둡니다. 코드 변경을 실제로 검사한다면 `command` 모드에 실제 명령과 각각의 종료코드를 기록하세요. 두 모드를 섞거나 임의의 성공코드를 만들지 않습니다.
- 완성된 검토 문서를 만들기 위해 미리 승인을 받아야 하는 것은 아닙니다. 예시의 `approval.decision`은 `pending`입니다. 제안이 완성되어 검토 준비 상태가 되어도 실행은 허용되지 않습니다. 거절된 제안이나 모르는 승인 상태는 차단 항목으로 남깁니다.
- 누락된 회차는 `null`→`needs_information`, 확인된 0회는 `0`→`blocked`입니다. 미실행 사례의 `actual_status`를 비워두면 차단 항목으로 남아야 합니다.
- 10:05에 유효한 자료도 시간이 지나면 만료됩니다. `assessment_at`은 예시의 고정된 모의 검토 시각이며 실제 현재 시각이 아닙니다. 실무에서는 실제 검토 시각과 현재 원본으로 다시 확인하세요.

The completed example is fictional manual evidence, not measured model performance. Manual verification requires evidence and an explanation of why command checks are not applicable; its commands and exit codes stay empty. Command verification requires actual commands and their matching outcomes. Never fabricate a command or a successful exit code. The example proposal is pending approval: a review-ready document does not grant execution permission. Missing data, zero values, and unrun checks have different meanings. Time-sensitive source and proposal records must be rechecked for real work. A stored approval string cannot authenticate a person, bind an external action, or make execution safe.

## 원가 / Cost calculation

`총비용 = API + 도구비 + (준비 + 직접 작업 + 검수 + 재작업 분) ÷ 60 × 시간 가치`입니다. 네 시간 단계는 서로 겹치지 않게 기록하고 한 업무에 배분한 비용만 한 번씩 적으세요. 실패·재시도 비용도 빼지 않습니다. `unique_accepted`에는 최종적으로 사용 가능한 고유 결과 수를 적습니다.

완성 예시는 별도 가상 요청5건에서 유효 결과4건을 얻은 계산용 기록입니다. 수동: `(0 + 70/60×12000) / 4 = 3500원`. 보조: `(200 + 55/60×12000) / 4 = 2800원`. 8개 규칙 검사 사례와 이 5건 비용 배치는 서로 다른 자료입니다. 시간당 12,000원과 모든 금액은 연습용 가정입니다. 낮은 API 요금이 낮은 총원가를 보장하지 않습니다. 유효 결과 0건이면 건당 비용은 산출 불가입니다. 이 예시로 실제 ROI·절약 시간·매출을 주장하지 않습니다.

Total cost includes API/tool costs and the value of preparation, direct work, review, and rework time without overlapping phases. Divide by unique accepted outputs, not attempts. Zero accepted outputs means no per-output estimate. These illustrative numbers are not wage advice, production measurements, or a positive ROI claim.

## 개발자 검증 / Developer checks

Node.js가 있다면 이 폴더에서 실행합니다. 추가 패키지 설치나 네트워크가 필요 없습니다.

```text
node test_kit_engine.cjs
```

The acceptance checks cover incomplete evidence, source expiry, unrun checks, manual/command verification, pending proposals without execution permission, cost edge cases, distinct missing/zero values, readable forms, output escaping, and fixed artifact filenames. They do not exercise a real browser or external services. The application never executes commands written in a project record.
