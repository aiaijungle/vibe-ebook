# 2권 최소 실행 실습

가상 스튜디오의 사전 검토입니다. 외부 API·유료 패키지·실제 예약·고객 정보가 필요하지 않습니다.

1. ZIP을 새 빈 폴더에 풀고, 그 폴더에서 터미널을 엽니다. Python 3가 필요합니다.
2. `python --version`으로 명령 사용 여부를 확인합니다. 환경에 따라 `python3`를 사용하세요.
3. `python ontology_lab.py`: `status`가 `ready_for_review`, `executed`가 `false`인지 봅니다.
4. `python -m unittest -v test_ontology_lab.py`: 마지막 결과의 `OK`와 실행 개수를 기록합니다.
5. 실행 전에 다섯 상황을 예측한 뒤 `python run_scenarios.py`를 실행합니다.
6. 각 줄의 case, expected, status, reason, evidence, executed를 읽고 자신의 예상과 비교합니다.

기대 상태: missing=needs_information / zero=blocked / normal=ready_for_review / overlap=blocked / expired=needs_information.
모든 passed=true, 마지막 `5/5 scenarios matched; executed=false in every case`이면 일치합니다.
이 결과는 실서비스 권한·중복 실행·동시 예약 처리를 검증하지 않습니다.

막히면: 파일을 찾지 못함=현재 폴더와 압축 해제 확인 / python을 찾지 못함=설치 또는 python3 확인 / import 오류=다섯 파일이 같은 폴더인지 확인.
실행하지 못했다면 오류 문구와 실행 단계만 적습니다. 미실행을 성공으로 기록하지 않습니다.

ontology_lab.py, sample_data.json, test_ontology_lab.py는 기존 공통 실습 원본을 그대로 포함합니다.
