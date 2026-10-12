"""Optional provider boundary for future model-assisted features.

The ARQUITETO decision engine does not depend on this module.  It exists so any
future reviewer/copilot can be implemented without coupling the framework to a
specific model vendor.
"""

from typing import Protocol


class ModelAdapter(Protocol):
    """Minimal provider-neutral contract for an optional model runtime."""

    def generate(self, system: str, user: str) -> str:
        """Return a text response for the supplied system/user input."""
        ...
