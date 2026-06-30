---
name: wechat-html-restore
description: Restore and clean WeChat Official Account article HTML so rich local/editor templates survive WeChat draft/add and paste workflows. Use when a user asks to convert, sanitize, repair, stabilize, or make a WeChat/微信公众号 article template copyable or draft-add-ready, especially when formatting disappears, table borders appear, heading rules wrap badly, or editor-export markup renders differently after publishing.
---

# WeChat HTML Restore

Use this skill to turn a visually approved WeChat article template into stable HTML that can be pasted into the editor or sent through official `draft/add`.

## Core Rule

Preserve the approved visual intent, not the original DOM. WeChat often rewrites editor HTML, exposes table borders, drops fragile attributes, and changes heading layout. Keep the visible typography and spacing, but simplify structures that are known to break.

## Workflow

1. Inspect the source HTML in a browser or screenshot before changing it.
2. Identify the visible design contract: top metadata line, hero image, section labels, headings, body text, CTA/footer, QR, disclaimer.
3. Run the local cleaner:

```bash
python3 scripts/restore_wechat_html.py input.html -o output.wechat.html --report
```

4. Re-open the cleaned HTML locally and compare against the source.
5. If publishing through official `draft/add`, prefer the cleaned HTML when the original preview shows missing styles, table borders, fake indentation, or broken heading lines.
6. If the user has already confirmed that a raw rendered template survives `draft/add`, do not clean it again unless the mobile preview regresses.

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
- Tables used only for layout. The bundled cleaner flattens `table/tr/td` into simpler `div/span` tags by default because WeChat may show cell borders.
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
- The report from `restore_wechat_html.py --report` has no unexpected warnings.

## Bundled Resources

- `scripts/restore_wechat_html.py`: local cleaner and reporter.
- `examples/`: before/after HTML and screenshot assets for quick orientation.
