#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 guide 仓库的 Markdown 正文编译成一本 PDF 手册。

用法：
    python scripts/build_handbook.py                       # 输出到 dist/
    python scripts/build_handbook.py --out custom.pdf      # 指定输出文件
    python scripts/build_handbook.py --html only           # 只生成 HTML，不调浏览器
    python scripts/build_handbook.py --channel chrome      # 指定本机 Chrome 通道

依据：markdown 负责渲染正文，Playwright 驱动 Chromium 打印为 A4 PDF
（页眉页脚页码、书签目录由浏览器生成）。网络不通时图片会退化为占位提示，
不会中断构建。
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
TITLE = "宁夏大学鑫启网安俱乐部 · 入门手册"
ORG = "宁夏大学鑫启网安俱乐部"
SHORT = "XinQi Cyber Club"

# 目录收录到节（h2）；三级标题仍会进入 PDF 书签
TOC_LEVELS = 2

# 正文顺序：总览在前，章节按文件名顺序
CHAPTERS = ["README.md"] + sorted(p.name for p in ROOT.glob("0*.md"))

CSS = r"""
@page { size: A4; }

html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

body {
  margin: 0;
  color: #1f2328;
  font-family: "Source Han Sans SC", "Noto Sans SC", "Microsoft YaHei",
               "PingFang SC", "Hiragino Sans GB", "WenQuanYi Micro Hei", sans-serif;
  font-size: 10.5pt;
  line-height: 1.8;
}

/* ---------- 封面 ---------- */
.cover { text-align: center; padding-top: 55mm; }
.cover .org { font-size: 13pt; letter-spacing: 4px; color: #57606a; }
.cover h1 {
  margin: 14mm 0 6mm;
  font-size: 24pt;
  letter-spacing: 2px;
  border: 0;
  padding: 0;
}
.cover .rule { width: 42mm; height: 3px; margin: 0 auto 8mm; background: #1f6feb; }
.cover .sub { font-size: 12pt; color: #57606a; }
.cover .meta {
  width: 120mm;
  margin: 46mm auto 0;
  font-size: 10pt;
  color: #57606a;
  line-height: 2.1;
}
.cover .meta td { padding: 1.4mm 4mm; }
.cover .meta td:first-child { width: 22mm; color: #8c959f; }

/* ---------- 目录 ---------- */
.toc { page-break-before: always; }
.toc h1 { border-bottom: 2px solid #1f6feb; }
.toc ul { list-style: none; margin: 0; padding-left: 0; }
.toc li { margin: 2.4mm 0; display: flex; align-items: baseline; }
.toc li a { flex: 0 0 auto; }
.toc .dots {
  flex: 1 1 auto;
  min-width: 6mm;
  margin: 0 2mm;
  border-bottom: 0.5pt dotted #c3ccd6;
  transform: translateY(-1.2mm);
}
.toc .pg { flex: none; white-space: nowrap; color: #57606a; font-size: 9.5pt; font-variant-numeric: tabular-nums; }
.toc .l1 { font-weight: 700; font-size: 11.5pt; margin-top: 5mm; }
.toc .l2 { padding-left: 7mm; font-size: 10.5pt; }
.toc .l3 { padding-left: 14mm; font-size: 10pt; color: #57606a; }
.toc a { color: inherit; text-decoration: none; border-bottom: 0; }

.sentinel { font-size: 1pt; color: #ffffff; }

/* ---------- 正文 ---------- */
.chapter { page-break-before: always; }

h1, h2, h3, h4 { line-height: 1.45; page-break-after: avoid; }
h1 {
  font-size: 19pt;
  margin: 0 0 6mm;
  padding-bottom: 2.5mm;
  border-bottom: 2px solid #1f6feb;
}
h2 {
  font-size: 14pt;
  margin: 9mm 0 3mm;
  padding-left: 3mm;
  border-left: 4px solid #1f6feb;
}
h3 { font-size: 11.5pt; margin: 6mm 0 2mm; }
h4 { font-size: 10.5pt; margin: 4mm 0 1.5mm; color: #24292f; }

p { margin: 0 0 2.6mm; }
ul, ol { margin: 0 0 2.8mm; padding-left: 7mm; }
li { margin: 0.8mm 0; }
li > ul, li > ol { margin-top: 1mm; }

a { color: #0b5cad; text-decoration: none; border-bottom: 0.4pt solid #c9d6e4; }

code {
  font-family: "Cascadia Mono", Consolas, "DejaVu Sans Mono", monospace;
  font-size: 9pt;
  background: #f2f4f7;
  border-radius: 2px;
  padding: 0.4mm 1.2mm;
}

pre {
  background: #f6f8fa;
  border: 0.5pt solid #d8dee4;
  border-left: 3px solid #1f6feb;
  border-radius: 2px;
  padding: 3mm 4mm;
  margin: 0 0 3mm;
  page-break-inside: avoid;
}
pre code {
  background: none;
  padding: 0;
  font-size: 8.8pt;
  line-height: 1.62;
  white-space: pre-wrap;
  word-break: break-word;
}

blockquote {
  margin: 0 0 3mm;
  padding: 2mm 4mm;
  background: #f6f8fa;
  border-left: 3px solid #8c959f;
  color: #48505a;
}
blockquote p:last-child { margin-bottom: 0; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 4mm;
  font-size: 9.6pt;
  page-break-inside: avoid;
}
th, td {
  border: 0.5pt solid #cfd8e3;
  padding: 1.6mm 2.4mm;
  text-align: left;
  vertical-align: top;
}
th { background: #eef2f7; font-weight: 700; }
tbody tr:nth-child(even) td { background: #fafbfc; }
table code { font-size: 8.8pt; }

hr {
  border: 0;
  border-top: 0.5pt solid #d8dee4;
  margin: 5mm 0;
}

img { max-width: 65%; height: auto; }

div[align="center"] { text-align: center; }
div[align="center"] img { max-width: 46%; display: block; margin: 3mm auto; }

/* 章末的“适用环境 / 最近校订” */
p.meta {
  margin-top: 6mm;
  padding-top: 2.5mm;
  border-top: 0.5pt dashed #cfd8e3;
  color: #6a737d;
  font-size: 9pt;
}
p.meta span { margin-right: 6mm; }

.img-missing {
  display: block;
  padding: 4mm;
  border: 0.5pt dashed #cfd8e3;
  color: #8c959f;
  font-size: 9pt;
  text-align: center;
}
"""


