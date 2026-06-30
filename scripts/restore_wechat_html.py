#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from html import unescape
from pathlib import Path


EDITOR_ATTR_PATTERNS = [
    r'\s+leaf="[^"]*"',
    r"\s+leaf='[^']*'",
    r'\s+mpa-font-style="[^"]*"',
    r"\s+mpa-font-style='[^']*'",
    r'\s+data-[a-zA-Z0-9_-]+="[^"]*"',
    r"\s+data-[a-zA-Z0-9_-]+='[^']*'",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Restore/simplify WeChat article HTML for paste or official draft/add."
    )
    parser.add_argument("input", type=Path, help="Input HTML file.")
    parser.add_argument("-o", "--output", type=Path, help="Output HTML file. Defaults to <input>.wechat.html")
    parser.add_argument(
        "--keep-sections",
        action="store_true",
        help="Keep <section> tags instead of flattening them to <div>.",
    )
    parser.add_argument(
        "--keep-headings",
        action="store_true",
        help="Keep h1/h2 tags instead of converting them to styled paragraphs.",
    )
    parser.add_argument(
        "--keep-tables",
        action="store_true",
        help="Keep table/tr/td tags. Use for real data/comparison tables; by default layout tables are flattened.",
    )
    parser.add_argument(
        "--keep-justify",
        action="store_true",
        help="Keep text-align:justify instead of normalizing it to left.",
    )
    parser.add_argument(
        "--keep-max-width",
        action="store_true",
        help="Keep max-width style declarations.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print a small before/after stability report.",
    )
    return parser.parse_args()


def strip_editor_attrs(html: str) -> str:
    for pattern in EDITOR_ATTR_PATTERNS:
        html = re.sub(pattern, "", html)
    return html


def normalize_styles(
    style_text: str,
    *,
    keep_justify: bool = False,
    keep_max_width: bool = False,
) -> str:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for raw in [part.strip() for part in style_text.split(";") if part.strip()]:
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        normalized_value = re.sub(r"\s*!important\s*$", "", value, flags=re.I).strip().lower()

        if key == "text-align" and normalized_value == "justify" and not keep_justify:
            value = "left !important"
        elif key == "text-align" and normalized_value == "left":
            value = "left !important"
        if key == "max-width" and not keep_max_width:
            continue
        if key == "margin" and value.lower() == "0 auto":
            value = "0"
        if key == "text-indent":
            value = "0"
        if key in {"padding-left", "margin-left"} and value.lower() in {"auto", "inherit"}:
            value = "0"
        if key == "letter-spacing" and value.endswith("px"):
            try:
                px_value = float(value[:-2])
            except ValueError:
                px_value = None
            if px_value is not None and px_value > 1.2:
                value = "1px"

        if key in seen:
            entries = [(k, v) for k, v in entries if k != key]
        entries.append((key, value))
        seen.add(key)

    values_by_key = {key: value for key, value in entries}
    align = re.sub(r"\s*!important\s*$", "", values_by_key.get("text-align", ""), flags=re.I).strip().lower()
    if align == "left":
        for key, value in {
            "text-align-last": "left",
            "letter-spacing": "0",
            "word-spacing": "normal",
            "white-space": "normal",
            "word-break": "normal",
        }.items():
            if key not in seen:
                entries.append((key, value))
                seen.add(key)
    if "box-sizing" not in seen:
        entries.append(("box-sizing", "border-box"))
    return ";".join(f"{key}:{value}" for key, value in entries) + ";"


def normalize_style_attrs(
    html: str,
    *,
    keep_justify: bool = False,
    keep_max_width: bool = False,
) -> str:
    def replace(match: re.Match[str]) -> str:
        quote = match.group(1)
        style_text = match.group(2)
        style = normalize_styles(
            style_text,
            keep_justify=keep_justify,
            keep_max_width=keep_max_width,
        )
        return f"style={quote}{style}{quote}"

    return re.sub(r'style=(["\'])(.*?)\1', replace, html, flags=re.I | re.S)


