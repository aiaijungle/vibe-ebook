# 로맨스AI스튜디오 (MVP)

로맨스판타지/BL 니치 AI 캐릭터챗 서비스. [Agnaistic(agnai)](https://github.com/agnaistic/agnai)를 포크한 코드베이스에
브랜딩 최소 변경 + 시드 캐릭터카드 3종을 추가한 상태입니다.

전체 사업 기획은 `/obsidian/제타스타일-AI캐릭터챗-기획안.md` 참고.

## ⚠️ 반드시 먼저 읽을 것 — 라이선스(AGPL-3.0)

원본 Agnaistic은 **AGPL-3.0** 라이선스입니다. 이건 상업 서비스 계획에 직접 영향을 줍니다:

- AGPL은 "네트워크로 서비스만 제공해도(배포하지 않아도) 소스 공개 의무가 발생"하는 카피레프트 라이선스입니다.
- 즉 이 코드를 기반으로 서비스를 운영하면, **이용자에게 수정된 전체 소스코드를 공개해야 할 의무**가 생깁니다.
- 기획안의 **트랙 A(B2B 화이트라벨 SaaS)와 충돌 가능성이 큽니다.** 파트너사에 비공개 화이트라벨로 재판매하려면:
  1. 이 저장소는 프로토타입/검증용으로만 쓰고, 상용 코드는 자체 구현으로 교체하거나
  2. Agnaistic 측에 상용 라이선스를 별도 문의하거나
  3. MIT/Apache 라이선스의 대안(예: SillyTavern 확장, 자체 스크래치 빌드)으로 전환
- **트랙 B(니치 B2C)는 AGPL이 실질적으로 덜 문제됨** — 소스 공개 자체가 오히려 오픈소스 커뮤니티 신뢰로 활용 가능. 이 트랙부터 검증하는 걸 권장.

이 판단은 법률 자문이 필요한 사안이라 여기서는 리스크만 표시합니다. 상용화 전 반드시 확인하세요.

**결정 (2026-07-20):** 지금 단계에서는 Agnaistic 코드를 그대로 유지하고 **트랙 B(니치 B2C)부터 PMF 검증**한다. 트랙 A(B2B 화이트라벨, 비공개 재판매)를 실제로 추진할 시점이 오면 그때 코드 교체/상용 라이선스 문의를 재검토한다.

## 현재 포함된 것
- Agnaistic 원본 코드베이스 (`srv`: Node/Express 백엔드, `web`: SolidJS 프론트엔드, `common`: 공유 타입)
- `web/index.html` 타이틀/OG 태그 한국어 브랜딩으로 교체
- `package.json` 이름/설명 변경
- `seed-characters/` — chara_card_v2 규격 캐릭터카드 3종
  - `01-이시헐-회귀공작.json` (로맨스판타지, 회귀·집착남주)
  - `02-라스코-계약연애.json` (BL, 계약연애·후회공)
  - `03-황태자엔카를로-빙의악녀.json` (로맨스판타지, 빙의·악녀)

## 검증 완료 (2026-07-20)
- [x] `pnpm install` — 정상 (node_modules 1.1G)
- [x] 빌드 — 백엔드(`tsc -p srv.tsconfig.json`), 프론트엔드(`parcel build`) 둘 다 에러 없음
- [x] 서버 기동 — `JSON_STORAGE=1`(MongoDB 없이 파일 저장소)로 `http://127.0.0.1:3001` 정상 응답(200). 외부 LLM 프로바이더 모델 목록 조회 일부만 네트워크 정책으로 실패(치명적 아님, 무시하고 부팅됨)

## 아직 안 된 것 (다음 단계)
- [ ] LLM 백엔드 연결 — API 키 필요 (OpenAI/Claude/OpenRouter 등. `.env.template` 참고)
- [ ] 시드 캐릭터카드를 앱에 실제로 import해서 동작 확인 (`web/pages/Character/ImportCharacter.tsx` 사용)
- [ ] 결제 연동 (토스페이먼츠/아임포트 등)
- [ ] 연령확인 — 기획안 5장 리스크 참고, MVP 필수 항목
- [ ] 배포 인프라 결정 (Docker 이미지는 기본 제공됨, `self-host.docker-compose.yml`)

## 로컬 실행 (검증됨)
```bash
npx pnpm@10 install --lockfile   # 의존성 설치
npm run build:server              # 백엔드 빌드 (tsc)
npx parcel build web/index.html --no-optimize --detailed-report   # 프론트엔드 빌드
cp .env.template .env             # JSON_STORAGE=1 포함, MongoDB 없이 실행 가능
JSON_STORAGE=1 node srv/start.js  # http://127.0.0.1:3001
```
Docker로 MongoDB 포함 실행:
```bash
docker compose -p romance-ai-studio -f self-host.docker-compose.yml up -d
```
LLM은 `.env.template`을 참고해 API 키를 설정해야 실제 대화가 동작합니다 (현재 미설정 — 다음 단계).

## 원본 라이선스/저작권
원본 코드 저작권은 Agnaistic 프로젝트에 있습니다. `LICENSE.md` 원문 유지.
