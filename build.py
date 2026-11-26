"""phoebe 官網產生器

用法：python build.py
讀取 src/layout.html 與 src/pages/*.html，產生 docs/*.html（GitHub Pages 從 docs/ 發布）。
共用的頁首、頁尾只改 src/layout.html 一處即可。
營養師、特約團隊、合作夥伴的資料在 src/team.json，營養師個人頁（team-xxx.html）也由它產生。
"""
import hashlib
import html as htmlmod
import json
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
     "認識非比的營養師，以及特約的物理、職能、語言治療師與護理師。"),
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
    ("全齡營養", "services.html#all-ages", "#33665f"),
    ("講座與合作", "services.html#talks", "#4f7f77"),
    ("長照營養", "services.html#ltc", "#7f6c5e"),
    ("健康管理", "services.html#health", "#5f8f86"),
]


def plate_svg():
    """首頁餐盤：四個扇形拼成完整圓盤，中間放完整 Logo"""
    cx = cy = 200
    r_out, r_in = 172, 98
    parts = []
    for i, (label, href, color) in enumerate(PLATE):
        a0 = math.radians(-90 + i * 90)
        a1 = math.radians(-90 + (i + 1) * 90)

        def pt(r, a):
            return f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}"

        d = (f"M{pt(r_out, a0)} A{r_out},{r_out} 0 0 1 {pt(r_out, a1)} "
             f"L{pt(r_in, a1)} A{r_in},{r_in} 0 0 0 {pt(r_in, a0)} Z")
        am = (a0 + a1) / 2
        tx, ty = cx + 133 * math.cos(am), cy + 133 * math.sin(am)
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
    # 橫式 Logo 原圖 1754x623，完整放在中央白色圓內
    lw, lh = 180, 180 * 391 / 1200
    logo = (f'<circle cx="{cx}" cy="{cy}" r="{r_in}" fill="#fff"/>'
            f'<image href="assets/logo-h.png" x="{cx - lw / 2:.1f}" y="{cy - lh / 2:.1f}" '
            f'width="{lw}" height="{lh:.1f}"/>')
    return (
        '<svg class="plate" viewBox="0 0 400 400" role="img" aria-labelledby="plate-t">'
        '<title id="plate-t">非比的四項服務：全齡營養、講座與合作、長照營養、健康管理</title>'
        '<circle cx="200" cy="200" r="190" fill="none" stroke="#7f6c5e" stroke-width="4"/>'
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


E = htmlmod.escape


def load_team():
    return json.loads((SRC / "team.json").read_text(encoding="utf-8"))


def dietitian_cards(team):
    out = []
    for d in team["dietitians"]:
        tags = "".join(f"<span>{E(t)}</span>" for t in d["tags"])
        title = E(d["title"])
        out.append(f"""      <li>
        <a class="d-card" href="team-{d['slug']}.html">
          <img src="assets/photos/team/{d['slug']}.jpg" alt="{E(d['name'])} {E(d['role'])}" width="400" height="400" loading="lazy">
          <span class="d-body">
            <strong>{E(d['name'])}</strong>
            <span class="d-title">{title}</span>
            <span class="d-lead">{E(d['lead'])}</span>
            <span class="tags">{tags}</span>
            <span class="d-more">看完整介紹</span>
          </span>
        </a>
      </li>""")
    return "\n".join(out)


def specialists_html(team):
    out = []
    for r in team["specialists"]:
        items = "".join(f"<li>{E(x)}</li>" for x in r["can"])
        out.append(f"""      <article class="role">
        <h3>{E(r['role'])}</h3>
        <p class="when">{E(r['when'])}</p>
        <ul>{items}</ul>
      </article>""")
    return "\n".join(out)


def partners_html(team):
    return "\n".join(f"      <li>{E(p)}</li>" for p in team["partners"])


def profile_body(d):
    secs = "".join(
        f'<section class="p-sec"><h2>{E(h)}</h2><ul>{"".join(f"<li>{E(x)}</li>" for x in items)}</ul></section>'
        for h, items in d["sections"])
    award = f'<p class="p-award">{E(d["award"])}</p>' if d.get("award") else ""
    title = E(d["title"]) if d["title"] == d["role"] else f'{E(d["role"])}・{E(d["title"])}'
    return f"""<section class="band profile">
  <div class="wrap">
    <p class="crumb"><a href="team.html">營養師團隊</a> ／ {E(d['name'])}</p>
    <div class="p-grid">
      <aside class="p-side">
        <img src="assets/photos/team/{d['slug']}-full.jpg" alt="{E(d['name'])} {E(d['role'])}" loading="lazy">
      </aside>
      <div class="p-main">
        <h1>{E(d['name'])}</h1>
        <p class="p-title">{title}</p>
        <p class="p-intro">{E(d['intro'])}</p>
        {award}
        <div class="p-secs">{secs}</div>
        <p class="p-cta"><a class="btn btn-line" href="{{{{line_url}}}}">加 LINE 預約諮詢</a> <a class="btn btn-ghost" href="team.html">回團隊列表</a></p>
      </div>
    </div>
  </div>
</section>
"""


def render(layout, slug, nav_slug, title, desc, body):
    body = (body.replace("{{plate}}", plate_svg())
                .replace("{{line_url}}", LINE_URL)
                .replace("{{fb_url}}", FB_URL))
    html = (layout.replace("{{title}}", title)
                  .replace("{{description}}", desc)
                  .replace("{{slug}}", slug)
                  .replace("{{nav}}", nav_html(nav_slug))
                  .replace("{{body}}", body)
                  .replace("{{line_url}}", LINE_URL)
                  .replace("{{fb_url}}", FB_URL)
                  .replace("{{year}}", str(date.today().year)))
    (OUT / f"{slug}.html").write_text(html, encoding="utf-8")
    print("built", slug)


def main():
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    # 樣式檔加版本號：style.css 內容一改，網址就變，手機不會再用舊的快取
    css_ver = hashlib.md5((OUT / "assets" / "style.css").read_bytes()).hexdigest()[:8]
    layout = layout.replace('href="assets/style.css"', f'href="assets/style.css?v={css_ver}"')
    team = load_team()
    for slug, _, title, desc in PAGES:
        body = (SRC / "pages" / f"{slug}.html").read_text(encoding="utf-8")
        body = (body.replace("{{dietitian_cards}}", dietitian_cards(team))
                    .replace("{{specialists}}", specialists_html(team))
                    .replace("{{partners}}", partners_html(team)))
        render(layout, slug, slug, title, desc, body)
    for d in team["dietitians"]:
        render(layout, f"team-{d['slug']}", "team",
               f"{d['name']} {d['role']} - 非比營養諮詢中心", d["lead"], profile_body(d))


if __name__ == "__main__":
    main()
