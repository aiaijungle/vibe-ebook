"""Insert hands-on labs at the end of specific chapters (inside the paid reading flow).

Each lab goes right before the next chapter starts: inside the previous chapter <section> for
section-based volumes (3, 4, 5), or before the divider for flat volumes (1, 2). Author prose is untouched.
Idempotent: existing <section id="..."> labs are replaced. Run: python scripts/build_chapter_labs.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = __import__('html').escape


def F(key, label, example, hint=None):
    f = {'key': key, 'label': label, 'example': example, 'placeholder': '예: ' + example[:40]}
    if hint:
        f['hint'] = hint
    return f


def checks_for(fields):
    return [{'key': f['key'], 'min': 4, 'ok': f['label'].split(' — ')[0] + ' 적음', 'todo': f['label'].split(' — ')[0] + ' 채우기'} for f in fields]


def O(label, best, why):
    return {'label': label, 'best': best, 'why': why}


LABS = [
    # ---------------- volume 1
    dict(file='book1.html', before='4장. AI한테 잘 시키는 법', id='lab-v1-ch3', type='choice', minutes=3,
         title='채널을 바꿔도 사실은 같게', goal='채널별 변환에서 생기는 실수 3개 판단',
         easy='블로그 글을 인스타그램·문자·영상 대본으로 바꿀 때 가장 자주 생기는 일 세 가지입니다.',
         data={'steps': [
             {'context': '블로그 원문: "11월 30일까지 10% 할인, 공식몰에서만". 문자로 줄였더니 → "지금 10% 할인 중!"', 'q': '이 문자를 보내도 될까요?', 'options': [
                 O('짧아야 하니 그대로 보낸다', False, '마감일과 판매처가 빠지면 다른 곳에서 할인을 요구하는 문의가 생깁니다.'),
                 O('마감일과 판매처를 넣고, 대신 다른 수식어를 뺀다', True, '줄일 때 빼는 것은 꾸밈말이지 조건이 아닙니다.')]},
             {'context': '영상 대본으로 바꾸자 AI가 "구매자 98%가 만족했어요"라는 문장을 넣었습니다. 원문에는 없는 숫자입니다.', 'q': '어떻게 할까요?', 'options': [
                 O('영상은 재미가 중요하니 둔다', False, '근거 없는 수치는 채널과 상관없이 허위 광고 문제가 될 수 있습니다.'),
                 O('지운다. 실제 후기가 있으면 출처와 함께 따로 넣는다', True, '원문에 없는 숫자는 지우는 것이 기본입니다.')]},
             {'context': '세 채널 글을 모두 받았습니다. 시간이 10분밖에 없습니다.', 'q': '무엇부터 확인할까요?', 'options': [
                 O('문장이 매끄러운지', False, '문장은 나중에 고쳐도 됩니다. 틀린 사실은 고객에게 바로 피해를 줍니다.'),
                 O('세 채널의 날짜·가격·조건·링크가 원문과 같은지', True, '사실 확인이 먼저, 표현은 그다음입니다.')]}],
             'results': [{'min': 3, 'title': '채널 변환 합격', 'text': '줄여도 조건은 남기는 감각이 있습니다.'}, {'min': 0, 'title': '한 번 더', 'text': '틀린 장면의 이유를 다시 읽어 보세요.'}],
             'takeaway': '채널마다 말투와 길이는 달라도, 독자에게 약속한 사실은 같아야 한다.'}),
    dict(file='book1.html', before='5장. 에러를 만나면', id='lab-v1-ch4', type='builder', minutes=5,
         title='CIF 지시서 조립기', goal='C·I·F 세 줄을 채워 지시서 완성',
         easy='이 장의 CIF 공식을 바로 써 봅니다. 세 칸만 채우면 AI에게 줄 지시서가 완성됩니다. 금지와 확인 칸을 더하면 더 안전합니다.',
         data={'fields': [
             F('c', 'C (Context) — 지금 상황', '나는 동네 꽃집을 한다. 인스타그램 팔로워 1,200명. 이번 주 신상품은 미니 꽃다발 15,000원'),
             F('i', 'I (Intent) — 하고 싶은 것', '이번 주 신상품 소개 게시물 문구 3가지 버전을 만들고 싶다'),
             F('f', 'F (Format) — 결과물 형태', '각 150자 이내, 해시태그 5개, 버전마다 첫 문장을 다르게'),
             F('ban', '금지 — 하지 말 것', '가격·재고·할인을 바꾸거나 새로 만들지 말 것'),
             F('chk', '확인 — 내가 볼 것', '가격 15,000원이 그대로인지, 매장 위치를 지어내지 않았는지')],
             'checks': None, 'footer': '## 모르는 정보\n빠진 정보가 있으면 추측하지 말고 [확인 필요]로 표시해 줘.'}),
    # ---------------- volume 2
    dict(file='index.html', before='제5장 : 비개발자를', id='lab-v2-ch4', type='steps', minutes=10,
         title='배포 버튼 누르기 전 6단계 점검', goal='배포 전 사고 6가지를 미리 막기',
         easy='이 장에서 만든 페이지를 공개하기 전에 하나씩 체크하세요. 2권 72일 일지의 실제 사고들이 이 목록의 출처입니다.',
         data={'steps': [
             {'title': '.env 같은 비밀 파일이 .gitignore에 들어 있다', 'detail': 'git status에 .env가 보이면 아직 막히지 않은 것입니다.'},
             {'title': '코드에 내 컴퓨터 경로(C:/Users/...)가 없다', 'detail': '서버에는 그 폴더가 없습니다. 첫 배포 날 ImportError의 원인이었습니다.'},
             {'title': '필요한 패키지가 requirements.txt(또는 package.json)에 모두 적혀 있다'},
             {'title': '새 폴더에 저장소를 처음부터 받아서 다시 실행해 봤다', 'detail': '내 컴퓨터에만 있던 파일이 빠졌는지 확인하는 가장 확실한 방법입니다.'},
             {'title': 'API를 쓴다면 결제 한도와 금액 알림을 설정했다'},
             {'title': '배포 후 실제 주소에서 핵심 기능을 한 번 눌러 봤다', 'detail': '"배포 성공" 표시가 아니라 화면에서 확인합니다.'}],
             'done': '배포 준비가 끝났습니다.', 'next': '문제가 생기면 다음 장(디버깅)의 에러 읽는 순서로 돌아오세요.'}),
    dict(file='index.html', before='제7장 : AI 비서와', id='lab-v2-ch6', type='choice', minutes=3,
         title='잘 되던 기능을 지키는 지시법', goal='범위·확인·복원 판단 3개',
         easy='파일 통제가 무너지는 순간은 대개 지시 한 줄에서 시작됩니다.',
         data={'steps': [
             {'q': '로그인 버튼 색만 바꾸고 싶습니다. 어떻게 지시할까요?', 'options': [
                 O('"디자인 좀 더 예쁘게 해 줘"', False, 'AI가 범위를 스스로 정합니다. 다른 화면까지 바뀝니다.'),
                 O('"login.html의 로그인 버튼 배경색만 #2563eb로 바꿔. 다른 파일과 다른 요소는 건드리지 마."', True, '파일·요소·값·금지가 모두 들어 있습니다.')]},
             {'q': 'AI가 "완료했습니다"라고 했는데 바뀐 파일이 3개입니다.', 'options': [
                 O('결과 화면이 괜찮으면 넘어간다', False, '보이지 않는 곳의 변경이 나중에 문제를 만듭니다.'),
                 O('git diff로 바뀐 내용을 보고, 요청과 무관한 변경은 되돌린다', True, '변경 기록을 보는 습관이 파일 통제의 시작입니다.')]},
             {'q': '수정 후 잘 되던 결제 버튼이 안 눌립니다. 30분째 AI와 고치는 중입니다.', 'options': [
                 O('될 때까지 계속 수정을 요청한다', False, '고칠수록 원래 상태에서 멀어집니다.'),
                 O('마지막으로 정상이던 커밋으로 되돌린 뒤, 바꾸려던 것만 작게 다시 시도한다', True, '되돌리기가 고치기보다 빠를 때가 많습니다.')]}],
             'results': [{'min': 3, 'title': '파일 통제 합격', 'text': '범위를 좁히고, 변경을 확인하고, 필요하면 되돌릴 줄 압니다.'}, {'min': 0, 'title': '한 번 더', 'text': '틀린 장면의 이유를 다시 읽어 보세요.'}],
             'takeaway': '작게 지시하고, 바뀐 것을 보고, 망가지면 되돌린다.'}),
    dict(file='index.html', before='제14장 : 파이프라인', id='lab-v2-ch13', type='sort', minutes=4,
         title='어떤 일에 어떤 모델을 쓸까', goal='작업 6개를 모델 등급에 배치',
         easy='이 장의 "모델 등급 3단계"를 내 업무에 적용해 봅니다. 정답은 하나가 아니지만, 이유를 설명할 수 있어야 합니다.',
         data={'levels': [
             {'id': 'small', 'label': '작고 빠른 모델 (Haiku급)', 'desc': '분류·추출·짧은 응답, 대량'},
             {'id': 'mid', 'label': '중간 모델 (Sonnet급)', 'desc': '글쓰기·코드·분석 대부분'},
             {'id': 'large', 'label': '큰 모델 (Opus급 이상)', 'desc': '어렵고 틀리면 비싼 판단'}],
             'question': '각 작업에 알맞은 등급을 고르세요.',
             'items': [
                 {'text': '고객 문의 1,000건을 "배송/환불/기타"로 분류', 'answer': 'small', 'why': '정해진 칸에 넣는 일입니다. 양이 많아 단가가 중요합니다.'},
                 {'text': '스팸 댓글 걸러내기', 'answer': 'small', 'why': '짧고 반복적인 판정입니다.'},
                 {'text': '블로그 초안 10편 쓰기', 'answer': 'mid', 'why': '품질이 필요하지만 매번 최고 모델일 필요는 없습니다.'},
                 {'text': '버그 원인 찾고 수정 코드 작성', 'answer': 'mid', 'why': '대부분의 코드 작업은 중간 모델로 충분합니다. 막히면 올립니다.'},
                 {'text': '여러 파일에 걸친 구조 변경 설계', 'answer': 'large', 'why': '한 번 틀리면 되돌리는 비용이 큽니다.'},
                 {'text': '계약 조건 비교와 위험 검토 (최종 판단은 사람)', 'answer': 'large', 'why': '놓친 조건 하나가 비쌉니다. 그래도 결정은 사람이 합니다.'}],
             'takeaway': '모델을 올리기 전에 캐시와 짧은 출력부터. 등급은 "틀렸을 때 비용"으로 고른다.'}),
    # ---------------- volume 3
    dict(file='agent-bible.html', before='STEP 3 — 10분 만에', id='lab-v3-react', type='choice', minutes=3,
         title='ReAct 한 바퀴 직접 돌리기', goal='생각 → 행동 → 관찰을 직접 선택',
         easy='"내일 서울에서 우산을 챙길까?"라는 질문을 받은 에이전트가 되어 다음 행동을 고르세요.',
         data={'steps': [
             {'context': 'Thought: 내일 서울 날씨를 알아야 한다. 사용 가능한 도구: get_weather(city, date)', 'q': '다음 Action은?', 'options': [
                 O('학습한 지식으로 "아마 맑을 거예요"라고 답한다', False, '모델은 내일 날씨를 모릅니다. 도구가 있는데 쓰지 않으면 지어내게 됩니다.'),
                 O('get_weather("서울", "내일")을 호출한다', True, '필요한 정보가 없으면 도구로 관찰합니다. 이것이 ReAct의 Action입니다.')]},
             {'context': 'Observation: 강수확률 70%, 오후 3시부터 비', 'q': '다음은?', 'options': [
                 O('정확성을 위해 같은 도구를 5번 더 호출한다', False, '같은 결과를 반복해서 받으면 비용만 듭니다. 루프가 끝나지 않는 대표적인 원인입니다.'),
                 O('Thought: 비 올 확률이 높다 → 답: "오후부터 비 예보(70%)라 우산을 챙기세요"', True, '관찰이 충분하면 멈추고 답합니다. 근거(70%)를 함께 말합니다.')]},
             {'context': 'Observation: get_weather 오류 — timeout', 'q': '도구가 실패했습니다. 어떻게 할까요?', 'options': [
                 O('"비 소식은 없습니다"라고 답한다', False, '관찰하지 못한 것을 사실처럼 말하면 가장 위험한 실패입니다.'),
                 O('정해진 횟수만 재시도하고, 그래도 실패하면 "확인하지 못했다"고 알린다', True, '재시도 한도와 정직한 실패 보고가 에이전트의 기본기입니다.')]}],
             'results': [{'min': 3, 'title': 'ReAct 합격', 'text': '모르면 관찰하고, 충분하면 멈추고, 실패하면 정직하게 말합니다.'}, {'min': 0, 'title': '한 번 더', 'text': '틀린 장면의 이유를 다시 읽어 보세요.'}],
             'takeaway': '도구가 있으면 지어내지 말고 관찰한다. 관찰이 충분하면 멈춘다. 실패는 숨기지 않는다.'}),
    dict(file='agent-bible.html', before='STEP 6a — HITL', id='lab-v3-memory', type='sort', minutes=4,
         title='이 정보는 어디에 기억할까', goal='정보 6개를 기억 4종류에 배치',
         easy='이 장의 기억 4종류를 실제 상황에 적용해 봅니다.',
         data={'levels': [
             {'id': 'ctx', 'label': '컨텍스트', 'desc': '이번 대화 안에서만'},
             {'id': 'file', 'label': '파일(JSON)', 'desc': '재시작해도 남는 작은 상태'},
             {'id': 'db', 'label': 'DB(SQLite)', 'desc': '많은 기록을 조건으로 조회'},
             {'id': 'vec', 'label': '벡터DB', 'desc': '"비슷한 내용" 찾기'}],
             'question': '각 정보에 알맞은 기억 방식을 고르세요.',
             'items': [
                 {'text': '방금 사용자가 "내 이름은 민수야"라고 말함', 'answer': 'ctx', 'why': '이 대화 안에서만 쓰면 됩니다.'},
                 {'text': '봇이 마지막으로 처리한 뉴스 ID', 'answer': 'file', 'why': '작은 값 하나, 재시작 후에도 이어 가야 합니다.'},
                 {'text': '알림 받을 시간 같은 설정값 몇 개', 'answer': 'file', 'why': '자주 바뀌지 않는 작은 설정입니다.'},
                 {'text': '고객 3,000명의 주문 이력에서 "지난달 2회 이상 구매" 찾기', 'answer': 'db', 'why': '조건으로 정확히 조회하는 일은 DB가 맞습니다.'},
                 {'text': '월별 매출 합계 계산', 'answer': 'db', 'why': '집계와 계산은 DB 쿼리로 정확하게 합니다.'},
                 {'text': '"환불 관련 문의와 비슷한 과거 답변" 찾기', 'answer': 'vec', 'why': '단어가 달라도 의미가 비슷한 것을 찾는 일입니다.'}],
             'takeaway': '정확히 찾으면 DB, 비슷한 것을 찾으면 벡터DB, 작은 상태는 파일, 지금 대화는 컨텍스트.'}),
    # ---------------- volume 4
    dict(file='claude-code-bible.html', before='MCP — 슈퍼파워', id='lab-v4-claudemd', type='builder', minutes=7,
         title='내 프로젝트 CLAUDE.md 조립기', goal='프로젝트 지침 파일 초안 완성',
         easy='이 장의 황금 템플릿을 내 프로젝트로 채워 봅니다. 완성된 내용을 프로젝트 루트의 CLAUDE.md에 붙여 넣으세요.',
         data={'fields': [
             F('what', '프로젝트 설명 — 무엇이고 누가 쓰나', '동네 꽃집 예약 페이지. 사장 1명과 손님이 휴대폰으로 사용'),
             F('stack', '구조와 실행 방법', 'index.html + app.js + style.css. 로컬 확인은 브라우저로 index.html 열기'),
             F('rules', '작업 규칙', '수정 전에 계획을 먼저 보여 준다. 한 번에 한 기능만 바꾼다. 변경 후 바뀐 파일 목록을 알려 준다'),
             F('deny', '절대 건드리지 말 것', '.env, payment/ 폴더, 이미 배포된 주소의 경로 구조'),
             F('done', '완료 기준', '휴대폰 화면에서 가로 넘침 없음, 예약 버튼 눌렀을 때 확인 문구 표시, 콘솔 에러 0개')],
             'checks': None, 'footer': '## 주의\n이 파일은 매 대화에 읽히는 지침이지 강제 장치가 아니다. 반드시 막아야 할 것은 권한 설정이나 훅으로 막는다.'}),
    dict(file='claude-code-bible.html', before='Subagents — AI 팀', id='lab-v4-hooks', type='sort', minutes=4,
         title='이 일은 어떤 훅에 걸까', goal='자동화 6개를 훅 이벤트에 배치',
         easy='훅은 "언제" 실행되느냐가 전부입니다. 각 자동화를 알맞은 시점에 연결해 보세요.',
         data={'levels': [
             {'id': 'pre', 'label': 'PreToolUse', 'desc': '도구 실행 직전'},
             {'id': 'post', 'label': 'PostToolUse', 'desc': '도구 실행 직후'},
             {'id': 'stop', 'label': 'Stop', 'desc': '응답이 끝났을 때'},
             {'id': 'notif', 'label': 'Notification', 'desc': '알림이 발생할 때'},
             {'id': 'prompt', 'label': 'UserPromptSubmit', 'desc': '내가 입력을 보낼 때'},
             {'id': 'start', 'label': 'SessionStart', 'desc': '세션을 시작할 때'}],
             'question': '각 자동화에 알맞은 훅을 고르세요.',
             'items': [
                 {'text': 'rm -rf 같은 위험 명령을 실행 전에 막기', 'answer': 'pre', 'why': '실행된 뒤에는 늦습니다. 직전에 막아야 합니다.'},
                 {'text': '파일을 수정할 때마다 린트·테스트 돌리기', 'answer': 'post', 'why': '수정이 끝난 직후가 검사할 시점입니다.'},
                 {'text': '작업이 끝나면 소리로 알려 주기', 'answer': 'stop', 'why': '응답이 끝났을 때 한 번 실행됩니다.'},
                 {'text': '권한 확인 요청이 오면 메신저로 알림 보내기', 'answer': 'notif', 'why': 'Claude가 확인을 기다릴 때 발생하는 알림에 연결합니다.'},
                 {'text': '내가 보낸 메시지에 API 키 같은 비밀값이 있는지 검사', 'answer': 'prompt', 'why': '입력이 모델에 전달되기 전에 걸러야 합니다.'},
                 {'text': '시작할 때 오늘의 작업 메모와 git 상태 불러오기', 'answer': 'start', 'why': '세션 시작 시점에 맥락을 넣어 줍니다.'}],
             'takeaway': '막을 일은 Pre, 확인할 일은 Post, 알릴 일은 Stop·Notification.'}),
    dict(file='claude-code-bible.html', before='비용 절약 · VS Code', id='lab-v4-mistakes', type='choice', minutes=4,
         title='실수 12가지 — 이 장면이면?', goal='실수가 시작되는 순간 4개 판단',
         easy='12가지 실수는 대부분 "이 정도는 괜찮겠지"에서 시작됩니다. 그 순간을 골라 봤습니다.',
         data={'steps': [
             {'q': '로그인 기능을 끝냈습니다. 이어서 같은 창에서 결제 기능을 시작하려 합니다.', 'options': [
                 O('맥락이 이어지니 그대로 시작한다', False, '이전 작업의 맥락이 새 작업 판단을 흐립니다(실수 #2).'),
                 O('커밋한 뒤 /clear로 비우고 새 작업을 시작한다', True, '독립 작업은 깨끗한 컨텍스트에서. 필요한 맥락은 CLAUDE.md와 작업 메모로 넘깁니다.')]},
             {'q': '같은 에러로 Claude가 세 번째 같은 수정을 시도하고 있습니다.', 'options': [
                 O('언젠가는 맞히겠지 기다린다', False, '루프에 빠진 상태입니다(실수 #10). 토큰만 쓰입니다.'),
                 O('멈추고, 지금까지 시도한 것과 결과를 정리하게 한 뒤 다른 접근을 묻는다', True, '멈추고 정리하는 것이 루프를 끊는 가장 빠른 방법입니다.')]},
             {'q': '테스트를 위해 API 키를 코드에 잠깐 넣었습니다. 이제 커밋하려 합니다.', 'options': [
                 O('나중에 지우면 되니 커밋한다', False, '한 번 커밋된 키는 이력에 남습니다(실수 #4). 이미 올렸다면 키를 폐기하고 새로 발급하세요.'),
                 O('키를 .env로 옮기고 .gitignore를 확인한 뒤 커밋한다', True, '비밀값은 코드 밖에 둡니다.')]},
             {'q': 'Claude가 "이 라이브러리는 최신 버전에서 이 함수를 지원합니다"라고 합니다.', 'options': [
                 O('Claude가 말했으니 그대로 쓴다', False, '라이브러리 정보는 학습 시점 이후 바뀌었을 수 있습니다(실수 #12).'),
                 O('공식 문서나 설치된 버전에서 직접 확인한다', True, '중요한 결정은 공식 문서와 대조합니다.')]}],
             'results': [{'min': 4, 'title': '실수 예방 합격', 'text': '실수가 시작되는 순간을 알아보는 눈이 있습니다.'}, {'min': 2, 'title': '거의 다 왔습니다', 'text': '틀린 장면의 실수 번호를 본문에서 다시 읽어 보세요.'}, {'min': 0, 'title': '한 번 더', 'text': '이 장의 12가지를 한 번 더 훑고 다시 풀어 보세요.'}],
             'takeaway': '새 작업은 새 컨텍스트, 반복되면 멈춤, 비밀은 코드 밖, 중요한 사실은 공식 문서.'}),
    # ---------------- volume 5
    dict(file='practical-bible.html', before='30 에이전트 따로 놀면', id='lab-v5-decision', type='builder', minutes=5,
         title='결정 로그 한 건 쓰기', goal='나중에 다시 꺼내 볼 수 있는 결정 기록 1건',
         easy='이 장의 결정 로그를 우리 팀 결정 하나로 써 봅니다. 사람이 쓰든 AI가 정리하든 칸은 같습니다.',
         data={'fields': [
             F('what', '결정 — 무엇을 정했나', '고객 문의 1차 답변을 AI 초안 + 담당자 확인 방식으로 바꾼다'),
             F('why', '이유와 근거', '지난달 문의 420건 중 70%가 배송 조회. 평균 첫 답변 시간이 6시간'),
             F('alt', '검토했지만 버린 안', 'AI 자동 발송 — 환불 문의에 잘못 답할 위험 때문에 제외'),
             F('who', '결정한 사람과 실행 담당', '결정: 대표 / 실행: CS 담당 이 매니저'),
             F('check', '언제 다시 볼지와 되돌리는 기준', '12월 1일 재검토. 잘못된 답변 2건 이상이면 이전 방식으로 복귀')],
             'checks': None, 'footer': '## 보관\n결정 로그 폴더(노션·드라이브·디스코드 등 한 곳)에 날짜를 제목으로 저장한다.'}),
    dict(file='practical-bible.html', before='Webhook — 이벤트로', id='lab-v5-pm2', type='choice', minutes=3,
         title='새벽에 봇이 멈췄다', goal='24시간 자동화가 멈췄을 때의 판단 3개',
         easy='아침에 보니 밤사이 돌아야 할 보고서가 없습니다. 이 장의 PM2와 Cron으로 어떻게 대응할까요?',
         data={'steps': [
             {'q': '가장 먼저 무엇을 볼까요?', 'options': [
                 O('일단 코드를 고친다', False, '원인을 모르고 고치면 다른 곳이 망가집니다.'),
                 O('pm2 status와 pm2 logs로 프로세스 상태와 마지막 에러를 본다', True, '살아 있는지, 언제 왜 죽었는지부터 확인합니다.')]},
             {'q': '로그를 보니 밤 2시에 메모리 부족으로 죽은 뒤 다시 살아나지 않았습니다.', 'options': [
                 O('매일 아침 사람이 수동으로 재시작한다', False, '사람이 단일 장애점이 됩니다. 이 장이 깨려는 바로 그 구조입니다.'),
                 O('자동 재시작 설정과 메모리 상한 재시작을 걸고, 재시작이 일어나면 알림을 받게 한다', True, '죽으면 살리고, 살렸다는 사실은 사람이 알게 합니다.')]},
             {'q': '재발 방지까지 했습니다. 마지막으로 남길 것은?', 'options': [
                 O('잘 돌아가니 아무것도 안 남긴다', False, '같은 일이 생기면 처음부터 다시 찾아야 합니다.'),
                 O('원인·조치·확인 방법을 결정 로그와 실수 기록에 남긴다', True, '기록이 쌓이면 다음 장애는 몇 분 만에 끝납니다.')]}],
             'results': [{'min': 3, 'title': '운영 합격', 'text': '확인 → 자동 복구 → 알림 → 기록의 순서가 잡혀 있습니다.'}, {'min': 0, 'title': '한 번 더', 'text': '틀린 장면의 이유를 다시 읽어 보세요.'}],
             'takeaway': '24시간 자동화의 조건은 "죽지 않는 것"이 아니라 "죽으면 살아나고, 사람이 아는 것".'}),
]


def block(c):
    d = dict(c['data'])
    if c['type'] == 'builder' and d.get('checks') is None:
        d['checks'] = checks_for(d['fields'])
    blob = json.dumps(d, ensure_ascii=False).replace('</', '<\\/')
    return (f'<section class="aib-lab" data-lab="{c["type"]}" id="{c["id"]}" aria-labelledby="{c["id"]}-t">\n'
            f'<p class="lab-kicker">본문 실습 · 이 장을 바로 써 보기</p><h2 id="{c["id"]}-t">{E(c["title"])}</h2>\n'
            f'<p class="lab-meta"><span>⏱ {c["minutes"]}분</span><span>🎯 {E(c["goal"])}</span></p>\n'
            f'<p>{E(c["easy"])}</p>\n<div class="lab-mount"></div>\n'
            f'<script type="application/json" class="lab-data">{blob}</script>\n</section>\n')


def insert_pos(t, heading):
    ms = list(re.finditer(r'<h[12][^>]*>(?:(?!</h[12]>).)*?' + re.escape(heading), t, re.S))
    if not ms:
        raise SystemExit('heading not found: ' + heading)
    s = ms[-1].start()
    sec = t.rfind('<section', 0, s)
    if sec != -1 and s - sec < 700:
        return t.rfind('</section>', 0, sec)
    for marker in ('<!--', '<hr'):
        m = t.rfind(marker, 0, s)
        if m != -1 and s - m < 120:
            s = m
    hr = t.rfind('<hr', 0, s)
    return hr if hr != -1 and s - hr < 160 else s


def main():
    for c in LABS:
        p = ROOT / c['file']
        t = p.read_text(encoding='utf-8')
        t = re.sub(r'<section class="aib-lab"[^>]*id="' + c['id'] + r'".*?</section>\n', '', t, flags=re.S)
        pos = insert_pos(t, c['before'])
        t = t[:pos] + block(c) + t[pos:]
        p.write_text(t, encoding='utf-8')
        print('lab', c['id'], '->', c['file'])


if __name__ == '__main__':
    main()
