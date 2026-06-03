"""agent-bible.html -> 인쇄용 HTML 생성 후 Playwright PDF 변환"""
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

SRC  = Path(__file__).parent / "agent-bible.html"
TMP  = Path(__file__).parent / "_print_agent_bible.html"
PDF  = Path(__file__).parent / "AI_Agent_Bible_AITF2026.pdf"

PRINT_STYLE = """
<style>
* { box-sizing: border-box; }
body {
  font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
  background: #fff; color: #111;
  margin: 0; padding: 0; font-size: 14px; line-height: 1.7;
}
.chapter { page-break-before: always; padding: 32px 40px; max-width: 860px; margin: 0 auto; }
.chapter:first-of-type { page-break-before: avoid; }
.ch-header { background: #f4f4f8; border-left: 6px solid #7c3aed; padding: 24px 28px; margin-bottom: 28px; border-radius: 0 8px 8px 0; }
.ch-num   { font-size: 11px; font-weight: 700; color: #7c3aed; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 6px; }
.ch-title { font-size: 22px; font-weight: 900; color: #111; margin-bottom: 8px; }
.ch-desc  { font-size: 13px; color: #444; }
.ch-body  { padding: 0 4px; }
.ch-badges { margin-top: 10px; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; margin-right: 5px; background: #e9e3ff; color: #5b21b6; }
h2,h3 { color: #111; }
p { margin: 10px 0; }
pre, code { background: #f3f4f6; border: 1px solid #d1d5db; border-radius: 6px; padding: 2px 6px; font-size: 12px; white-space: pre-wrap; word-break: break-all; font-family: 'Consolas','D2Coding',monospace; }
pre { padding: 14px 18px; display: block; overflow: visible; }
.tip-box, .warn-box, .code-block {
  background: #f9fafb; border: 1px solid #d1d5db; border-radius: 8px;
  padding: 14px 18px; margin: 14px 0; font-size: 13px;
}
.tip-box  { border-left: 4px solid #7c3aed; }
.warn-box { border-left: 4px solid #f59e0b; }
a { color: #4338ca; text-decoration: underline; }
table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13px; }
th, td { border: 1px solid #d1d5db; padding: 8px 12px; text-align: left; }
th { background: #f4f4f8; font-weight: 700; }
.yt-cta { background: #fff7ed; border: 1px solid #fed7aa; border-radius: 10px; padding: 14px 18px; margin: 14px 0; font-size: 13px; }
.yt-cta-icon { display: none; }
.yt-cta-actions { display: none; }
img { max-width: 100%; height: auto; }
/* 철학 섹션 인라인 다크박스 → 라이트 */
div[style*="0f0520"], div[style*="0a0010"], div[style*="12001e"] {
  background: #f0edff !important; color: #111 !important;
  border-left: 4px solid #7c3aed !important;
}
/* 카운트다운, 배너 숨김 */
#may-countdown, #series-intro-banner, #top-progress { display: none !important; }
.harness-grid { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0; }
.harness-item { background: #f4f4f8; border: 1px solid #d1d5db; border-radius: 6px; padding: 6px 14px; font-size: 12px; font-weight: 600; }
@page { size: A4; margin: 18mm 15mm; }
</style>
"""

COVER_HTML = """
<div style="page-break-after:always;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;text-align:center;padding:60px 40px;">
  <div style="font-size:12px;font-weight:700;letter-spacing:.15em;color:#7c3aed;text-transform:uppercase;margin-bottom:16px;">AITF 2026 · 실전 가이드</div>
  <h1 style="font-size:38px;font-weight:900;color:#111;line-height:1.3;margin-bottom:20px;">AI 에이전트 바이블</h1>
  <p style="font-size:16px;color:#444;margin-bottom:40px;">Claude 에이전트 · MCP · 멀티에이전트 · 프로덕션 배포</p>
  <div style="width:60px;height:4px;background:#7c3aed;border-radius:2px;margin-bottom:40px;"></div>
  <p style="font-size:13px;color:#666;">무료 공개 에디션 · aiaijungle.github.io/vibe-ebook</p>
  <p style="font-size:12px;color:#aaa;margin-top:8px;">6월 1일부터 각 권당 19,900원 판매 예정</p>
</div>
"""

def build_print_html():
    raw = SRC.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "lxml")

    # .chapter 섹션만 추출
    chapters = soup.select(".chapter")
    if not chapters:
        raise RuntimeError("No .chapter elements found")

    print(f"Found {len(chapters)} chapters")

    # 각 챕터에서 불필요한 요소 제거
    for ch in chapters:
        for sel in [".yt-cta-actions", ".yt-cta-badge", "#may-countdown",
                    "#series-intro-banner", ".mobile-topbar"]:
            for el in ch.select(sel):
                el.decompose()
        # inline style의 다크 배경 제거
        for el in ch.find_all(style=True):
            s = el.get("style", "")
            if "0f0520" in s or "0a0010" in s or "180010" in s or "12001e" in s:
                el["style"] = "background:#f0edff;color:#111;border-left:4px solid #7c3aed;padding:16px 20px;border-radius:0 10px 10px 0;margin:20px 0;"

    chapters_html = "\n".join(str(c) for c in chapters)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI 에이전트 바이블 - AITF 2026</title>
{PRINT_STYLE}
</head>
<body>
{COVER_HTML}
{chapters_html}
</body>
</html>"""

    TMP.write_text(html, encoding="utf-8")
    size_kb = TMP.stat().st_size / 1024
    print(f"Print HTML: {TMP.name} ({size_kb:.0f} KB)")
    return TMP


def generate_pdf(html_path: Path):
    url = html_path.as_uri()
    print(f"Generating PDF from {html_path.name}...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)
        h = page.evaluate("document.body.scrollHeight")
        print(f"Page height: {h}px")
        page.pdf(
            path=str(PDF),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()

    size_mb = PDF.stat().st_size / 1024 / 1024
    print(f"PDF: {PDF.name}  {size_mb:.1f} MB  ({PDF.stat().st_size:,} bytes)")
    return PDF


if __name__ == "__main__":
    html = build_print_html()
    generate_pdf(html)
