# CLAUDE.md — web-skill repo rules

## Sync rule

`scripts/install.sh` and `INSTALL.md` must be kept in sync with the actual skill structure at all times:

- Adding a new tool under `skill/tools/`? Update the install.sh system-deps section if the tool needs new CLI tools, and update INSTALL.md's model-download list if it downloads new models on first use.
- Removing a dependency? Remove it from install.sh and INSTALL.md.
- Changing the `skill/` layout? Verify install.sh still copies correctly and INSTALL.md's verify step still works.

Never leave install.sh or INSTALL.md stale after a structural change.

## Skill frontmatter rule

`skill/SKILL.md` frontmatter (`description`, `allowed-tools`) must accurately reflect what tools are actually available. Update it whenever a tool is added, removed, or its trigger phrases change. Never leave it describing tools that don't exist yet.

## Tests rule

One test file per tool: `tests/test_<tool>.py` (e.g. `tests/test_video_transcript.py`). Adding a tool adds its own file — don't fold tests into an existing tool's file, so editing one tool only re-runs that tool's tests. Each file is `uv run`-able standalone and uses plain asserts (no framework).
