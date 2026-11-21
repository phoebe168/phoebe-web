"""phoebe 官網產生器

用法：python build.py
讀取 src/layout.html 與 src/pages/*.html，產生 docs/*.html（GitHub Pages 從 docs/ 發布）。
共用的頁首、頁尾只改 src/layout.html 一處即可。
"""
import hashlib
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"

LINE_URL = "https://line.me/R/ti/p/@phoebecare"
FB_URL = "https://www.facebook.com/profile.php?id=100086501402852"

# slug, 選單名稱, 頁面標題, 頁面描述（搜尋結果顯示用）
PAGES = [
    ("index", None, "非比營養諮詢中心 - 新竹營養師團隊",
     "非比營養諮詢中心是新竹的營養師團隊，提供長照營養、全齡營養諮詢、營養講座與健康管理。"),
    ("about", "關於非比", "關於非比 - 非比營養諮詢中心",
     "非比營養諮詢中心的工作原則與服務區域。"),
    ("team", "營養師團隊", "營養師團隊 - 非比營養諮詢中心",
     "認識非比的營養師、物理治療師與職能治療師。"),
    ("services", "服務內容", "服務內容 - 非比營養諮詢中心",
     "全齡營養、營養講座與合作、長照營養、健康管理。"),
    ("process", "服務流程", "服務流程 - 非比營養諮詢中心",
     "從加 LINE 到追蹤調整，個人諮詢與講座合作的進行方式。"),
    ("cases", "實績案例", "實績案例 - 非比營養諮詢中心",
     "非比在政府、社區、學校與照護機構的合作紀錄。"),
    ("contact", "立即預約", "立即預約 - 非比營養諮詢中心",
     "加入 LINE 好友預約營養諮詢，或來電洽詢講座合作。"),
]

# 首頁餐盤：四大服務
PLATE = [
    ("全齡營養", "services.html#all-ages", "#01513c"),
    ("講座與合作", "services.html#talks", "#2f6e58"),
    ("長照營養", "services.html#ltc", "#723e27"),
    ("健康管理", "services.html#health", "#4f8670"),
]


def plate_svg():
    """首頁餐盤：四個扇形拼成完整圓盤，中間放完整 Logo"""
    cx = cy = 200
    r_out, r_in = 172, 86
    parts = []
    for i, (label, href, color) in enumerate(PLATE):
        a0 = math.radians(-90 + i * 90)
        a1 = math.radians(-90 + (i + 1) * 90)

        def pt(r, a):
            return f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}"

        d = (f"M{pt(r_out, a0)} A{r_out},{r_out} 0 0 1 {pt(r_out, a1)} "
             f"L{pt(r_in, a1)} A{r_in},{r_in} 0 0 0 {pt(r_in, a0)} Z")
        am = (a0 + a1) / 2
        tx, ty = cx + 129 * math.cos(am), cy + 129 * math.sin(am)
        parts.append(
            f'<a href="{href}" class="plate-part">'
            f'<path d="{d}" fill="{color}"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" dominant-baseline="middle">{label}</text>'
            f"</a>"
        )
    # 白色等寬分隔線，讓四格間距一致、外形仍是完整圓形
    seps = ('<g stroke="#fff" stroke-width="7">'
            f'<line x1="{cx}" y1="{cy - r_out - 2}" x2="{cx}" y2="{cy + r_out + 2}"/>'
            f'<line x1="{cx - r_out - 2}" y1="{cy}" x2="{cx + r_out + 2}" y2="{cy}"/></g>')
    # Logo 原圖 560x464，完整放在中央白色圓內
    lw, lh = 120, 120 * 464 / 560
    logo = (f'<circle cx="{cx}" cy="{cy}" r="{r_in}" fill="#fff"/>'
            f'<image href="assets/logo.png" x="{cx - lw / 2:.1f}" y="{cy - lh / 2:.1f}" '
            f'width="{lw}" height="{lh:.1f}"/>')
    return (
        '<svg class="plate" viewBox="0 0 400 400" role="img" aria-labelledby="plate-t">'
        '<title id="plate-t">非比的四項服務：全齡營養、講座與合作、長照營養、健康管理</title>'
        '<circle cx="200" cy="200" r="190" fill="none" stroke="#723e27" stroke-width="4"/>'
        + "".join(parts) + seps + logo + "</svg>"
    )


def nav_html(current):
    items = []
    for slug, name, *_ in PAGES:
        if not name:
            continue
        cls = ' class="cta"' if slug == "contact" else ""
        cur = ' aria-current="page"' if slug == current else ""
        items.append(f'<a href="{slug}.html"{cls}{cur}>{name}</a>')
    items.insert(-1, f'<a href="{FB_URL}" class="fb">臉書</a>')
    return "\n      ".join(items)


def main():
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    # 樣式檔加版本號：style.css 內容一改，網址就變，手機不會再用舊的快取
    css_ver = hashlib.md5((OUT / "assets" / "style.css").read_bytes()).hexdigest()[:8]
    layout = layout.replace('href="assets/style.css"', f'href="assets/style.css?v={css_ver}"')
    for slug, _, title, desc in PAGES:
        body = (SRC / "pages" / f"{slug}.html").read_text(encoding="utf-8")
        body = (body.replace("{{plate}}", plate_svg())
                    .replace("{{line_url}}", LINE_URL)
                    .replace("{{fb_url}}", FB_URL))
        html = (layout.replace("{{title}}", title)
                      .replace("{{description}}", desc)
                      .replace("{{slug}}", slug)
                      .replace("{{nav}}", nav_html(slug))
                      .replace("{{body}}", body)
                      .replace("{{line_url}}", LINE_URL)
                      .replace("{{fb_url}}", FB_URL)
                      .replace("{{year}}", str(date.today().year)))
        (OUT / f"{slug}.html").write_text(html, encoding="utf-8")
        print("built", slug)


if __name__ == "__main__":
    main()
