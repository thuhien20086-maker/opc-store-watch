#!/usr/bin/env python3
"""OPC Store 每日快照 + 静态看板生成（GitHub Actions 版）。
抓 ai6666.com/store 全量 → 对比上次 → 生成 index.html + data/*.json
"""
import json, urllib.request, pathlib, datetime, html

BASE = "https://ai6666.com/opcpay/api/v1/opc/products?q=&sort=joined&page="
ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"


def fetch_all():
    out, page = [], 1
    while page <= 40:
        req = urllib.request.Request(BASE + str(page), headers={"User-Agent": "Mozilla/5.0"})
        d = json.load(urllib.request.urlopen(req, timeout=30))
        items = d.get("items") or []
        if not items:
            break
        out += items
        if not d.get("has_more"):
            break
        page += 1
    seen, uniq = set(), []
    for p in out:
        if p["id"] not in seen:
            seen.add(p["id"])
            uniq.append(p)
    return uniq


def esc(x):
    return html.escape(str(x or ""))


def render(cur, prev, today):
    prev_map = {p["id"]: p for p in prev}
    new = [p for p in cur if p["id"] not in prev_map]
    top = sorted(cur, key=lambda p: -(p.get("view_count") or 0))[:20]
    total_views = sum(p.get("view_count") or 0 for p in cur)

    # 历史
    hist = []
    for f in sorted(DATA.glob("snapshot-*.json"))[-14:]:
        try:
            snap = json.loads(f.read_text(encoding="utf-8"))
            hist.append((f.stem.replace("snapshot-", ""), len(snap)))
        except Exception:
            pass

    def row(p):
        name = esc(p.get("name"))
        url = p.get("website_url") or p.get("web_url") or ""
        link = f'<a href="{esc(url)}" target="_blank" rel="noopener">{name}</a>' if url else name
        return (f"<tr><td>{link}</td><td class=n>{(p.get('view_count') or 0)}</td>"
                f"<td class=n>{esc(p.get('rating') or '-')}</td>"
                f"<td class=n>{(p.get('review_count') or 0)}</td>"
                f"<td class=n>{esc(str(p.get('created_at'))[:10])}</td></tr>")

    new_cards = ""
    for p in new:
        url = p.get("website_url") or p.get("web_url") or ""
        new_cards += f"""<div class=card><div class=ct>{esc(p.get('name'))}</div>
<div class=cd>{esc((p.get('description') or '')[:180])}</div>
<div class=cm>{esc(str(p.get('created_at'))[:10])}{' · <a href="'+esc(url)+'" target=_blank>打开</a>' if url else ''}</div></div>"""

    hist_rows = "".join(f"<tr><td>{d}</td><td class=n>{n}</td></tr>" for d, n in hist)

    return f"""<!doctype html><html lang=zh-CN><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>OPC Store 监控 · {today}</title>
<style>
:root{{--bg:#0d1117;--fg:#e6edf3;--mut:#8b949e;--line:#21262d;--acc:#58a6ff}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,"PingFang SC",sans-serif;padding:40px 20px}}
.wrap{{max-width:960px;margin:0 auto}}
h1{{font-size:26px;margin:0 0 6px}}
.sub{{color:var(--mut);font-size:13px;margin-bottom:26px}}
.kpis{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:28px}}
.kpi{{border:1px solid var(--line);border-radius:10px;padding:12px 18px;min-width:120px}}
.kpi b{{display:block;font-size:24px;color:var(--acc)}}
.kpi span{{color:var(--mut);font-size:12px}}
h2{{font-size:17px;margin:32px 0 12px;border-left:3px solid var(--acc);padding-left:10px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left}}
th{{color:var(--mut);font-weight:500;font-size:12px}}
td.n{{text-align:right;font-variant-numeric:tabular-nums}}
a{{color:var(--acc);text-decoration:none}}a:hover{{text-decoration:underline}}
.card{{border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:10px}}
.ct{{font-weight:600;margin-bottom:4px}}
.cd{{color:var(--mut);font-size:13px}}
.cm{{color:#6e7681;font-size:12px;margin-top:6px}}
.empty{{color:var(--mut);padding:14px;border:1px dashed var(--line);border-radius:10px}}
footer{{color:var(--mut);font-size:12px;margin-top:40px;border-top:1px solid var(--line);padding-top:14px}}
</style></head><body><div class=wrap>
<h1>OPC Store 监控</h1>
<div class=sub>ai6666.com/store · 每日自动快照 · 更新于 {today}（北京时间 21:10 由 GitHub Actions 生成）</div>
<div class=kpis>
<div class=kpi><b>{len(cur)}</b><span>产品总数</span></div>
<div class=kpi><b>{len(new)}</b><span>今日新增</span></div>
<div class=kpi><b>{total_views:,}</b><span>累计浏览</span></div>
<div class=kpi><b>{sum(1 for p in cur if (p.get('review_count') or 0)>0)}</b><span>有评论的产品</span></div>
</div>
<h2>今日新增</h2>
{new_cards or '<div class=empty>今日无新增</div>'}
<h2>浏览 Top 20</h2>
<table><thead><tr><th>产品</th><th class=n>浏览</th><th class=n>评分</th><th class=n>评论</th><th class=n>入驻</th></tr></thead>
<tbody>{''.join(row(p) for p in top)}</tbody></table>
<h2>历史（产品总数）</h2>
<table><thead><tr><th>日期</th><th class=n>总数</th></tr></thead><tbody>{hist_rows}</tbody></table>
<footer>数据来源：ai6666.com 公开 API。本页由 GitHub Actions 每日生成，仅做公开信息聚合。原始数据见 <a href="data/latest.json">data/latest.json</a></footer>
</div></body></html>"""


def main():
    DATA.mkdir(exist_ok=True)
    prev_file = DATA / "latest.json"
    prev = json.loads(prev_file.read_text(encoding="utf-8")) if prev_file.exists() else []
    cur = fetch_all()
    today = datetime.datetime.utcnow().astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d")
    (DATA / f"snapshot-{today}.json").write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
    prev_file.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "index.html").write_text(render(cur, prev, today), encoding="utf-8")
    new = len(cur) - len(prev) if prev else len(cur)
    print(f"[{today}] total={len(cur)} prev={len(prev)} new={new}")


if __name__ == "__main__":
    main()
