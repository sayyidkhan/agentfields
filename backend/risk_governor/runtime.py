from __future__ import annotations

import inspect
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class ExecutionBudget:
    max_steps: int = 8
    max_reasoner_calls: int = 12
    max_skill_calls: int = 24

    steps_used: int = 0
    reasoner_calls_used: int = 0
    skill_calls_used: int = 0

    def bump_step(self) -> None:
        self.steps_used += 1
        if self.steps_used > self.max_steps:
            raise BudgetExceeded(f"max_steps exceeded: {self.steps_used}/{self.max_steps}")

    def bump_reasoner(self) -> None:
        self.reasoner_calls_used += 1
        if self.reasoner_calls_used > self.max_reasoner_calls:
            raise BudgetExceeded(
                f"max_reasoner_calls exceeded: {self.reasoner_calls_used}/{self.max_reasoner_calls}"
            )

    def bump_skill(self) -> None:
        self.skill_calls_used += 1
        if self.skill_calls_used > self.max_skill_calls:
            raise BudgetExceeded(
                f"max_skill_calls exceeded: {self.skill_calls_used}/{self.max_skill_calls}"
            )


@dataclass
class RegisteredFn:
    name: str
    fn: Callable[..., Any]
    kind: str  # "reasoner" | "skill"
    tags: tuple[str, ...] = ()


@dataclass
class AgentFieldLiteApp:
    """
    Minimal AgentField-like runtime.

    - Discovery: call-by-name routing (reasoners/skills are registered)
    - Guided autonomy: explicit budget tracking for predictability
    """

    node_id: str
    _reasoners: dict[str, RegisteredFn] = field(default_factory=dict)
    _skills: dict[str, RegisteredFn] = field(default_factory=dict)

    def reasoner(self, name: Optional[str] = None, tags: Optional[list[str]] = None):
        def decorator(fn: Callable[..., Any]):
            reg_name = name or fn.__name__
            fq = f"{self.node_id}.reasoners.{reg_name}"
            self._reasoners[fq] = RegisteredFn(
                name=fq, fn=fn, kind="reasoner", tags=tuple(tags or [])
            )
            return fn

        return decorator

    def skill(self, name: Optional[str] = None, tags: Optional[list[str]] = None):
        def decorator(fn: Callable[..., Any]):
            reg_name = name or fn.__name__
            fq = f"{self.node_id}.skills.{reg_name}"
            self._skills[fq] = RegisteredFn(name=fq, fn=fn, kind="skill", tags=tuple(tags or []))
            return fn

        return decorator

    def list_reasoners(self) -> list[str]:
        return sorted(self._reasoners.keys())

    def list_skills(self) -> list[str]:
        return sorted(self._skills.keys())

    async def call(
        self,
        name: str,
        *,
        budget: Optional[ExecutionBudget] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Discovery call by name.

        Supports short names:
        - "market_regime_classifier" -> "{node_id}.reasoners.market_regime_classifier"
        - "fetch_market_data" -> "{node_id}.skills.fetch_market_data"
        """

        resolved = self._resolve_name(name)

        if resolved in self._reasoners:
            if budget:
                budget.bump_reasoner()
            target = self._reasoners[resolved].fn
        elif resolved in self._skills:
            if budget:
                budget.bump_skill()
            target = self._skills[resolved].fn
        else:
            raise KeyError(f"Unknown callable: {name} (resolved: {resolved})")

        if inspect.iscoroutinefunction(target):
            return await target(**kwargs)
        return target(**kwargs)

    def _resolve_name(self, name: str) -> str:
        if name.startswith(f"{self.node_id}.reasoners.") or name.startswith(
            f"{self.node_id}.skills."
        ):
            return name
        if name in self._reasoners:
            return name
        if name in self._skills:
            return name
        # heuristic: prefer reasoner if exists
        r = f"{self.node_id}.reasoners.{name}"
        s = f"{self.node_id}.skills.{name}"
        if r in self._reasoners:
            return r
        if s in self._skills:
            return s
        return name


def now_ms() -> int:
    return int(time.time() * 1000)

