# 3·4권 오프라인 실습

Python 3.9 이상. Python 표준 라이브러리만 사용합니다. API 키·pip 설치·Claude Code 로그인이 필요 없습니다.

저장소 전체를 받거나 이 폴더의 Python 파일을 같은 폴더에 저장하세요. 개별 다운로드 시 `reader_lab.py`, `hook_guard.py`, `run_checks.py`, `test_reader_lab.py` 네 파일이 필요합니다. 명령은 저장소 루트 기준입니다.

```text
python examples/claude-code-checks/reader_lab.py
python examples/claude-code-checks/run_checks.py
python examples/claude-code-checks/run_checks.py --demo-failure
```

첫 명령: 선택 근거 R2·R3·R4, 5사례×2회 결과 passed=true, 외부 실행0건. 두 번째 명령: unittest 검사 성공 시 종료코드0. 세 번째 명령: 의도적으로 종료코드1을 반환합니다. PowerShell은 실행 직후 `$LASTEXITCODE`, Bash는 `echo $?`로 확인하세요. 검사 실패를 숨기지 않는지 확인하는 예제이며 고장 난 실습이 아닙니다.

`hook_guard.py`는 JSON 이벤트를 표준입력으로 읽고 Read만 허용합니다. Read는0, 그 외 또는 잘못된 입력은2를 반환합니다. 파일 경로나 명령을 실행하지 않습니다. 검사 코드가 이 과정을 별도 프로세스로 확인합니다.

이 파일들은 Claude Code 설정을 자동 변경하지 않습니다. 직접 훅으로 연결할 경우 설치 버전의 공식 문서·실제 절대 경로·Python 실행 파일·이벤트 입력·권한을 확인하고 샘플 저장소에서 검증하세요. PostToolUse 검사 실패는 이미 일어난 변경을 되돌리지 못합니다. PreToolUse의 차단 결과와 혼동하지 마세요.

가상 원장의 신규 기록은 로컬 리스트 추가입니다. 실제 예약·외부 발송·파일 삭제·네트워크 호출은 없습니다. 평가 결과는 결정적 가상 코드의 결과이며 실제 모델 정확도나 운영 신뢰도 측정이 아닙니다.

공식 배경:

- https://www.anthropic.com/research/effective-context-engineering-for-ai-agents
- https://www.anthropic.com/research/demystifying-evals-for-ai-agents
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/hooks
