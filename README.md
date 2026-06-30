# WeChat HTML Restore Skill

A Codex skill for cleaning and restoring WeChat Official Account article HTML so rich local/editor templates survive paste and official `draft/add` workflows.

It is useful when:

- formatting disappears after sending HTML to the draft box
- WeChat exposes table cell borders
- heading lines wrap or indent strangely on mobile preview
- editor-export attributes make the final draft unstable
- hidden SEO blocks need to be removed while visible keyword lines are preserved

![Example screenshot](assets/example-screenshot.png)

## Quick Start

Ask your agent:

```text
Use $wechat-html-restore to clean this WeChat article HTML for draft/add.
```

The skill is agent-first. It teaches the agent how to inspect and rewrite the HTML directly, without requiring Python or any runtime.

## Install As A Codex Skill

Copy or clone this repository into your Codex skills directory:

```bash
git clone https://github.com/tonylawx/wechat-html-restore-skill.git ~/.codex/skills/wechat-html-restore
```

Then ask Codex:

```text
Use $wechat-html-restore to clean this WeChat article HTML for draft/add.
```

## Optional Batch Script

For repeated local batch cleanup, the repository also includes a small optional script:

```bash
python3 scripts/restore_wechat_html.py examples/before.html -o examples/after.generated.html --report
```

The script is not required by the skill. It is local-only, does not call the WeChat API, and does not handle credentials.

## Included

- `SKILL.md`: agent instructions.
- `scripts/restore_wechat_html.py`: optional deterministic local cleaner.
- `examples/before.html`: unstable editor-style sample.
- `examples/after.html`: cleaned sample.
- `assets/example-screenshot.png`: screenshot of the example output.

## License

MIT
