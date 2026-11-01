"""Insert one interactive lab per Korean volume, right after the free learning-route box.

Idempotent: an existing <section id="aib-lab-vN"> is replaced, so content edits here can be re-applied.
Run: python scripts/build_interactive_labs.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = '<link rel="stylesheet" href="assets/interactive-labs-20261101.css?v=4">'
JS = '<script src="assets/interactive-labs-20261101.js?v=4" defer></script>'

LABS = {
    'book1.html': {
        'id': 'aib-lab-v1', 'type': 'spot', 'minutes': 3,
        'title': 'AI 홍보글에서 틀린 문장 찾기',
        'goal': '원문과 다른 문장을 모두 고르기',
        'easy': 'AI는 문장을 매끄럽게 쓰지만, 원문에 없는 내용도 그럴듯하게 채웁니다. 아래 공지를 보고 AI가 쓴 홍보글에서 원문과 다른 문장을 눌러 고른 뒤 채점하세요.',
        'deep': ('왜 이런 일이 생기나', 'AI는 "다음에 올 그럴듯한 말"을 만드는 방식으로 글을 씁니다. 원문에 빈칸이 있으면 비슷한 글에서 자주 나오는 내용으로 채웁니다. 그래서 오류는 대개 세 종류입니다. 원문과 반대로 쓰기, 원문에 없는 내용 덧붙이기, 근거 없는 구매 압박 넣기. 이 세 가지만 눈으로 훑어도 대부분의 사고를 막을 수 있습니다.'),
        'pro': ('실무 노트 — 사실 확인표', '발행 전 표 하나를 만듭니다. 칸은 항목 · 원문 값 · 초안 값 · 일치 여부 · 조치. 날짜·요일·가격·포함 여부·장소·신청 방법·잔여 수량은 반드시 넣습니다. 원문에 없는 수치나 "선착순", "보장" 같은 표현은 허위·과장 광고 문제가 될 수 있어 지우는 것이 기본입니다.'),
        'data': {
            'source': '한빛공방 원데이 클래스 · 11월 15일(토) 오후 2시~4시 · 참가비 35,000원(재료 포함) · 정원 6명 · 신청은 카카오톡 채널 「한빛공방」 · 주차 불가(인근 공영주차장 이용)',
            'question': '아래 AI 초안에서 원문과 다른 문장을 모두 눌러 고르세요.',
            'segments': [
                {'text': '🌿 11월 15일 토요일 오후 2시, 한빛공방 원데이 클래스가 열립니다.', 'wrong': False, 'why': '날짜·요일·시간이 원문과 같습니다.'},
                {'text': '두 시간 동안 나만의 도자기 컵을 만들어 보세요.', 'wrong': True, 'why': '원문에는 무엇을 만드는지가 없습니다. AI가 그럴듯하게 채운 내용입니다.'},
                {'text': '참가비는 35,000원이며 재료비는 별도입니다.', 'wrong': True, 'why': '원문은 "재료 포함"입니다. 원문과 반대로 쓴 경우입니다.'},
                {'text': '정원은 6명입니다.', 'wrong': False, 'why': '원문과 같습니다.'},
                {'text': '현재 선착순 2자리만 남았어요!', 'wrong': True, 'why': '잔여석 정보는 원문에 없습니다. 근거 없는 구매 압박입니다.'},
                {'text': '신청은 카카오톡 채널 「한빛공방」에서 받습니다.', 'wrong': False, 'why': '원문과 같습니다.'},
                {'text': '공방 앞 주차가 가능하니 편하게 오세요.', 'wrong': True, 'why': '원문은 "주차 불가"입니다. 고객이 실제로 곤란해지는 오류입니다.'},
                {'text': '완성작은 가마에서 구운 뒤 2주 후에 받아 가실 수 있습니다.', 'wrong': True, 'why': '원문에 없는 약속입니다. 지키지 못하면 고객 불만으로 이어집니다.'},
            ],
            'takeaway': '오류는 ① 원문과 반대(재료비·주차) ② 원문에 없는 덧붙임(도자기 컵·2주 후 수령) ③ 근거 없는 압박(잔여석) 세 종류였습니다. 사실 확인표도 이 세 칸을 기준으로 만드세요.',
        },
    },
    'index.html': {
        'id': 'aib-lab-v2', 'type': 'choice', 'minutes': 4,
        'title': '에러 메시지 응급처치 — 첫 행동 고르기',
        'goal': '에러 4개에 가장 안전한 첫 행동 고르기',
        'easy': '에러는 고장 신호가 아니라 "어디를 보라"는 안내입니다. 실제로 자주 만나는 에러 4개를 보고, 가장 먼저 할 행동을 고르세요. 고르면 바로 이유가 나옵니다.',
        'deep': ('에러를 읽는 순서', '에러 메시지는 아래에서 위로 읽습니다. 맨 마지막 줄의 에러 이름(ModuleNotFoundError, AuthenticationError 등)이 무슨 일이 생겼는지, 그 위의 파일 이름과 줄 번호가 어디서 생겼는지 알려 줍니다. 비개발자가 가장 많이 놓치는 원인은 코드가 아니라 실행 환경입니다. 어느 폴더에서, 어느 가상환경으로, 어느 서버에서 실행했는지를 먼저 의심하세요.'),
        'pro': ('실무 노트 — AI에게 에러를 넘기는 법', '에러 전문(잘라내지 않은 원문), 실행한 명령, 실행한 위치, 직전에 바꾼 것 한 줄을 함께 줍니다. 그리고 "이 파일의 이 부분만 고쳐라, 다른 파일은 건드리지 마라"로 범위를 좁힙니다. 고친 뒤에는 처음과 같은 명령으로 다시 실행해 에러가 사라졌는지 확인합니다. API 키 같은 비밀값은 어떤 경우에도 대화창에 붙이지 않습니다.'),
        'data': {
            'steps': [
                {'context': "ModuleNotFoundError: No module named 'requests'", 'q': '처음 실행한 프로그램에서 이 에러가 났습니다. 가장 먼저 할 일은?', 'options': [
                    {'label': '코드에서 import requests 줄을 지운다', 'best': False, 'why': '에러는 사라져도 그 모듈이 하던 기능(인터넷 요청)이 함께 사라집니다.'},
                    {'label': '가상환경이 켜져 있는지 확인하고, 그 환경에 pip install requests 를 실행한다', 'best': True, 'why': '"모듈이 없다"는 뜻입니다. 설치는 했는데 다른 환경에 깔린 경우가 가장 흔하므로 환경부터 확인합니다.'},
                    {'label': '파이썬을 지우고 다시 설치한다', 'best': False, 'why': '문제보다 훨씬 큰 조치입니다. 다른 프로젝트까지 망가뜨릴 수 있습니다.'},
                ]},
                {'context': 'AuthenticationError: 401 — invalid x-api-key', 'q': 'API 호출에서 인증 에러가 났습니다. 가장 안전한 첫 행동은?', 'options': [
                    {'label': '키를 코드에 직접 붙여 넣어 빨리 테스트한다', 'best': False, 'why': '그대로 저장·공유·업로드되면 키가 유출됩니다. 유출된 키는 남이 내 요금으로 씁니다.'},
                    {'label': 'AI 채팅창에 키를 보여 주고 무엇이 틀렸는지 묻는다', 'best': False, 'why': '비밀값은 대화창에도 붙이지 않습니다. 확인은 내 컴퓨터 안에서 합니다.'},
                    {'label': '키 값은 출력하지 않고, 키가 읽혔는지(있음/없음)만 확인한 뒤 .env 위치와 변수 이름을 점검한다', 'best': True, 'why': '401의 대부분은 키가 안 읽혔거나, 변수 이름이 다르거나, 만료·삭제된 키입니다. 값을 노출하지 않고 원인을 좁힐 수 있습니다.'},
                ]},
                {'context': 'IndentationError: unexpected indent (line 42)', 'q': 'AI가 고친 코드를 실행했더니 들여쓰기 에러가 납니다. 어떻게 지시할까요?', 'options': [
                    {'label': '"처음부터 전부 다시 짜 줘"라고 한다', 'best': False, 'why': '잘 되던 부분까지 바뀌어 새 버그가 생깁니다. 2권의 "전체 덮어쓰기 금지" 규칙입니다.'},
                    {'label': '에러 전문과 42줄 주변을 주고 "이 함수만 들여쓰기를 공백 4칸으로 통일해"라고 한다', 'best': True, 'why': '원인과 범위가 분명합니다. 고친 뒤 같은 명령으로 다시 실행해 확인합니다.'},
                    {'label': '42줄을 주석 처리하고 넘어간다', 'best': False, 'why': '그 줄이 하던 일이 빠진 채로 실행됩니다. 나중에 더 찾기 어려운 버그가 됩니다.'},
                ]},
                {'context': "서버 배포 후: ImportError: cannot import name 'load_config' from 'utils'", 'q': '내 컴퓨터에서는 잘 되는데 서버에서만 실패합니다. 먼저 확인할 것은?', 'options': [
                    {'label': '서버를 재시작하고 될 때까지 다시 배포한다', 'best': False, 'why': '원인이 그대로라 같은 에러가 반복됩니다.'},
                    {'label': '코드가 내 컴퓨터에만 있는 파일·경로를 참조하는지, 그 파일이 저장소에 포함됐는지 확인한다', 'best': True, 'why': '"로컬은 되는데 서버만 실패"의 가장 흔한 원인입니다. 2권 72일 일지의 실제 사고도 같은 원인이었습니다.'},
                    {'label': '에러가 난 줄을 try/except 로 감싸 에러를 숨긴다', 'best': False, 'why': '에러는 안 보이지만 기능은 여전히 동작하지 않습니다.'},
                ]},
            ],
            'results': [
                {'min': 4, 'title': '응급처치 합격', 'text': '원인을 좁히고, 범위를 제한하고, 비밀값을 지키는 순서가 몸에 배어 있습니다.'},
                {'min': 2, 'title': '기본기는 있습니다', 'text': '틀린 문항의 이유를 다시 읽어 보세요. 대부분 "범위를 넓게 잡은 선택"이었을 것입니다.'},
                {'min': 0, 'title': '에러 읽는 순서부터', 'text': '마지막 줄의 에러 이름 → 파일과 줄 번호 → 실행 환경 순서로 읽는 연습부터 하세요. 2권 5장이 이 내용입니다.'},
            ],
            'takeaway': '전문 복사 → 마지막 줄 확인 → 환경부터 의심 → 작은 범위만 고치게 지시 → 같은 명령으로 재실행.',
        },
    },
    'agent-bible.html': {
        'id': 'aib-lab-v3', 'type': 'sort', 'minutes': 4,
        'title': '에이전트에게 맡길 일, 승인받을 일, 맡기면 안 되는 일',
        'goal': '행동 7개를 세 단계로 나누기',
        'easy': '에이전트는 스스로 행동합니다. 그래서 "무엇을 혼자 해도 되는가"를 먼저 정해야 합니다. 아래 행동 7개를 세 단계 중 하나로 나눈 뒤 정답과 비교하세요.',
        'deep': ('판단 기준 세 가지', '① 밖으로 나가는가(고객·외부 서비스에 닿는가) ② 되돌릴 수 있는가 ③ 돈·약속·개인정보가 걸렸는가. 셋 다 "아니오"면 자동 실행, 하나라도 "예"면 사람 승인, 돈과 법적 약속은 사람이 직접 결정합니다. 3권 STEP 6a의 텔레그램 승인 버튼이 이 기준을 코드로 만든 것입니다.'),
        'pro': ('실무 노트 — 재시도와 중복 실행', '응답이 끊겼을 때 "다시 보내기"는 위험합니다. 메일·결제·예약은 이미 처리됐을 수 있습니다. 요청마다 고유 키(idempotency key)를 붙이고, 재시도 전에 같은 키로 결과를 먼저 조회합니다. 일반 조회 요청은 횟수 한도를 두고 자동 재시도해도 됩니다.'),
        'data': {
            'levels': [
                {'id': 'auto', 'label': '자동 실행', 'desc': '외부 영향이 없고 되돌릴 수 있음'},
                {'id': 'approve', 'label': '사람 승인 후 실행', 'desc': '밖으로 나가거나 되돌리기 어려움'},
                {'id': 'human', 'label': '사람이 직접', 'desc': '돈·법적 약속·중복 위험이 큼, 에이전트는 제안만'},
            ],
            'question': '각 행동에 알맞은 단계를 고르세요.',
            'items': [
                {'text': '오늘 뉴스 10건을 요약해 내 노트에 저장', 'answer': 'auto', 'why': '내 노트에만 쓰고, 틀리면 지우면 됩니다.'},
                {'text': '블로그 초안을 써서 "검토 대기" 폴더에 저장', 'answer': 'auto', 'why': '아직 공개되지 않았고 사람이 검토하는 단계가 남아 있습니다.'},
                {'text': '실패한 조회 API를 최대 3번까지 다시 호출', 'answer': 'auto', 'why': '읽기 요청이고 횟수 한도가 있어 비용 폭주가 없습니다.'},
                {'text': '고객 120명에게 가격 변경 안내 메일 발송', 'answer': 'approve', 'why': '밖으로 나가고, 보낸 메일은 되돌릴 수 없으며, 대량입니다.'},
                {'text': '회사 SNS 계정에 게시물 올리기', 'answer': 'approve', 'why': '공개되는 순간 회사의 말이 됩니다. 문구와 사실을 사람이 확인합니다.'},
                {'text': '고객 환불 요청에 "환불 완료"라고 답장', 'answer': 'human', 'why': '환불 여부는 정책·법·돈이 걸린 결정입니다. 잘못된 약속이 실제 분쟁으로 이어진 사례가 있습니다.'},
                {'text': '결제 응답이 끊겨 같은 결제를 다시 요청', 'answer': 'human', 'why': '이미 결제됐다면 중복 결제가 됩니다. 결과를 먼저 조회하고 사람이 판단합니다.'},
            ],
            'takeaway': '밖으로 나가는가, 되돌릴 수 있는가, 돈·약속이 걸렸는가. 이 세 질문으로 승인 버튼의 위치가 정해집니다.',
        },
    },
    'claude-code-bible.html': {
        'id': 'aib-lab-v4', 'type': 'builder', 'minutes': 5,
        'title': 'Claude Code 작업 지시서 조립기',
        'goal': '다섯 칸을 채워 바로 쓸 수 있는 지시서 만들기',
        'easy': '"잘 만들어 줘"는 AI에게 아무 정보도 주지 않습니다. 아래 다섯 칸을 채우면 지시서가 자동으로 완성되고, 빠진 요소를 알려 줍니다. 처음이면 "예시로 채우기"를 눌러 보세요.',
        'deep': ('왜 이 다섯 칸인가', '4권의 황금 워크플로우(탐색 → 계획 → 수정 → 커밋)를 지시서로 옮긴 것입니다. 범위와 금지는 AI가 엉뚱한 파일을 바꾸는 사고를, 먼저 할 일은 계획 없이 바로 고치는 실수 #1을, 완료 확인은 검증 없이 배포하는 실수 #8을 막습니다.'),
        'pro': ('실무 노트 — 반복되면 CLAUDE.md로', '같은 금지 사항을 매번 쓰고 있다면 프로젝트의 CLAUDE.md로 옮기세요. 다만 CLAUDE.md는 매 대화에 읽히는 지침일 뿐 강제 장치가 아닙니다. 절대 바뀌면 안 되는 파일은 권한 설정이나 훅(PreToolUse)으로 막고, 완료 확인은 테스트 명령으로 자동화합니다.'),
        'data': {
            'fields': [
                {'key': 'goal', 'label': '목표 — 무엇이 어떻게 바뀌어야 하나', 'hint': '눈으로 확인할 수 있는 결과로 씁니다.', 'placeholder': '예: 로그인 실패 시 빈 화면 대신 안내 문구를 보여준다', 'example': '로그인 실패 시 빈 화면 대신 "비밀번호를 확인해 주세요" 문구를 입력창 아래에 보여준다.'},
                {'key': 'scope', 'label': '범위 — 수정해도 되는 파일', 'hint': '파일 이름을 직접 적습니다.', 'placeholder': '예: src/login.js', 'example': 'src/login.js, src/login.css'},
                {'key': 'deny', 'label': '금지 — 건드리면 안 되는 것', 'hint': '비밀값·결제·잘 되는 기능을 적습니다.', 'placeholder': '예: .env, 결제 관련 파일', 'example': '.env 파일과 src/payment/ 폴더는 열지도 수정하지도 않는다. 새 라이브러리를 설치하지 않는다.'},
                {'key': 'first', 'label': '먼저 할 일 — 고치기 전에', 'hint': '읽기와 계획을 먼저 시킵니다.', 'placeholder': '예: 관련 파일을 읽고 계획을 먼저 보여 줘', 'example': '관련 파일을 읽고 원인과 수정 계획을 3줄로 먼저 보여 준다. 내가 승인하기 전에는 수정하지 않는다.'},
                {'key': 'done', 'label': '완료 확인 — 무엇을 실행해 확인하나', 'hint': '명령과 기대 결과를 함께 적습니다.', 'placeholder': '예: npm test 가 모두 통과', 'example': 'npm test 를 실행해 모두 통과하는지 보고한다. 틀린 비밀번호를 넣었을 때 문구가 보이는지 확인하는 방법을 알려 준다.'},
            ],
            'checks': [
                {'key': 'goal', 'min': 12, 'ok': '목표가 결과로 적혀 있음', 'todo': '목표를 "무엇이 어떻게 보이면 끝인지"로 12자 이상 적기'},
                {'key': 'scope', 'pattern': '[\\w/-]+\\.\\w+|/', 'ok': '수정 범위에 파일이 있음', 'todo': '수정할 파일 이름(예: src/app.js) 적기'},
                {'key': 'deny', 'min': 4, 'ok': '금지 사항이 있음', 'todo': '건드리면 안 되는 파일이나 행동 적기'},
                {'key': 'first', 'pattern': '계획|읽|탐색|plan|승인', 'ok': '수정 전 계획 단계가 있음', 'todo': '"먼저 읽고 계획을 보여 줘"처럼 계획 단계 넣기'},
                {'key': 'done', 'pattern': 'test|npm|python|node|pytest|실행|확인', 'ok': '완료를 확인할 방법이 있음', 'todo': '실행할 명령이나 확인 방법 적기'},
            ],
            'footer': '## 보고 방식\n수정한 파일과 바뀐 내용을 요약하고, 완료 확인을 실행한 결과를 그대로 보여 줘. 확인하지 못한 것은 확인하지 못했다고 말해.',
        },
    },
    'practical-bible.html': {
        'id': 'aib-lab-v5', 'type': 'sort', 'minutes': 5,
        'title': 'L0~L4 권한 배치 연습',
        'goal': '팀 업무 7개에 AI 권한 단계 정하기',
        'easy': 'AI에게 권한을 너무 적게 주면 쓸모가 없고, 너무 많이 주면 사고가 납니다. 5권의 다섯 단계 권한표로 우리 팀 업무 7개를 배치해 보세요.',
        'deep': ('단계를 나누는 기준', '단계가 올라갈수록 "되돌리기 어려움"과 "영향 범위"가 커집니다. 읽기는 자유롭게, 정해진 반복은 한도 안에서 자율로, 외부에 쓰는 일은 책임자 클릭으로, 대량·결제·권한 변경은 더 강한 확인으로, 정책과 AI 자신의 규칙은 사람만 바꿉니다.'),
        'pro': ('실무 노트 — 표를 운영판으로', '배치가 끝나면 업무마다 담당자 · 단계 · 한도(건수·금액) · 승인자 · 기록 위치를 한 줄로 적습니다. 이것이 5권 운영판의 첫 줄입니다. 한 달 동안 사고 없이 돌아간 업무만 한 단계 내리고, 사고가 나면 즉시 한 단계 올립니다.'),
        'data': {
            'levels': [
                {'id': 'L0', 'label': 'L0 정보', 'desc': '읽기·검색, 자유'},
                {'id': 'L1', 'label': 'L1 자율', 'desc': '정해진 반복 업무, 건수 한도 안에서'},
                {'id': 'L2', 'label': 'L2 1-click', 'desc': '외부에 쓰는 일, 책임자 클릭 승인'},
                {'id': 'L3', 'label': 'L3 강한 확인', 'desc': '대량 발송·결제·권한 변경, 재확인 필수'},
                {'id': 'L4', 'label': 'L4 사람 전용', 'desc': 'AI는 추천만, 실행은 사람'},
            ],
            'question': '각 업무에 알맞은 단계를 고르세요.',
            'items': [
                {'text': '지난주 회의록에서 결정 사항만 찾아 정리', 'answer': 'L0', 'why': '읽고 정리만 합니다. 아무것도 바뀌지 않습니다.'},
                {'text': '매일 아침 정해진 형식으로 매출 요약을 팀 채널에 게시', 'answer': 'L1', 'why': '내부 채널, 고정 형식, 하루 1건. 틀려도 바로 정정할 수 있습니다.'},
                {'text': '거래처 문의에 견적 회신 메일 보내기', 'answer': 'L2', 'why': '외부로 나가는 한 건입니다. 책임자가 내용을 보고 클릭으로 승인합니다.'},
                {'text': '결제 실패한 구독 고객 전체에 재결제 실행', 'answer': 'L3', 'why': '돈이 움직이고 대상이 많습니다. 대상 수와 금액을 재확인한 뒤 실행합니다.'},
                {'text': '신규 입사자에게 공유 드라이브 접근 권한 부여', 'answer': 'L3', 'why': '권한은 주는 순간부터 정보가 열립니다. 대상과 범위를 재확인합니다.'},
                {'text': '홈페이지의 환불·이용 정책 문구 변경', 'answer': 'L4', 'why': '법적 약속입니다. AI는 초안만, 결정과 게시는 사람이 합니다.'},
                {'text': 'AI 자신의 운영 규칙 파일(CLAUDE.md 등) 수정', 'answer': 'L4', 'why': 'AI가 자기 규칙을 바꾸면 다른 모든 통제가 무력해집니다.'},
            ],
            'takeaway': '단계는 "얼마나 똑똑한가"가 아니라 "틀렸을 때 얼마나 크게 번지는가"로 정합니다.',
        },
    },
}


def section(c):
    data = json.dumps(c['data'], ensure_ascii=False).replace('</', '<\\/')
    e = html.escape
    return (
        f'<section class="aib-lab" data-lab="{c["type"]}" id="{c["id"]}" aria-labelledby="{c["id"]}-title">\n'
        f'  <p class="lab-kicker">직접 해보기 · 인터랙티브 실습</p><h2 id="{c["id"]}-title">{e(c["title"])}</h2>\n'
        f'  <p class="lab-meta"><span>⏱ {c["minutes"]}분</span><span>🎯 {e(c["goal"])}</span><span>로그인·API 키 불필요 · 입력 내용은 저장·전송되지 않음</span></p>\n'
        f'  <p>{e(c["easy"])}</p>\n'
        f'  <div class="lab-mount"></div>\n'
        f'  <details class="lab-layer"><summary>한 단계 깊게 — {e(c["deep"][0])}</summary><p>{e(c["deep"][1])}</p></details>\n'
        f'  <details class="lab-layer"><summary>{e(c["pro"][0])}</summary><p>{e(c["pro"][1])}</p></details>\n'
        f'  <script type="application/json" class="lab-data">{data}</script>\n'
        f'</section>\n'
    )


def main():
    for name, c in LABS.items():
        path = ROOT / name
        t = path.read_text(encoding='utf-8')
        block = section(c)
        existing = re.compile(r'<section class="aib-lab"[^>]*id="' + c['id'] + r'".*?</section>\n?', re.S)
        if existing.search(t):
            t = existing.sub(lambda m: block, t, count=1)
        else:
            start = t.index('id="aib-learning-route"')
            end = t.index('</section>', start) + len('</section>')
            t = t[:end] + '\n' + block + t[end:]
        if CSS not in t:
            anchor = '<link rel="stylesheet" href="assets/learning-edition-20261031.css?v=3">'
            t = t.replace(anchor, anchor + '\n' + CSS + '\n' + JS, 1)
        path.write_text(t, encoding='utf-8')
        print('lab', c['id'], '->', name)


if __name__ == '__main__':
    main()