# ---------------------------------------------------------------- Markdown 渲染


def slugify(value: str) -> str:
    """尽量贴近 GitHub 的锚点算法：小写、去标点、空格转连字符、保留中文。"""
    value = value.strip().lower()
    out = []
    for ch in value:
        if ch.isalnum() or "\u4e00" <= ch <= "\u9fff":
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    return re.sub(r"-{2,}", "-", "".join(out)).strip("-")


MD = markdown.Markdown(
    extensions=["extra", "sane_lists", "toc"],
    extension_configs={"toc": {"slugify": lambda v, s: slugify(v)}},
)


def chapter_index(name: str) -> int:
    return CHAPTERS.index(name)


def render_chapter(name: str) -> tuple[str, list[tuple[int, str, str]]]:
    """返回（片段 HTML，[(层级, id, 纯文本)…]）。"""
    text = (ROOT / name).read_text(encoding="utf-8")

    if name == "README.md":
        # 封面已有书名，正文里这篇当“总览”用
        text = re.sub(r"^#\s+.*$", "# 总览", text, count=1, flags=re.M)

    MD.reset()
    body = MD.convert(text)
    idx = chapter_index(name)

    # 标题加章节前缀，避免跨章重复 id
    headings: list[tuple[int, str, str]] = []

    def add_id(m: re.Match) -> str:
        level, inner = int(m.group(1)), m.group(3)
        plain = re.sub(r"<[^>]+>", "", inner).strip()
        hid = f"c{idx}-{slugify(plain)}"
        headings.append((level, hid, plain))
        return f'<h{level} id="{hid}">{inner}</h{level}>'

    body = re.sub(r"<h([1-4])([^>]*)>(.*?)</h\1>", add_id, body, flags=re.S)

    # 章末元信息
    body = re.sub(
        r"<p>(适用环境：[^<]*)</p>", r'<p class="meta">\1</p>', body
    )
    body = body.replace("<p class=\"meta\">适用环境：", "<p class=\"meta\"><span>适用环境：")
    body = re.sub(
        r'<p class="meta"><span>(适用环境：[^<]*?)最近校订：(.*?)</p>',
        r'<p class="meta"><span>\1</span><span>最近校订：\2</span></p>',
        body,
    )

    # 章节间引用：00-xxx.md#frag -> 本文档内部锚点
    def relink(m: re.Match) -> str:
        target, frag = m.group(1), m.group(2)
        if target not in CHAPTERS:
            return m.group(0)
        base = f"#c{chapter_index(target)}"
        return base + (f"-{slugify(frag)}" if frag else "")

    body = re.sub(
        r'href="([0-9A-Za-z\u4e00-\u9fff\-]+\.md)(?:#([^"]+))?"', relink, body
    )

    return f'<section class="chapter" id="ch-{idx}">\n{body}\n</section>', headings


