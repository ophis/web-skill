"""web-skill — on-device tools for AI agents, packaged as a Claude Code skill.

The agent is the router: it reads skill/SKILL.md, picks a tool doc, and runs the
upstream CLIs. This package is the *engine* — install, status (doctor), and
skill registration. Add a channel = drop one file in channels/ + one doc in
skill/tools/.
"""

__version__ = "0.1.0"
