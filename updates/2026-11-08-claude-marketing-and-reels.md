# 마케팅 기록 — Claude 활용 콘텐츠 & AI사냥꾼 릴스 제작

- 기록일: 2026년 11월 8일
- 목적: 인스타그램에서 반응 좋은 Claude 활용 콘텐츠를 정리하고, AI사냥꾼 채널용 릴스 소재로 쓴다.
- 원칙: 남의 릴스 화면·음원은 쓰지 않는다. 형식만 참고하고 화면과 음악은 직접 만든다. 도구 정보는 공식 저장소에서 확인한 내용만 쓴다.

## 1. Claude 마케팅 커넥터 5개

참고: oaiwan.kr 릴스 "Claude로 마케팅한다면 이 5개는 무조건 연결하세요" (좋아요 655 · 댓글 2,660 · 저장 3,708, 확인 시점 기준)

| 단계 | 커넥터 | 하는 일 | Claude에게 시키는 예시 |
|---|---|---|---|
| 조사 | Bright Data | 릴스·트렌드 조사 | "요즘 뜨는 AI 릴스 50개 조회수·댓글 패턴 정리해줘" |
| 실행 | Meta Ads | 광고 성과 관리 | "지난주 광고 중 클릭당 비용 제일 비싼 3개 끄자고 제안해줘" |
| 조사 | Firecrawl | 경쟁사 사이트 수집 | "경쟁사 3곳 가격표·문구 한 표로 비교해줘" |
| 분석 | PostHog | 이탈 지점 분석 | "결제 페이지에서 어디서 제일 많이 나가는지 알려줘" |
| 실행 | Upload-Post | SNS 자동 업로드 | "이 릴스 인스타·틱톡·유튜브에 내일 아침 9시 예약해줘" |

- 흐름: 조사 → 실행 → 분석을 Claude 하나로 한 바퀴 돌린다.
- 연결 전에 확인할 것: 각 서비스의 공식 MCP·커넥터 여부, 요금, 광고 계정 권한 범위. 광고 끄기·게시 같은 실행은 처음엔 "제안만" 받고 사람이 승인한다.

## 2. 전문가 느낌 웹사이트 세트 (스킬 3 + MCP 2)

참고: lazy_owen 릴스 "진짜 전문가가 만든 것 같은 웹사이트를 클로드로 만드는 방법" (좋아요 3,544 · 댓글 1.7만 · 저장 1.4만)

| 종류 | 이름 | 하는 일 | 설치 (공식 README 기준) |
|---|---|---|---|
| 스킬 | Emil Kowalski (emilkowalski/skills) | 버튼·화면 전환 등 움직임 디테일 | `npx skills@latest add emilkowalski/skills` |
| 스킬 | Impeccable (pbakaus/impeccable) | 'AI 티' 나는 디자인 점검·다듬기 | `npx impeccable install` |
| 스킬 | Taste (Leonxlnx/taste-skill) | 레퍼런스 기반 아트 디렉션 | `npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"` |
| MCP | Figma | 피그마 디자인을 코드로 | Figma 앱 Dev Mode에서 MCP 서버 켜고 Claude에 연결 |
| MCP | Playwright (microsoft/playwright-mcp) | 브라우저로 직접 보고 고치기 | `claude mcp add playwright npx @playwright/mcp@latest` |

## 3. MotionSites 무료 스킬 (영화 같은 랜딩페이지)

참고: Taher Shabaan 릴스 "Comment 'Cinematic' to get the skill" (좋아요 1,132 · 저장 3,718)

- 저장소: github.com/Motionsites-AI/claude-skill (MIT, 별 약 1,800개 — 2026-11-08 확인)
- 내용: 예시 프롬프트 40개, 시네마틱 영상 50개+, 효과 레시피 55개+, 스크린샷 보고 스스로 고치는 점검 루프
- 설치: Claude 앱은 릴리스의 `motionsites-web-builder.zip`을 Customize → Skills → Upload a skill로 올리고 켠다(코드 실행 기능 필요). Claude Code는 `/plugin marketplace add Motionsites-AI/claude-skill` → `/plugin install motionsites-web-builder@motionsites`

## 4. 생활 속 AI — 챗GPT 알람(예약 작업)

- 원본: AI사냥꾼 영상 "생활 속에서 AI를 가장 잘 쓰는 방법" (2026-06-04 촬영, 30초)
- 핵심: 알람을 설정해 두면 받고 싶은 정보·공부할 내용을 AI가 찾아서 정해진 시간에 보내준다.
- 예시 프롬프트: "매일 아침 7시에 오늘의 AI 뉴스 3줄로 요약해서 알려줘"

## 5. 오늘 만든 릴스 (모두 9:16, 1080×1920)

| # | 제목 | 길이 | 사용 소재 | 댓글 키워드(CTA) |
|---|---|---|---|---|
| 1 | 클로드 영상 편집 7단계 | 14초 | 모션그래픽만 | 편집 |
| 2 | AI로 만들고, 사람에게 가르칩니다 (스토리형) | 38초 | AI 홍보영상 + 유리칠판 강의 영상 + 강의실 사진 | 영상 |
| 3 | 오늘 한 줄부터 | 37초 | 무대 강연·기업 강의·실습·노트북 사진 | 한 줄 |
| 4 | 챗GPT 알람 기능 (+보너스 MotionSites) | 45초 | 생활 속 AI 영상 + 강연 사진 | 알람 |
| 5 | 클로드 무료 스킬로 영화 같은 홈페이지 | 30초 | 모션그래픽만 | 시네마틱 |
| 6 | Claude 마케팅 커넥터 5개 | 33초 | 강의 사진 6장 | 마케팅 |
| 7 | 전문가 느낌 웹사이트 만드는 법 | 35초 | 강의 사진 6장 | 웹사이트 |

- 음악·효과음은 모두 직접 생성해 저작권 문제가 없다.
- 영상 파일은 작업 환경 임시 폴더에 있어 따로 내려받아 보관해야 한다.

## 게시 전 체크리스트

- [ ] 강의 사진·영상 속 참석자 얼굴 게시 동의
- [ ] 댓글 키워드별 자동응답(DM)과 보낼 자료(PDF·프롬프트·설치법) 준비
- [ ] 영상 속 예시 화면(랜딩페이지·알림 문구 등)은 설명용 그림임을 캡션에 명시할지 결정
- [ ] 커넥터·스킬 설치 명령어를 게시 직전 한 번 더 공식 저장소에서 확인