# ---------------------------------------------------------------- 资源本地化

IMG_CACHE = ROOT / "build" / "img"


def localize_images(fragment: str) -> str:
    def repl(m: re.Match) -> str:
        url = m.group(1)
        if not url.startswith(("http://", "https://")):
            return m.group(0)
        IMG_CACHE.mkdir(parents=True, exist_ok=True)
        name = re.sub(r"[^A-Za-z0-9._-]", "_", url.rsplit("/", 1)[-1]) or "img"
        dest = IMG_CACHE / name
        if not dest.exists():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "handbook-build"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    dest.write_bytes(resp.read())
            except Exception as exc:  # 离线也要能出书
                print(f"  ! 图片下载失败，已跳过：{url}（{exc}）", file=sys.stderr)
                return f'<span class="img-missing">图片未能内嵌：{html.escape(url)}</span>'
        return f'src="{dest.as_uri()}"'

    return re.sub(r'src="([^"]+)"', repl, fragment)


# ---------------------------------------------------------------- HTML 组装


def build_html(version: str, pages: dict[str, int] | None = None) -> tuple[str, list[tuple[int, str, str]]]:
    frags, headings = [], []
    for name in CHAPTERS:
        frag, hs = render_chapter(name)
        frags.append(localize_images(frag))
        headings.extend(hs)

    toc_items = []
    for level, hid, text in headings:
        if level > TOC_LEVELS:
            continue
        page = (pages or {}).get(hid)
        pg = f'<span class="pg">{page}</span>' if page else '<span class="pg"></span>'
        toc_items.append(
            f'<li class="l{level}"><a href="#{hid}">{html.escape(text)}</a>'
            f'<span class="dots"></span>{pg}</li>'
        )
    toc = "\n".join(toc_items)
    # 正文起点标记，供第二遍定位页码时跳过封面与目录页
    frags[0] = re.sub(
        r'(<section class="chapter"[^>]*>)',
        r'\1<span class="sentinel">@@BODY@@</span>',
        frags[0],
        count=1,
    )

    today = dt.date.today().strftime("%Y 年 %m 月 %d 日")
    doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{TITLE}</title>
<style>{CSS}</style>
</head>
<body>

<section class="cover">
  <div class="org">{ORG}</div>
  <h1>{TITLE}</h1>
  <div class="rule"></div>
  <div class="sub">新成员入门教程 · 共 {len(CHAPTERS)} 篇</div>
  <table class="meta">
    <tr><td>版本</td><td>{html.escape(version)}</td></tr>
    <tr><td>编制</td><td>{ORG}</td></tr>
    <tr><td>日期</td><td>{today}</td></tr>
    <tr><td>仓库</td><td>github.com/NingXia-XinQiCyberClub/guide</td></tr>
  </table>
