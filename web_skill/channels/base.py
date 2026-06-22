"""Channel = one tool the skill exposes. Subclass, set the fields, implement status().

To add a channel: create channels/<name>.py with a Channel subclass, add it to
CHANNELS in channels/__init__.py, and write skill/tools/<doc>.
"""


class Channel:
    name = ""          # routing id, matches the skill doc's topic
    doc = ""           # filename under skill/tools/
    brew_deps = []     # Homebrew formulae `install` should ensure
    uv_tools = []      # `uv tool install <pkg>` CLIs `install` should ensure

    def status(self):
        """Return (level, message). level ∈ ok | warn | error | off."""
        raise NotImplementedError
