# -*- coding: utf-8 -*-
"""Channel base class (ported from Agent-Reach's channels/base.py).

Each channel = one platform. It provides:
  - can_handle(url) → does this URL belong to this platform?
  - check(config)   → is an upstream backend installed/usable? sets active_backend.

Backend routing: `backends` is an ORDERED candidate list (backends[0] preferred,
rest are fallbacks). "Switching backends" = reordering this list. check() probes
candidates and sets self.active_backend to the one actually serving now.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


class Channel(ABC):
    name: str = ""
    description: str = ""
    backends: List[str] = []          # ordered candidates — backends[0] = preferred
    tier: int = 0                     # 0=zero-config, 1=needs login/key, 2=needs heavy setup

    active_backend: Optional[str] = None  # set by check(); None = unavailable

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        ...

    def ordered_backends(self, config=None) -> List[str]:
        """Candidates in probe order, honoring a `<name>_backend` override in config."""
        candidates = list(self.backends)
        override = config.get(f"{self.name}_backend") if config else None
        if override:
            for i, b in enumerate(candidates):
                if b == override or b.startswith(override):
                    candidates.insert(0, candidates.pop(i))
                    break
        return candidates

    def check(self, config=None) -> Tuple[str, str]:
        """Return (status, message); status ∈ ok|warn|off|error. Must set active_backend."""
        self.active_backend = self.backends[0] if self.backends else "built-in"
        return "ok", ", ".join(self.backends) if self.backends else "built-in"
