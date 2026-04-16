#!/usr/bin/env python3
"""
Markdown → PDF Generator (zero-dependency fallback, or weasyprint if installed)
──────────────────────────────────────────────────────────────────────────────────
Converts the marketing Markdown docs to styled PDF files.

Usage:
    # Convert a single file
    python generate_pdf.py ../../sales_assets/marketing-offer/40-percent-leaked-leads.md

    # Specify output path
    python generate_pdf.py ../../sales_assets/marketing-offer/40-percent-leaked-leads.md -o /tmp/offer.pdf

    # Convert all .md files in a directory
    python generate_pdf.py ../../sales_assets/marketing-offer/

Dependencies (optional for styled output):
    pip install markdown weasyprint

If no dependencies are installed, falls back to a simple HTML file that can be
printed to PDF via any browser (Ctrl+P → Save as PDF).
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

# ── Minimal Markdown → HTML converter (no deps) ──────────────

def md_to_html(text: str) -> str:
    """Barebones Markdown → HTML. Handles headers, bold, lists, tables, hr, paragraphs."""
    lines = text.split("\n")
    out: list[str] = []
    in_list = False
    in_table = False
    in_code = False

    for line in lines:
        stripped = line.strip()

        # Code blocks
        if stripped.startswith("```"):
            if in_code:
                out.append("</pre>")
                in_code = False
            else:
                out.append("<pre style='background:#f1f5f9;padding:16px;border-radius:8px;overflow-x:auto;font-size:13px;direction:ltr;text-align:left'>")
                in_code = True
            continue
        if in_code:
            out.append(html.escape(line))
            continue

        # Headers
        m = re.match(r"^(#{1,6})\s+(.*)", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            continue

        # HR
        if re.match(r"^---+$", stripped):
            out.append("<hr>")
            continue

        # Table rows
        if "|" in stripped and not stripped.startswith("```"):
            cells = [c.strip() for c in stripped.split("|")]
            cells = [c for c in cells if c]
            if all(re.match(r"^-+$", c) for c in cells):
                continue  # separator row
            if not in_table:
                out.append("<table>")
                in_table = True
            tag = "th" if not any("<td" in o for o in out[-5:] if "<t" in o) and out[-1] == "<table>" else "td"
            out.append("<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False

        # Lists
        m = re.match(r"^[-*]\s+(.*)", stripped)
        m2 = re.match(r"^\d+[.)]\s+(.*)", stripped)
        if m or m2:
            if not in_list:
                tag = "ul" if m else "ol"
                out.append(f"<{tag}>")
                in_list = tag
            content = (m or m2).group(1)
            out.append(f"<li>{_inline(content)}</li>")
            continue
        if in_list and stripped == "":
            out.append(f"</{in_list}>")
            in_list = False
            continue

        # Blockquote
        if stripped.startswith(">"):
            out.append(f"<blockquote>{_inline(stripped[1:].strip())}</blockquote>")
            continue

        # Empty line
        if stripped == "":
            out.append("")
            continue

        # Paragraph
        out.append(f"<p>{_inline(stripped)}</p>")

    if in_list:
        out.append(f"</{in_list}>")
    if in_table:
        out.append("</table>")

    return "\n".join(out)


def _inline(text: str) -> str:
    """Convert inline Markdown (bold, italic, code, links)."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


# ── Styling ───────────────────────────────────────────────────

CSS = """
@page { size: A4; margin: 24mm 20mm; }
body {
    font-family: 'IBM Plex Sans Arabic', 'Segoe UI', system-ui, sans-serif;
    direction: rtl;
    color: #1e293b;
    line-height: 1.8;
    font-size: 14px;
    max-width: 680px;
    margin: 0 auto;
    padding: 40px 20px;
}
h1 { font-size: 28px; font-weight: 800; color: #0f172a; margin-top: 48px; }
h2 { font-size: 22px; font-weight: 700; color: #0f172a; margin-top: 36px; border-bottom: 2px solid #00D4AA; padding-bottom: 8px; }
h3 { font-size: 18px; font-weight: 700; margin-top: 24px; }
p { margin: 10px 0; }
strong { color: #0f172a; }
table { width: 100%; border-collapse: collapse; margin: 16px 0; }
th, td { border: 1px solid #e2e8f0; padding: 10px 14px; text-align: right; }
th { background: #f1f5f9; font-weight: 700; }
blockquote { border-right: 4px solid #00D4AA; margin: 16px 0; padding: 12px 20px; background: #f0fdfa; border-radius: 0 8px 8px 0; }
hr { border: none; border-top: 2px solid #e2e8f0; margin: 32px 0; }
code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
ul, ol { padding-right: 24px; }
li { margin: 6px 0; }
a { color: #0891b2; }
"""


def wrap_html(body: str, title: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
{body}
<footer style="margin-top:48px;padding-top:16px;border-top:1px solid #e2e8f0;font-size:12px;color:#94a3b8;text-align:center">
Dealix — مبني في السعودية | متوافق مع PDPL
</footer>
</body>
</html>"""


# ── Conversion ────────────────────────────────────────────────

def convert_file(md_path: Path, output: Path | None = None) -> Path:
    """Convert a Markdown file to PDF (or HTML fallback)."""
    text = md_path.read_text(encoding="utf-8")
    title = md_path.stem.replace("-", " ").replace("_", " ").title()

    # Try weasyprint first
    try:
        import markdown
        body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    except ImportError:
        body = md_to_html(text)

    full_html = wrap_html(body, title)

    try:
        from weasyprint import HTML
        out = output or md_path.with_suffix(".pdf")
        HTML(string=full_html).write_pdf(str(out))
        print(f"✓ PDF: {out}")
        return out
    except ImportError:
        # Fallback: save as HTML (user can print to PDF from browser)
        out = output or md_path.with_suffix(".html")
        if str(out).endswith(".pdf"):
            out = out.with_suffix(".html")
        out.write_text(full_html, encoding="utf-8")
        print(f"✓ HTML (weasyprint not installed — open in browser and Ctrl+P to save as PDF): {out}")
        return out


def convert_directory(dir_path: Path) -> list[Path]:
    """Convert all .md files in a directory."""
    results = []
    for md in sorted(dir_path.glob("*.md")):
        results.append(convert_file(md))
    return results


# ── CLI ───────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert marketing Markdown to PDF")
    parser.add_argument("input", help="Markdown file or directory")
    parser.add_argument("-o", "--output", help="output file path")
    args = parser.parse_args(argv)

    inp = Path(args.input)
    if inp.is_dir():
        results = convert_directory(inp)
        print(f"\n✓ Converted {len(results)} files")
    elif inp.is_file():
        out = Path(args.output) if args.output else None
        convert_file(inp, out)
    else:
        print(f"[error] Not found: {inp}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