def flatten_sections(html: str) -> str:
    html = re.sub(r"<(/?)section\b", r"<\1div", html, flags=re.I)
    return html


def downgrade_headings(html: str) -> str:
    def replace_heading(match: re.Match[str]) -> str:
        attrs = match.group(2) or ""
        inner = match.group(3)
        return f"<p{attrs}>{inner}</p>"

    return re.sub(r"<(h[12])([^>]*)>(.*?)</\1>", replace_heading, html, flags=re.I | re.S)


def flatten_layout_tables(html: str) -> str:
    replacements = [
        (r"<(/?)table\b", r"<\1div"),
        (r"<(/?)tbody\b", r"<\1div"),
        (r"<(/?)thead\b", r"<\1div"),
        (r"<(/?)tfoot\b", r"<\1div"),
        (r"<(/?)tr\b", r"<\1div"),
        (r"<(/?)td\b", r"<\1span"),
        (r"<(/?)th\b", r"<\1span"),
    ]
    for pattern, repl in replacements:
        html = re.sub(pattern, repl, html, flags=re.I)
    return html


def text_content(html_fragment: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", html_fragment)).strip()


def remove_hidden_keyword_blocks(html: str) -> str:
    always_hidden = r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0"
    zero_font = r"font-size\s*:\s*0(?:px|em|rem|%)?\b"

    def remove_by_style(
        source: str,
        style_pattern: str,
        *,
        require_text: bool = False,
    ) -> str:
        def replace(match: re.Match[str]) -> str:
            inner = match.group(3)
            if require_text and not text_content(inner):
                return match.group(0)
            return ""

        for quote in ('"', "'"):
            source = re.sub(
                rf"<([a-z0-9]+)([^>]*style={quote}[^>]*(?:{style_pattern})[^>]*{quote}[^>]*)>(.*?)</\1>",
                replace,
                source,
                flags=re.I | re.S,
            )
        return source

    html = remove_by_style(html, always_hidden)
    html = remove_by_style(html, zero_font, require_text=True)
    return html


def clean_html(html: str, args: argparse.Namespace) -> str:
    html = html.replace("\r\n", "\n").replace("\r", "\n").strip()
    html = strip_editor_attrs(html)
    html = remove_hidden_keyword_blocks(html)
    if not args.keep_sections:
        html = flatten_sections(html)
    if not args.keep_headings:
        html = downgrade_headings(html)
    if not args.keep_tables:
        html = flatten_layout_tables(html)
    html = normalize_style_attrs(
        html,
        keep_justify=args.keep_justify,
        keep_max_width=args.keep_max_width,
    )
    html = re.sub(r">\s+<", "><", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html + "\n"


def count(pattern: str, html: str) -> int:
    return len(re.findall(pattern, html, flags=re.I | re.S))


def report(before: str, after: str) -> str:
    rows = [
        ("bytes", len(before), len(after)),
        ("section tags", count(r"</?section\b", before), count(r"</?section\b", after)),
        ("table tags", count(r"</?table\b|</?td\b", before), count(r"</?table\b|</?td\b", after)),
        ("h1/h2 tags", count(r"</?h[12]\b", before), count(r"</?h[12]\b", after)),
        ("editor attrs", sum(count(p, before) for p in EDITOR_ATTR_PATTERNS), sum(count(p, after) for p in EDITOR_ATTR_PATTERNS)),
        ("hidden markers", count(r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0|font-size\s*:\s*0", before), count(r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0|font-size\s*:\s*0", after)),
    ]
    lines = ["metric,before,after"]
    lines.extend(f"{name},{before_value},{after_value}" for name, before_value, after_value in rows)
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")
    output = args.output or args.input.with_suffix(".wechat.html")
    before = args.input.read_text(encoding="utf-8")
    after = clean_html(before, args)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(after, encoding="utf-8")
    if args.report:
        print(report(before, after))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
