# 자산 목록 및 점검 결과

2026-10-31 기준 · 저장소 전체 162개 파일(약 20MB, `.git` 제외)을 점검했다. 모든 HTML·CSS·JS·XML·TXT의 로컬 참조(`src`, `href`, `url()`, 공개 사이트 절대 URL)를 실제 파일과 대조하고, `sitemap.xml`·중복 파일·참조되지 않는 파일을 확인했다.

## 1. 요약

| 항목 | 결과 |
|---|---|
| 실제 깨진 링크 | 6곳 발견, **이번에 모두 수정** (아래 3절) |
| 중복 파일(동일 해시) | 없음 |
| sitemap 등록 URL 37개 | 모두 실제 파일 존재 |
| 참조 없는 공개 자산 | PDF 2개, 내부 초안 HTML 7개 (4절) |
| 인라인 스크립트 문법 (`scripts/verify_inline_scripts.py`) | 90개 통과 |
| 독자 통계 테스트 (`tests/reader-stats.test.cjs`) | 통과 |
| 실습 압축 검증 (`scripts/verify_exercise_archives.py`) | **실패**: 줄바꿈(CRLF) 차이, 내용은 같음 (5절) |

## 2. 분류별 목록

### 2.1 독서기 본문 (유료/무료 권)

| 권 | 한국어 | 영어 | 일본어 |
|---|---|---|---|
| 1권 마케팅 | `book1.html` (205KB) | `en/book1.html` | – |
| 2권 바이브 코딩 | `index.html` (919KB) | `en/index.html` | `ja/index.html` |
| 3권 에이전트 | `agent-bible.html` (424KB) | `en/agent-bible.html` | – |
| 4권 Claude Code | `claude-code-bible.html` (281KB) | `en/claude-code-bible.html` | – |
| 5권 실무 운영 | `practical-bible.html` (479KB) | `en/practical-bible.html` | `ja/practical-bible.html` |
| 별권 육아 | `parenting/index.html` (+ `cover.png` 1.3MB, `family.jpg` 541KB) | – | – |

영어 실습 동반 페이지: `en/practice/volume-1.html` ~ `volume-5.html`

### 2.2 판매·안내·SEO 랜딩 페이지

