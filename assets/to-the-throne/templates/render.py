#!/usr/bin/env python3
"""Generate data-driven TTT *draft* HTML and optional PNG previews.

No live website writes. Does not recreate approved artwork exactly.
Requires Playwright + Chromium only for --png (HTML uses stdlib).
"""
import argparse
import html
import json
from pathlib import Path
from validate import issues

PALETTE = {
    "navy":"#13233F", "deep":"#101A2E", "paper":"#FFF8EA",
    "bronze":"#B87930", "gold":"#D7A84F", "ink":"#24334B",
    "burgundy":"#7E303A", "amber":"#A76B2D"
}
def esc(value):
    return html.escape(str(value), quote=True)

def paragraph(value):
    return esc(value).replace("\n", "<br>")

def matter_html(m, number):
    focus = "".join("<li>" + esc(x) + "</li>" for x in m["prayer_focus"])
    scripture = m["scripture"]
    map_image = str(m.get("map_image", "")).strip()
    # The optional map must be an already approved or separately verified image.
    # Never generate misleading geography from a location string.
    if map_image:
        if map_image.startswith(("https://", "http://", "data:")):
            map_html = '<img src="' + esc(map_image) + '" alt="Verified map of ' + esc(m["location"]) + '">'
        else:
            map_html = '<div class="map-placeholder">MAP FILE: ' + esc(map_image) + '</div>'
    else:
        map_html = '<div class="map-placeholder">APPROVED MAP REQUIRED<br>' + esc(m["location"]) + '</div>'
    return ( '<section class="matter"><div class="num">' + ("%02d" % number) +
        '</div><div class="map">' + map_html + '</div><div class="facts"><div class="location">' +
        esc(m["location"]) + '</div><h2 class="matter-heading">' + esc(m["heading"]) +
        '</h2><p>' + paragraph(m["summary"]) + '</p></div><div class="prayer"><h3>TAKE IT BEFORE THE THRONE</h3><ul>' +
        focus + '</ul><p class="verse"><strong>' + esc(scripture["reference"]) + '</strong> — ' +
        paragraph(scripture["text"]) + '</p><div class="status">' + esc(m["status"]) +
        ' · INTERCESSION</div></div></section>' )

