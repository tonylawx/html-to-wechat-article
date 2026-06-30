---
name: html-to-wechat-article
description: Convert, restore, and clean HTML into WeChat Official Account article HTML with near-100% visual restoration of the approved template while surviving WeChat draft/add and paste workflows. Use when a user asks for HTML to WeChat article conversion, WeChat/微信公众号 HTML cleanup, article template restoration, draft-add-ready HTML, or fixing formatting that disappears, table borders, broken heading rules, or editor-export markup after publishing.
---

# WeChat HTML Restore

Use this skill to turn a visually approved WeChat article template into stable HTML that can be pasted into the editor or sent through official `draft/add`, while aiming for near-100% visual restoration of the original design.

## Core Rule

Preserve the approved visual result almost exactly. Do not redesign, restyle, summarize, or "improve" the article unless the user asks. WeChat often rewrites editor HTML, exposes table borders, drops fragile attributes, and changes heading layout, so the DOM may change, but the reader-facing result should stay as close as possible to the source. Treat near-100% visual restoration as the goal; change markup only where the original DOM is likely to break in WeChat.

## Agent-First Workflow

1. Inspect the source HTML in a browser or screenshot before changing it.
2. Identify the visible design contract: top metadata line, hero image, section labels, headings, body text, CTA/footer, QR, disclaimer.
3. Edit the HTML directly. Preserve visible content, spacing, colors, typography, image sizing, and inline styles that matter; simplify only the fragile DOM.
4. Re-open the edited HTML locally and compare against the source.
5. Decide the publishing path before changing markup: local preview, editor paste, and official `draft/add` can render the same HTML differently.
6. If the user has already confirmed that a raw rendered template survives the target path, do not clean it again unless the mobile preview regresses.
7. If publishing through official `draft/add`, prefer the simplified HTML when the original preview shows missing styles, table borders, fake indentation, stretched Chinese text, or broken heading lines.

This skill does not require Python. Use normal file-reading/search/editing tools. The optional script in `scripts/` is only a reference implementation for batch jobs.

## Manual Rewrite Rules

Apply these transformations intentionally, not blindly:

1. Remove editor-only attributes while keeping normal `style`, `src`, `href`, `alt`, and semantic attributes:
   - remove `leaf`
   - remove `mpa-font-style`
   - remove `data-*` unless the user explicitly needs editor-export fidelity
2. Remove hidden keyword blocks:
   - remove blocks styled with `display:none`, `visibility:hidden`, or `opacity:0`
   - treat `font-size:0` as hidden only when the block carries hidden text; keep empty decorative rule spans that use `font-size:0`
   - keep visible, subtle SEO lines if the user asked for them
3. Replace layout tables:
   - convert `table`, `tbody`, `tr` wrappers to simple `section` or `div`
   - convert label `td` cells to `span`
   - keep real data tables only when the article genuinely contains tabular data; use the bundled script with `--keep-tables` for comparison tables or parameter grids
4. Stabilize headings:
   - if `h1/h2` render badly in WeChat mobile preview, replace them with styled `p` blocks
   - keep the visual font size, weight, color, and margins
   - avoid putting long Chinese titles on the same line as decorative rules
5. Normalize risky styles:
   - change `text-align:justify` to `text-align:left !important` when it creates fake indentation
   - change `text-indent` to `0`
   - reduce excessive Chinese heading `letter-spacing` to `0` or about `1px`
   - remove `max-width` if WeChat drops centering assumptions
   - add `box-sizing:border-box` to major containers when widths/padding matter
   - for body copy that will go through `draft/add`, prefer `text-align:left !important;text-align-last:left;letter-spacing:0;word-spacing:normal;white-space:normal;word-break:normal`

## What To Preserve

- The approved visual design as close to 100% as WeChat allows.
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

Body images and cover images use different WeChat API concepts. Body images are uploaded to content image storage and the returned hosted `url` replaces the HTML `src`; cover thumbnails need a `thumb_media_id`. Do not expect a body-image upload to return a reusable cover `media_id`.

## Publishing Boundaries

- Keep this skill focused on HTML shape. If `draft/add` fails with credentials, IP whitelist, proxy, SSH, or other network errors, diagnose the publishing workflow before rewriting the article.
- Do not add `content_source_url`, source links, video links, or provenance footers unless the user explicitly asks for them.
- If the WeChat draft title is supplied as API metadata, avoid repeating the same H1 title inside the body unless the approved visual template includes a visible title block.
- Before handoff to a publisher, confirm local `file://` images and relative image paths will be uploaded or converted by that publisher.

## Validation Checklist

Before handing off:

- The cleaned file opens locally and still looks like the approved article.
- No `leaf`, `mpa-font-style`, or unnecessary `data-*` attributes remain.
- Layout tables are gone unless they are real data tables.
- Section labels do not use `table` or `td`.
- Body copy has stable alignment and no fake first-line indentation.
- Real data tables, if any, still retain their information structure.
- Official `draft/add` output has no unintended duplicate title block.
- Any local image paths are accounted for by the downstream publishing workflow.
- The output has one obvious root article container and no hidden keyword stuffing.
- A quick text search confirms no unexpected fragile tags/attributes remain.

## Bundled Resources

- `scripts/restore_wechat_html.py`: optional local cleaner and reporter for batch jobs; do not require it for normal agent use. Use `--keep-tables` when tables are real article content rather than layout.
- `examples/`: before/after HTML and screenshot assets for quick orientation.
