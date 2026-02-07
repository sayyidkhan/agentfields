"""
Autonomous Portfolio Risk Governor (AI backend runtime layer).

This package implements AgentField-style primitives:
- Reasoners: typed, auditable decision functions (Pydantic outputs)
- Skills: deterministic, testable computation + side-effect boundaries
- Memory: shared KV + vector memory (sqlite-backed)
- Discovery: call-by-name routing via registries (no hardcoded DAG)
"""

