# CLAUDE.md — web-skill repo rules

## Structure

Doc = router, package = engine — framework ported from Agent-Reach (don't reinvent it). The agent reads `web_skill/skill/` docs and runs the upstream CLIs; `web_skill/` is the engine: `probe.py` (`probe_command`), `channels/` (`Channel.check()` + ordered `backends` + `active_backend`), `doctor.py` (`check_all`/`format_report`), `cli.py` (install/doctor/skill). The deterministic "which backend is usable" decision lives in `check()`, not in the agent. Layout in README.md.

## Adding a channel — keep these in sync

A new tool means **all** of:
- `web_skill/channels/<name>.py` — `Channel` subclass: `name`, `description`, `backends` (ordered, `backends[0]` preferred), `tier`, `can_handle()`, `check()` (probe each candidate via `probe_command`, set `active_backend`, return first ok→warn). Register in `channels/__init__.py`. Multi-backend (e.g. primary CLI + OpenCLI fallback) = list both + an `_check_<backend>` each; copy the pattern in `xiaohongshu.py`.
- Install line(s) in `install()` in `web_skill/cli.py`.
- `web_skill/skill/tools/<name>.md` (router doc) + a row in `web_skill/skill/SKILL.md`.
- `INSTALL.md` only if a new first-run model download or manual step is introduced.
- Reusable scripts go in `web_skill/skill/scripts/`; reference them in docs as `${CLAUDE_SKILL_DIR}/scripts/<x>.py`. `tools/` stays pure docs.

## Skill frontmatter rule

`web_skill/skill/SKILL.md` frontmatter (`description`, `allowed-tools`) must accurately reflect what tools are actually available. Update it whenever a tool is added, removed, or its trigger phrases change. Never leave it describing tools that don't exist yet.

## Tests rule

One test file per script: `tests/test_<script>.py` for each `web_skill/skill/scripts/<script>.py`. Editing one script only re-runs its file. Tests use pytest, declared via the file's PEP 723 inline deps so `uv run tests/test_<script>.py` runs just that file; the whole suite is `uv run --with pytest --with requests pytest tests/`. Each file imports the script via `tests/_common.py`'s `load()`. Scripts with no importable pure functions (e.g. `stt.py` — logic runs at import) get no test file.
