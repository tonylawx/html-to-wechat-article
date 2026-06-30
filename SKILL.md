---
name: html-to-wechat-article
description: Convert, restore, and clean HTML into WeChat Official Account article HTML so rich local/editor templates survive WeChat draft/add and paste workflows. Use when a user asks for HTML to WeChat article conversion, WeChat/微信公众号 HTML cleanup, article template restoration, draft-add-ready HTML, or fixing formatting that disappears, table borders, broken heading rules, or editor-export markup after publishing.
---

# WeChat HTML Restore

Use this skill to turn a visually approved WeChat article template into stable HTML that can be pasted into the editor or sent through official `draft/add`.

## Core Rule

Preserve the approved visual intent, not the original DOM. WeChat often rewrites editor HTML, exposes table borders, drops fragile attributes, and changes heading layout. Keep the visible typography and spacing, but simplify structures that are known to break.

## Agent-First Workflow

1. Inspect the source HTML in a browser or screenshot before changing it.
2. Identify the visible design contract: top metadata line, hero image, section labels, headings, body text, CTA/footer, QR, disclaimer.
3. Edit the HTML directly. Preserve visible content and inline styles that matter; simplify only the fragile DOM.
4. Re-open the edited HTML locally and compare against the source.
5. If publishing through official `draft/add`, prefer the simplified HTML when the original preview shows missing styles, table borders, fake indentation, or broken heading lines.
6. If the user has already confirmed that a raw rendered template survives `draft/add`, do not clean it again unless the mobile preview regresses.

This skill does not require Python. Use normal file-reading/search/editing tools. The optional script in `scripts/` is only a reference implementation for batch jobs.

## Manual Rewrite Rules

Apply these transformations intentionally, not blindly:

1. Remove editor-only attributes while keeping normal `style`, `src`, `href`, `alt`, and semantic attributes:
   - remove `leaf`
   - remove `mpa-font-style`
   - remove `data-*` unless the user explicitly needs editor-export fidelity
2. Remove hidden keyword blocks:
   - remove blocks styled with `display:none`, `visibility:hidden`, `opacity:0`, or `font-size:0`
   - keep visible, subtle SEO lines if the user asked for them
3. Replace layout tables:
   - convert `table`, `tbody`, `tr` wrappers to simple `section` or `div`
   - convert label `td` cells to `span`
   - keep real data tables only when the article genuinely contains tabular data
4. Stabilize headings:
   - if `h1/h2` render badly in WeChat mobile preview, replace them with styled `p` blocks
   - keep the visual font size, weight, color, and margins
   - avoid putting long Chinese titles on the same line as decorative rules
5. Normalize risky styles:
   - change `text-align:justify` to `text-align:left` when it creates fake indentation
   - change `text-indent` to `0`
   - reduce excessive Chinese heading `letter-spacing` to `0` or about `1px`
   - remove `max-width` if WeChat drops centering assumptions
   - add `box-sizing:border-box` to major containers when widths/padding matter

## What To Preserve

- Inline styles that define the approved look.
- The same article order and section rhythm.
- Visible SEO or keyword line if the user asked for it.
- Full-width header images and QR/follow images.
- CTA and disclaimer text.
- Bold ticker symbols or other meaningful emphasis.

## What To Remove Or Rewrite

- Editor-only attributes: `leaf`, `data-*`, `mpa-font-style`.
- Hidden SEO stuffing: `display:none`, zero-size hidden blocks, invisible keyword dumps.
- Tables used only for layout. Flatten `table/tr/td` into simpler `section/div/span` tags because WeChat may show cell borders.
- Fragile heading tags if mobile `draft/add` stretches or indents them. Use styled paragraphs when needed.
- Large `letter-spacing` on Chinese headings if it causes wrapping or fake indentation.
- `text-align:justify` when it makes Chinese text look indented or stretched in the WeChat mobile preview.
- Outer `max-width` assumptions that disappear after WeChat normalization.

## Stable Section Label Pattern

For short labels plus a rule, avoid tables:

```html
<section style="margin:0 0 12px 0;padding:0;text-align:left;line-height:1.2;border:0;">
  <span style="display:inline-block;vertical-align:middle;color:#2763e9;font-size:12px;font-weight:850;letter-spacing:0.12em;line-height:1.2;text-transform:uppercase;border:0;">1 · Market</span>
  <span style="display:inline-block;vertical-align:middle;width:56%;height:1px;margin:0 0 3px 10px;background:#d7e2ff;line-height:1px;font-size:0;border:0;"> </span>
</section>
```

Keep the section title below the label when titles can be long. Do not put the rule beside long Chinese titles; it will drop awkwardly on narrow mobile screens.

## Manual Example

Bad layout-table label:

```html
<table style="width:100%;">
  <tr>
    <td style="color:#2763e9;">1 · Market</td>
    <td style="border-bottom:1px solid #d7e2ff;"> </td>
  </tr>
</table>
<h2 style="letter-spacing:2px;text-align:justify;">1 市场仍在等方向</h2>
```

Stable replacement:

```html
<section style="margin:0 0 12px 0;padding:0;text-align:left;line-height:1.2;border:0;">
  <span style="display:inline-block;vertical-align:middle;color:#2763e9;font-size:12px;font-weight:850;letter-spacing:0.12em;line-height:1.2;text-transform:uppercase;border:0;">1 · Market</span>
  <span style="display:inline-block;vertical-align:middle;width:56%;height:1px;margin:0 0 3px 10px;background:#d7e2ff;line-height:1px;font-size:0;border:0;"> </span>
</section>
<p style="margin:0 0 16px 0;color:#2a2a34;font-size:22px;line-height:1.45;font-weight:850;text-align:left;letter-spacing:0;">市场仍在等方向</p>
```

## Images

For local previews, `file:///absolute/path/image.jpg` is fine. For official `draft/add`, local images must be uploaded to WeChat content image storage by the publishing workflow before draft creation. This skill only prepares the HTML shape; it does not call the WeChat API.

## Validation Checklist

Before handing off:

- The cleaned file opens locally and still looks like the approved article.
- No `leaf`, `mpa-font-style`, or unnecessary `data-*` attributes remain.
- Layout tables are gone unless they are real data tables.
- Section labels do not use `table` or `td`.
- Body copy has stable alignment and no fake first-line indentation.
- The output has one obvious root article container and no hidden keyword stuffing.
- A quick text search confirms no unexpected fragile tags/attributes remain.

## Bundled Resources

- `scripts/restore_wechat_html.py`: optional local cleaner and reporter for batch jobs; do not require it for normal agent use.
- `examples/`: before/after HTML and screenshot assets for quick orientation.
