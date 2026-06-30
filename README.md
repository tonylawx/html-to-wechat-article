# HTML to WeChat Article Skill

[中文文档](README.zh-CN.md)

A Codex skill for converting, cleaning, and restoring HTML into WeChat Official Account article HTML with near-100% visual restoration, so rich local/editor templates survive paste and official `draft/add` workflows.

The goal is simple: keep the approved article looking almost exactly the same in WeChat. The agent should change markup only when the original DOM is likely to break inside WeChat.

It is useful when:

- formatting disappears after sending HTML to the draft box
- the same HTML looks different in local preview, editor paste, and official `draft/add`
- WeChat exposes table cell borders
- heading lines wrap or indent strangely on mobile preview
- editor-export attributes make the final draft unstable
- hidden SEO blocks need to be removed while visible keyword lines are preserved

![Example screenshot](assets/example-screenshot.png)

## Quick Start

Ask your agent:

```text
Use $html-to-wechat-article to convert this HTML into a WeChat article for draft/add while preserving the approved visual template as close to 100% as possible.
```

The skill is agent-first. It teaches the agent how to inspect and rewrite the HTML directly, without requiring Python or any runtime.

## Field Notes

- Decide the target path first. Local browser preview, WeChat editor paste, and official `draft/add` are different renderers.
- If a raw approved template already survives the target path, keep it raw. Switch to cleaned HTML when mobile preview shows fake indentation, stretched Chinese text, exposed table borders, or missing styles.
- Body images and cover images are different WeChat API concepts. Body images should be uploaded to content image storage and replaced with the returned hosted `url`; cover thumbnails need a `thumb_media_id`.
- Publishing errors such as credentials, IP whitelist, proxy, SSH, or network failures are not HTML problems. Fix the publishing path before rewriting the article.
- Do not add `content_source_url`, source links, video links, or provenance footers unless the user asks for them.
- If the draft title is supplied as API metadata, avoid repeating the same H1 title inside the body unless the approved template visibly includes it.

## Install As A Codex Skill

Copy or clone this repository into your Codex skills directory:

```bash
git clone https://github.com/tonylawx/html-to-wechat-article.git ~/.codex/skills/html-to-wechat-article
```

Then ask Codex:

```text
Use $html-to-wechat-article to convert this HTML into a WeChat article for draft/add while preserving the approved visual template as close to 100% as possible.
```

## Optional Batch Script

For repeated local batch cleanup, the repository also includes a small optional script:

```bash
python3 scripts/restore_wechat_html.py examples/before.html -o examples/after.generated.html --report
```

Use `--keep-tables` when the article contains real data tables such as comparison tables or parameter grids:

```bash
python3 scripts/restore_wechat_html.py article.html -o article.wechat.html --keep-tables --report
```

The script is not required by the skill. It is local-only, does not call the WeChat API, does not upload images, and does not handle credentials.

## Included

- `SKILL.md`: agent instructions.
- `scripts/restore_wechat_html.py`: optional deterministic local cleaner.
- `examples/before.html`: unstable editor-style sample.
- `examples/after.html`: cleaned sample.
- `assets/example-screenshot.png`: screenshot of the example output.

## License

MIT
