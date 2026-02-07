from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("RISK_GOVERNOR_HOST", "127.0.0.1")
    port = int(os.getenv("RISK_GOVERNOR_PORT", "8090"))
    uvicorn.run("risk_governor.api:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()