def make_html(d):
    kind = d["kind"]
    body = "\n".join(matter_html(m, i) for i,m in enumerate(d["matters"], 1))
    sources = " · ".join(esc(s) for s in d["sources"])
    # Printed sources must stay readable above the signature and mountain footer.
    css = """
    :root{--navy:#13233F;--deep:#101A2E;--paper:#FFF8EA;--bronze:#B87930;--gold:#D7A84F;--ink:#24334B;--burgundy:#7E303A}
    *{box-sizing:border-box}body{margin:0;background:#dedbd4;color:var(--ink);font-family:Georgia,'Times New Roman',serif}
    .sheet{width:1122px;min-height:1402px;margin:20px auto;padding:45px 47px 0;background:linear-gradient(180deg,#fffaf0,#f7efdf 88%,#d9c9ae);border:2px solid #bba77c;box-shadow:0 15px 30px #0002;position:relative}
    .draft{font:700 12px Arial;letter-spacing:2px;color:#8e302e;text-align:center;padding:7px;border:1px dashed #8e302e;margin-bottom:13px}
    .masthead{display:flex;align-items:center;justify-content:space-between;gap:24px;border-bottom:3px solid var(--gold);padding-bottom:16px;margin-bottom:18px}
    .wordmark{font-weight:800;font-size:47px;color:var(--navy);letter-spacing:2px}.mission{font:700 11px Arial;color:#845b2a;letter-spacing:1.2px}
    .meta{text-align:right;color:var(--navy);font:700 14px Arial;line-height:1.6}.intro h1{font-size:35px;color:var(--navy);margin:8px 0}
    .intro p{font-size:15px;line-height:1.46;margin:8px 0 18px}
    .matter{display:grid;grid-template-columns:43px 195px 1fr 1fr;gap:12px;align-items:stretch;border-top:1px solid #cbb790;padding:13px 0;break-inside:avoid}
    .num{font-size:28px;font-weight:800;color:#93672c}.map{min-height:134px;background:#d8d0be;border:1px solid #aa9c83}
    .map img{display:block;width:100%;height:100%;object-fit:cover}.map-placeholder{font:700 12px Arial;text-align:center;color:#586170;padding:38px 6px;line-height:1.5}
    .facts,.prayer{font-size:13px;line-height:1.32}.location{font:800 14px Arial;color:var(--navy);margin-bottom:6px}
    .matter-heading{font:800 15px Arial;line-height:1.25;color:var(--bronze);margin:4px 0 7px;text-transform:uppercase}
    .facts p,.prayer p{margin:4px 0}.prayer h3{font:800 12px Arial;color:var(--navy);margin:1px 0 6px}.prayer ul{padding-left:17px;margin:0 0 5px}
    .prayer li{margin-bottom:3px}.verse{font-style:italic;color:#334b63}.status{background:var(--burgundy);color:white;font:800 9px Arial;letter-spacing:1px;display:inline-block;padding:5px 9px;margin-top:6px}
    .outro{border-top:1px solid #cbb790;font-size:14px;line-height:1.4;padding-top:13px}.sources{font:700 12px Arial;color:var(--navy);margin:12px 0 9px;line-height:1.5}
    .tagline{font-size:17px;font-weight:700;font-style:italic;color:#87413c;margin:9px 0}.signature{margin-top:13px;color:var(--navy)}
    .signature strong{display:block;font-style:italic;font-size:25px;margin:5px 0}.mountain{height:72px;margin:14px -47px 0;background:linear-gradient(165deg,#d7c1a1 0 45%,#a99a86 46% 60%,#6e7780 61% 76%,#343f4b 77%);opacity:.65}
    .motto{margin:0 -47px;background:var(--deep);color:#f1d48f;text-align:center;font:800 13px Arial;letter-spacing:1.1px;padding:13px}
    .social-share .sheet{width:1080px;min-height:1080px}.social-share .matter{grid-template-columns:36px 140px 1fr 1fr}.social-share .map{min-height:100px}
    @media print{body{background:white}.sheet{margin:0;box-shadow:none;break-inside:avoid}}
    """
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>' + esc(d["title"]) +
        ' | TTT DRAFT</title><style>' + css + '</style></head><body class="' + esc(kind) +
        '"><main class="sheet"><div class="draft">UNAPPROVED EDITABLE TEMPLATE PREVIEW — NOT FOR PUBLICATION</div>' +
        '<header class="masthead"><div><div class="wordmark">TO THE THRONE</div><div class="mission">STANDING IN THE GAP FOR THOSE IN NEED · TURNING AWARENESS INTO INTERCESSION</div></div>' +
        '<div class="meta">' + esc(d["title"]) + '<br>' + esc(d["report_id"]) + '<br>' + esc(d["date_label"]) +
        '</div></header><section class="intro"><h1>To the Body of Christ,</h1><p>' + paragraph(d["introduction"]) +
        '</p></section>' + body + '<section class="outro"><p>' + paragraph(d["closing"]) +
        '</p></section><div class="sources">SOURCES: ' + sources +
        ' | Full dated citations and verification: ' + esc(d["source_archive_url"]) +
        '</div><p class="tagline">' + esc(d["tagline"]) +
        '</p><div class="signature">In Christ,<strong>Brother Kris</strong><small>RESTORED DAILY MINISTRIES</small></div>' +
        '<div class="mountain" aria-hidden="true"></div><footer class="motto">TRUTH BEFORE NARRATIVE &nbsp; | &nbsp; PRAYER BEFORE REACTION &nbsp; | &nbsp; AS FAST AS TRUTH ALLOWS</footer>' +
        '</main></body></html>')

def main():
    p=argparse.ArgumentParser()
    p.add_argument("data")
    p.add_argument("--out",required=True)
    p.add_argument("--png")
    p.add_argument("--pdf")
    args=p.parse_args()
    d=json.loads(Path(args.data).read_text(encoding="utf-8"))
    errors=issues(d)
    if errors:
        raise SystemExit("\n".join("ERROR: "+x for x in errors))
    output=Path(args.out).resolve()
    # Never overwrite website source or existing graphic production archives.
    if "weekly-graphics" in output.parts or "weekly-documents" in output.parts:
        raise SystemExit("Refusing to write directly to published asset folders.")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(make_html(d),encoding="utf-8")
    print("Created UNAPPROVED editable preview:",output)
    if args.png or args.pdf:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise SystemExit("PNG/PDF preview requires playwright. HTML is available.")
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            page=browser.new_page(viewport={"width":1250,"height":1700},device_scale_factor=1)
            page.goto(output.as_uri())
            page.locator(".sheet").wait_for()
            if args.png:
                page.locator(".sheet").screenshot(path=str(Path(args.png).resolve()),animations="disabled")
                print("Wrote PNG preview:",args.png)
            if args.pdf:
                page.pdf(path=str(Path(args.pdf).resolve()),print_background=True,width="1122px",height="1500px")
                print("Wrote PDF preview:",args.pdf)
            browser.close()

if __name__ == "__main__":
    main()