</section>

<section class="toc">
  <h1>目录</h1>
  <ul>
{toc}
  </ul>
</section>

{chr(10).join(frags)}

</body>
</html>
"""
    return doc, headings


# ---------------------------------------------------------------- 目录页码


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def locate_pages(pdf: Path, headings: list[tuple[int, str, str]]) -> dict[str, int]:
    """按阅读顺序逐页扫描，给每个标题找出所在页码（含封面页偏移）。"""
    import pymupdf

    doc = pymupdf.open(pdf)
    page_text = [_norm(p.get_text()) for p in doc]
    total = len(page_text)

    start = next((i for i, t in enumerate(page_text) if "@@BODY@@" in t), 0)
    result: dict[str, int] = {}
    cursor = start

    for level, hid, text in headings:
        if level > TOC_LEVELS:
            continue
        needle = _norm(text)
        if not needle:
            continue
        found = None
        for i in range(cursor, total):
            if needle in page_text[i]:
                found = i
                break
        if found is None:  # 跨行断字等情况，退回全文档搜索
            for i in range(start, total):
                if needle in page_text[i]:
                    found = i
                    break
        if found is not None:
            result[hid] = found + 1
            cursor = found
        else:
            print(f"  ! 目录页码定位失败：{text}", file=sys.stderr)
    doc.close()
    return result


# ---------------------------------------------------------------- 打印


def print_pdf(html_path: Path, out: Path, channel: str | None) -> int:
    """封面与正文分开打印：封面不带页眉页码，正文从第 1 页编号，最后合并。"""
    from playwright.sync_api import sync_playwright

    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.parent / f".{out.stem}-parts"
    tmp.mkdir(exist_ok=True)
    cover_pdf, body_pdf = tmp / "cover.pdf", tmp / "body.pdf"

    header = (
        '<div style="width:100%;font-size:8pt;color:#8c959f;'
        'font-family:sans-serif;padding:0 16mm;display:flex;'
        'justify-content:space-between;">'
        f'<span>{TITLE}</span><span>{ORG}</span></div>'
    )
    footer = (
        '<div style="width:100%;font-size:8pt;color:#8c959f;'
        'font-family:sans-serif;text-align:center;">'
        '<span class="pageNumber"></span> / <span class="totalPages"></span></div>'
    )
    margins = {"top": "20mm", "bottom": "18mm", "left": "18mm", "right": "18mm"}
    common = dict(
        format="A4", print_background=True, tagged=True,
        margin=margins, prefer_css_page_size=False,
    )

    with sync_playwright() as p:
        launch = {"args": ["--font-render-hinting=none"]}
        try:
            browser = p.chromium.launch(channel=channel, **launch) if channel else p.chromium.launch(**launch)
        except Exception:
            browser = p.chromium.launch(**launch)

        # 1) 封面：隐藏目录与正文
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="load")
        page.emulate_media(media="print")
        page.add_style_tag(content=".toc, .chapter { display: none !important; }")
        page.wait_for_timeout(500)
        page.pdf(path=str(cover_pdf), **common)
        page.close()

        # 2) 正文：隐藏封面，带页眉与页码
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="load")
        page.emulate_media(media="print")
        page.add_style_tag(content=".cover { display: none !important; }")
        page.wait_for_timeout(800)  # 给本地图片一点解码时间
        page.pdf(
            path=str(body_pdf), outline=True, display_header_footer=True,
            header_template=header, footer_template=footer, **common,
        )
        page.close()
        browser.close()

    return merge_pdfs([cover_pdf, body_pdf], out)


def merge_pdfs(parts: list[Path], out: Path) -> int:
    """合并分册；没有 pypdf 时退化为正文单册。"""
    try:
        from pypdf import PdfWriter
    except ImportError:
        print("  ! 未安装 pypdf，跳过封面/正文合并", file=sys.stderr)
        parts[-1].replace(out)
        return 0

    writer = PdfWriter()
    for part in parts:
        writer.append(str(part))
    with out.open("wb") as fh:
        writer.write(fh)
    pages = len(writer.pages)
    for part in parts:
        part.unlink(missing_ok=True)
    try:
        parts[0].parent.rmdir()
    except OSError:
        pass
    return pages


def git_describe() -> str:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return commit
    except Exception:
        return "unknown"


def write_notes(path: Path, version: str, pdf_name: str) -> None:
    today = dt.date.today().strftime("%Y-%m-%d")
    lines = [
        f"# {TITLE}",
        "",
        f"`{pdf_name}` · {version} · 构建于 {today}（源码 `{git_describe()}`）",
        "",
        "## 收录内容",
        "",
    ]
    for name in CHAPTERS:
        if name == "README.md":
            lines.append(f"- 总览：阅读路线、完成标准与入门任务（`{name}`）")
            continue
        first = (ROOT / name).read_text(encoding="utf-8").splitlines()[0]
        lines.append(f"- {first.lstrip('# ').strip()}（`{name}`）")
    lines += [
        "",
        "## 说明",
        "",
        "A4 排版，含封面、带页码的目录与 PDF 书签，可直接打印，也可在阅读器里按书签跳转。",
        "内容由仓库内的 `scripts/build_handbook.py` 从 Markdown 正文自动编译，以 `main` 分支为准；",
        "发现错漏请按贡献指南提交变更请求。",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_with_page_numbers(
    html_path: Path, out: Path, headings: list[tuple[int, str, str]],
    channel: str | None, version: str = "",
) -> tuple[int, dict[str, int]]:
    """反复出稿直到“标在目录上的页码”与“实际页码”一致（最多 4 轮）。"""
    page_map: dict[str, int] = {}
    for attempt in range(1, 5):
        doc, _ = build_html(version, page_map)
        html_path.write_text(doc, encoding="utf-8")
        draft = ROOT / "build" / f"round{attempt}.pdf"
        pages = print_pdf(html_path, draft, channel)
        measured = locate_pages(draft, headings)
        if measured == page_map or attempt == 4:
            if measured != page_map:
                print("  ! 目录页码未收敛，已使用最后一版", file=sys.stderr)
            out.parent.mkdir(parents=True, exist_ok=True)
            draft.replace(out)
            return pages, measured
        page_map = measured
    return 0, page_map  # 理论不可达


def main() -> int:
    ap = argparse.ArgumentParser(description=f"构建《{TITLE}》PDF")
    ap.add_argument("--out", default=ROOT / "dist" / f"{TITLE}.pdf", type=Path)
    ap.add_argument("--html", action="store_true", help="只生成 HTML，不打印 PDF")
    ap.add_argument("--channel", default=None, help="浏览器通道，如 chrome / msedge")
    ap.add_argument("--version", default=None, help="封面上的版本号，默认取 git describe")
    ap.add_argument("--notes", type=Path, default=None, help="另外写一份发布说明")
    ap.add_argument("--no-toc-pages", action="store_true", help="目录不标注页码（单遍构建）")
    args = ap.parse_args()

    version = args.version or f"main@{git_describe()}"
    out = Path(args.out)
    html_path = ROOT / "build" / "handbook.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"· 源码目录 {ROOT}")
    print(f"· 章节 {len(CHAPTERS)} 篇：{', '.join(CHAPTERS)}")

    doc, headings = build_html(version)
    html_path.write_text(doc, encoding="utf-8")
    print(f"· HTML  {html_path}")

    if not args.html:
        if args.no_toc_pages:
            pages = print_pdf(html_path, out, args.channel)
        else:
            pages, page_map = build_with_page_numbers(
                html_path, out, headings, args.channel, version
            )
            print(f"· 目录  已标注 {len(page_map)} 条页码")
        size = out.stat().st_size / 1024
        extra = f"，{pages} 页" if pages else ""
        print(f"· PDF   {out}（{size:.0f} KB{extra}）")

    if args.notes:
        write_notes(Path(args.notes), version, out.name)
        print(f"· 说明  {args.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
