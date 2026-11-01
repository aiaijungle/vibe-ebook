"""Add reader guides without touching author prose: volume 2 reading paths, volume 5 glossary.
Idempotent. Run: python scripts/build_reading_guides.py"""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def links(items):
    return ' → '.join(f'<a href="#{i}">{t}</a>' for i, t in items)

V2 = f'''<section class="aib-update aib-guide" id="aib-v2-paths" aria-labelledby="aib-v2-paths-t">
<p class="aib-kicker">2권 읽는 순서</p><h2 id="aib-v2-paths-t">처음엔 필수 경로만, 나머지는 필요할 때</h2>
<p>이 책은 72일 동안 쓴 기록을 쌓은 책이라 장 번호와 읽기 좋은 순서가 다릅니다(19장이 20장 뒤에 나옵니다). 처음 읽는다면 아래 <strong>필수 경로</strong>만으로 작은 도구 하나를 만들고 고치고 공개할 수 있습니다.</p>
<h3>필수 경로 — 작은 도구 하나 완성 (약 6~8시간)</h3>
<p>{links([('section-21','생존 키트'),('section-25','1장 실화'),('section-29','2장 설치'),('section-30','설치 체크리스트'),('section-37','3장 G-Stack'),('section-ch4','4장 배포'),('section-ch5','5장 디버깅'),('section-42','6장 파일 통제')])}</p>
<h3>막혔을 때 펴는 참고</h3>
<p>{links([('section-11','상황별 빠른 찾기'),('section-47','7장 용어 사전'),('section-137','부록 D 개념 50선'),('section-136','부록 C 프롬프트 15선'),('section-121','부록 B 실수 기록')])}</p>
<h3>선택 경로 — 필수 경로를 끝낸 뒤 목적에 따라</h3>
<p><strong>A. 비용과 실력</strong><br>{links([('section-74','13장 토큰 절약'),('section-122','19장 마스터 클래스'),('section-116','20장 3대 무기'),('section-160','심화 3 비용·속도'),('section-167','심화 4 공식문서 검증')])}</p>
<p><strong>B. 판매와 사업</strong><br>{links([('section-48','8장 실무 프롬프트'),('section-49','9장 비용·운영 실수'),('section-55','10장 생존 체크리스트'),('section-59','11장 도구 목록'),('section-66','12장 AITF'),('section-148','특별 부록 지식창업'),('section-154','심화 2 전자책 항해')])}</p>
<p><strong>C. 에이전트와 운영</strong> — 3권으로 이어집니다<br>{links([('section-89','15장 에이전트 팀'),('section-94','16장 보안'),('section-129','21장 운영 일지'),('section-144','부록 E 작업공유 MD')])}</p>
<p><strong>저자의 기록으로 읽기</strong><br>{links([('section-78','14장 72일 일지'),('section-102','17장 7가지 편견'),('section-110','18장 오토파일럿'),('section-72','에필로그')])}</p>
<p class="aib-small">필수 경로를 끝냈다면 <a href="first-win.html#kit-2-steps">30분 첫 성공 키트</a>로 같은 과정을 내 업무에 한 번 더 적용해 보세요.</p>
</section>
'''