- 판매/결제: `sales.html`, `en/sales.html`, `checkout.html`, `ai-bible.html`, `en/ai-bible-global.html`, `en/media-kit.html`
- 시작 안내: `start-here.html`, `free-ai-bible-checklist.html`, `ai-level-test.html`
- 국문 주제 랜딩(SEO): `learn-ai`, `vibe-coding`, `ai-agent`, `claude-code`, `ai-side-hustle`, `ai-orchestration`, `ai-video-ad-automation`, `ai-work-automation`, `aeo-geo`, `ai-prompt-engineering`, `n8n-automation`, `ai-copywriting`, `chatgpt-business-use`, `ai-report-automation` (각 `.html`)
- 영문 주제 랜딩: `en/learn-ai-for-solo-operators`, `en/ai-automation-for-solo-business`, `en/ai-agent-workflow`, `en/prompt-to-workflow`, `en/ai-orchestration`, `en/ai-video-ad-automation`, `en/first-workflow` (각 `.html`)
- 크롤러용: `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, `googlec39b6d91bbb5378e.html`(Search Console 인증), `.nojekyll`

### 2.3 이미지

| 파일 | 크기 | 사용처 |
|---|---|---|
| `assets/og-1200x630.png` | 462KB | 국문·영문 권 대부분의 OG/트위터 이미지 |
| `assets/bible_cover.png` | 894KB | 1·2·3·4·5권 표지, 카카오 공유 |
| `telegram_ai_hub.png` | 925KB | 2권 본문 |
| `assets/proof/ax-lecture-1.jpg`, `ax-lecture-2.jpg`, `consulting-santa.jpg` | 232/259/138KB | 1권 저자 신뢰 자료 |
| `parenting/cover.png`, `parenting/family.jpg` | 1.3MB / 541KB | 육아 별권 |

### 2.4 PDF 배포물

| 파일 | 크기 | 연결 |
|---|---|---|
| `AI_Bible_Free_7Day_Checklist.pdf` | 1.3MB | 1~5권, 체크리스트 랜딩, 영문 랜딩, `llms.txt` |
| `AI_One_Sentence_System_Leadmagnet.pdf` | 727KB | 1권(국/영) 리드마그넷 버튼 |
| `AI_Agent_Bible_AITF2026.pdf` | 5.8MB, 8쪽 | `generate_pdf.py` 출력물, 페이지 링크 없음 |
| `vibe-ebook-2-teaser.pdf` | 1.5MB, 6쪽 | **어디에도 연결 없음** |
| `리드마그넷_AI한문장시스템.pdf` | 316KB, 4쪽 | **어디에도 연결 없음** (영문명 PDF의 이전 판으로 보임) |
| `AI에이전트바이블_AITF2026.pdf` | 10KB, 1쪽 | **어디에도 연결 없음** (영문명 PDF의 1쪽 시안으로 보임) |

### 2.5 공통 CSS·JS (`assets/`)

| 파일 | 역할 | 로드 방식 |
|---|---|---|
| `updates-20261025.css/.js` | 국문 2026.10 업데이트 노트 패널 | 각 권 HTML |
| `global-updates-20261025.css/.js` | 영문 업데이트 노트 | 영문 권 HTML |
| `reader-stats-20261026.css/.js` | 실측 방문자·현재 독자 표시 | 각 권 HTML |
| `practical-mobile-20261026.css/.js` | 5권 모바일 UI | `updates-20261025.js`가 동적 주입 |
| `reader-sharing-20261031.js` | 인증 쿼리 제거 공유 모듈 | 각 권 HTML |
| `learning-edition-20261031.css` | 실습판 공통 스타일 | 각 권 HTML |
| `ai-hunter-videos.css` | 영상 카드 | 각 권 HTML |
| `global-edition.css`, `en/edition-guide.css` | 영문판 공통 | 영문 페이지 |

### 2.6 독자 실습 자료 (`examples/`)

| 폴더 | 다운로드 압축 | 대상 |
|---|---|---|
| `learning-edition/` | `volume2-starter.zip` (6KB) | 2권 온톨로지 스타터 |
| `agent-ontology/` | – (검증 원본) | 2·3권 공통 실습 |
| `claude-code-checks/` | `reader-checks.zip` (5KB) | 4권 |
| `operations-edition/` | `operations-practice.zip` (9KB) | 5권 |
| `work-completion-kit/` | `work-completion-kit.zip` (59KB) + `workbench.html` | 전권 업무 완성 키트 |

### 2.7 운영·개발 파일 (독자에게 노출 불필요)

- 서버: `supabase/functions/ai-bible-reader-stats/` (독자 통계 Edge Function)
- 검증/빌드: `scripts/*` 8개, `tests/reader-stats.test.cjs`, `generate_pdf.py`
- 편집 기록: `QUALITY_AUDIT_20261031.md`, `EDITORIAL_RELEASE_20261031.md`, `release-20261031.json`, `updates/*.md` 4개
- 내부 초안 HTML(sitemap 미등록, 링크 없음): `_feature1_reactions.html`, `_feature2_messages.html`, `_feature3_completion.html`, `_feature_quiz.html`, `_teaser_2권.html`, `_print_agent_bible.html`(PDF 인쇄용), `checkout-sandbox.html`
- 브라우저 점검 로그: `.gstack/browse-console.log`, `.gstack/browse-network.log` (git에 추적되고 있음)

## 3. 이번에 수정한 깨진 링크

| 파일 | 문제 | 수정 |
|---|---|---|
| `en/book1.html` | 리드마그넷 PDF를 `en/` 안에서 찾음 → 404 | `../AI_One_Sentence_System_Leadmagnet.pdf` |
| `ja/index.html` | 표지를 `ja/assets/`에서 찾음 → 이미지 깨짐 | `../assets/bible_cover.png` |
| `en/practical-bible.html` | OG·트위터 이미지 `og-practical.png` 없음 | `assets/og-1200x630.png` (국문판과 동일) |
| `en/agent-bible.html` | OG 이미지 `img/agent_bible_og.png` 없음 | 동일 |
| `en/claude-code-bible.html` | OG 이미지 `og-claude-code.png` 없음 | 동일 |

참고: 자동 검사에 걸렸지만 실제 문제가 아닌 항목 — `blog_2026.html`(코드 예시 속 문자열), `certificate.png`·`AI-Bible-Certificate.png`(브라우저에서 생성하는 다운로드 파일명), `assets/*.js` 안의 페이지 경로(페이지 기준으로 정상 해석됨).

## 4. 정리 권장 (삭제·변경은 하지 않음)

1. **연결 없는 PDF 3개** (`vibe-ebook-2-teaser.pdf`, `리드마그넷_AI한문장시스템.pdf`, `AI에이전트바이블_AITF2026.pdf`, 합계 약 1.8MB): 공개 URL로 이미 배포된 적이 있다면 외부 링크 보호를 위해 유지, 아니라면 삭제 검토.
2. **`AI_Agent_Bible_AITF2026.pdf` (5.8MB, 8쪽)와 `_print_agent_bible.html` (538KB)**: `generate_pdf.py`가 3권 본문으로 만드는 인쇄용 파일이며 페이지에서 링크되지 않는다. 특히 인쇄용 HTML은 잠금 장치 없이 본문을 담고 있어 URL만 알면 누구나 열 수 있다. **유료 콘텐츠 노출 여부를 우선 확인**할 것 (각 권 본문도 클라이언트 측 잠금이라 원문 자체는 공개 저장소에 있다는 점은 동일).
3. **내부 초안 HTML 7개**: GitHub Pages에서 URL만 알면 열린다. 공개가 필요 없으면 별도 폴더로 옮기거나 삭제 검토. `checkout-sandbox.html`은 결제 시험 페이지이므로 특히 확인 필요.
4. **`.gstack/` 로그**: `.gitignore`에 `.gstack/` 추가 후 추적 해제 권장.
5. **이미지 용량**: `telegram_ai_hub.png`(925KB), `assets/bible_cover.png`(894KB), `parenting/cover.png`(1.3MB)는 WebP/JPEG 변환 시 크게 줄일 수 있어 모바일 첫 로딩에 유리.
6. **sitemap 미등록 공개 페이지**: `en/index.html`, `en/book1.html`, `en/agent-bible.html`, `en/claude-code-bible.html`, `en/media-kit.html`, `ja/index.html`, `parenting/index.html`, `checkout.html` — 검색 노출을 원하는 페이지만 추가.

## 5. 실습 압축 검증 실패 원인

`scripts/verify_exercise_archives.py`가 `volume2-starter.zip` 안의 `ontology_lab.py`·`sample_data.json`·`test_ontology_lab.py`와 `examples/agent-ontology/` 원본을 바이트 단위로 비교하다 실패한다. 압축 안 파일은 CRLF(Windows 줄바꿈), 원본은 LF이며, **줄바꿈을 무시하면 내용은 완전히 같다**. 이번 수정과는 무관한 기존 상태다. 압축을 LF로 다시 만들거나, 검사에서 줄바꿈을 정규화하면 해결된다.
