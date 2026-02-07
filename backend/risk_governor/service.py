from __future__ import annotations

import os
import sys
from pathlib import Path

from .db import SqliteDB
from .engine import RiskGovernorEngine
from .runtime import AgentFieldLiteApp


def _ensure_backend_on_path() -> None:
    # Ensure `shared` imports work when running as a service.
    backend_dir = Path(__file__).resolve().parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))


def build_engine() -> RiskGovernorEngine:
    _ensure_backend_on_path()

    db_path = os.getenv(
        "RISK_GOVERNOR_DB",
        str(Path(__file__).resolve().parent / "data" / "risk_governor.sqlite"),
    )

    SqliteDB(Path(db_path)).migrate()

    app = AgentFieldLiteApp(node_id="risk-governor")

    # Register deterministic skills + typed reasoners
    from . import skills as skills_mod
    from . import reasoners as reasoners_mod
    from . import persistence_skills as persistence_mod

    skills_mod.register(app)
    persistence_mod.register(app)
    reasoners_mod.register(app)

    return RiskGovernorEngine(app=app, db_path=db_path)