TERMS = [
    ('리미트리스맨', '저자 김화현의 필명입니다. 회사 잔다(JANDA)를 운영합니다.'),
    ('잔다 (JANDA)', '저자가 운영하는 회사입니다. 이 책 사례 대부분의 출처이며, "JANDA 실측"은 이 회사에서 직접 잰 기록을 뜻합니다.'),
    ('시황 (Sihwang)', '잔다의 AI 운영 에이전트 이름입니다. 공저자로 표기되며, 18개 도구를 써서 회사 업무를 처리합니다. 매일 밤 자기 코드를 고치는 자가코딩 루프는 4권에도 나옵니다.'),
    ('강.1 ~ 강.18', '이 책의 강의 번호입니다. "강.12"는 12강을 뜻합니다.'),
    ('6 도메인', '책의 6개 큰 단원입니다. 데이터 · AI 활용 · 자동화 · AI 에이전트 · 디스코드 · 오케스트라 순서로 익힙니다.'),
    ('Bridge', '도메인과 도메인 사이를 잇는 짧은 연결 장입니다. 앞 단원에서 생긴 문제가 다음 단원으로 왜 이어지는지 설명합니다.'),
    ('AITF (AI Team Flow)', '저자가 만든 AI 플랫폼과 API 상품군 이름입니다. 2권 12장에서 처음 소개됩니다.'),
    ('18 tool', '시황이 쓰는 도구 18개입니다. 노션 페이지 만들기처럼 도구 이름이 곧 하는 일입니다.'),
    ('silent_activator', '사람이 시키지 않아도 정해진 시각에 스스로 일을 시작하는 작업자(워커)입니다. 잔다에서는 5개가 매일 일을 만듭니다.'),
    ('L0 ~ L4', 'AI에게 주는 권한 단계입니다. L0 읽기 · L1 정해진 반복 · L2 사람 클릭 승인 · L3 강한 확인 · L4 사람 전용.'),
    ('PIN', 'L3 작업을 실행하기 직전에 사람이 직접 입력하는 확인 문자입니다. 실수로 버튼을 누르는 일을 막습니다.'),
    ('PM2 · Cron', 'PM2는 프로그램이 죽으면 다시 살리는 관리 도구, Cron은 정해진 시각에 작업을 실행하는 예약 도구입니다.'),
    ('Webhook', '어떤 일이 생기면 다른 시스템에 바로 알려 주는 연결입니다. 기다리지 않고 이벤트로 깨웁니다.'),
    ('MCP', 'Claude를 노션·깃허브·DB 같은 외부 도구에 연결하는 표준 방식입니다.'),
    ('Code · API · Cowork', 'Claude를 쓰는 세 방식입니다. Claude Code는 코드를 만들고, API는 프로그램에서 호출하고, Cowork는 그 시스템으로 업무를 운영합니다.'),
    ('Reflexion', 'AI가 자기 답을 비평하고 다시 쓰게 하는 기법입니다. 비평을 반복한다고 항상 좋아지지는 않아, 같은 기준으로 확인합니다.'),
    ('SPOF', '단일 장애점입니다. 그것 하나가 멈추면 전체가 멈추는 지점입니다. 사장이 SPOF가 되는 것이 이 책이 가장 경계하는 상태입니다.'),
    ('오케스트레이션', '여러 에이전트가 따로 놀지 않도록 지휘자 역할이 순서와 담당을 조율하는 것입니다.'),
    ('AI하우스', '잔다가 운영하는 사장 정기 모임입니다. 새로운 도메인(업계 지식)을 사람에게서 얻는 자리로 소개됩니다.'),
    ('알집', '5권 마스터 상품에 포함된 AI 도구 10종 빌드키트입니다.'),
]

V5 = ('<section class="aib-update aib-guide" id="aib-v5-glossary" aria-labelledby="aib-v5-glossary-t">\n'
      '<p class="aib-kicker">5권 용어집</p><h2 id="aib-v5-glossary-t">처음 보는 이름이 나오면 여기서 확인하세요</h2>\n'
      '<p>이 책은 저자 회사에서 실제로 쓰는 이름을 그대로 씁니다. 본문은 바꾸지 않고, 자주 나오는 이름만 모았습니다.</p>\n<dl class="aib-glossary">'
      + ''.join(f'<dt>{t}</dt><dd>{d}</dd>' for t, d in TERMS) + '</dl>\n</section>\n')

CSS = ('<style id="aib-guide-style">.aib-guide h3{margin:22px 0 6px}.aib-guide p a{white-space:normal}'
       '.aib-glossary{margin:12px 0}.aib-glossary dt{font-weight:800;margin-top:12px}.aib-glossary dd{margin:2px 0 0;line-height:1.75}</style>\n')

def put(name, after_id, sec_id, block):
    p = ROOT / name; t = p.read_text(encoding='utf-8')
    t = re.sub(r'<section class="aib-update aib-guide" id="' + sec_id + r'".*?</section>\n', '', t, flags=re.S)
    i = t.index('id="' + after_id + '"'); e = t.index('</section>', i) + len('</section>')
    t = t[:e] + '\n' + block + t[e:]
    if 'id="aib-guide-style"' not in t:
        t = t.replace('</head>', CSS + '</head>', 1)
    p.write_text(t, encoding='utf-8'); print('guide', sec_id, '->', name)

put('index.html', 'aib-lab-v2', 'aib-v2-paths', V2)
put('practical-bible.html', 'aib-lab-v5', 'aib-v5-glossary', V5)
