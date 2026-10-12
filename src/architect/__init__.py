"""The ARCHITECT vendor-neutral AI/LLM architecture decision package.

Re-exports the small public surface the Streamlit UI (`app.py`) and tests
depend on: the `ArchitectureCase` input model, the `recommend()` decision
function and its `Recommendation`/`DecisionPlan`/`OptionScore` outputs.
"""

from .engine import recommend
from .models import ArchitectureCase, DecisionPlan, OptionScore, Recommendation

__all__ = ["ArchitectureCase", "DecisionPlan", "OptionScore", "Recommendation", "recommend"]
