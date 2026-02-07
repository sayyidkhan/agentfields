#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# MagiStock — Start All Agents
#
# Starts the Agentfield control plane and all 5 MagiStock agents.
# Each agent runs as a separate process (microservices architecture).
#
# Usage:
#   chmod +x scripts/start_all.sh
#   ./scripts/start_all.sh
#
# To stop all agents:
#   ./scripts/start_all.sh stop
# ──────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_DIR="$PROJECT_DIR/.pids"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─── Stop all agents ────────────────────────────────────────────────────────
stop_all() {
    echo -e "${YELLOW}Stopping all MagiStock agents...${NC}"
    if [ -d "$PID_DIR" ]; then
        for pidfile in "$PID_DIR"/*.pid; do
            if [ -f "$pidfile" ]; then
                pid=$(cat "$pidfile")
                name=$(basename "$pidfile" .pid)
                if kill -0 "$pid" 2>/dev/null; then
                    kill "$pid"
                    echo -e "  ${RED}Stopped${NC} $name (PID: $pid)"
                fi
                rm -f "$pidfile"
            fi
        done
        rmdir "$PID_DIR" 2>/dev/null || true
    fi
    echo -e "${GREEN}All agents stopped.${NC}"
    exit 0
}

if [ "${1:-}" = "stop" ]; then
    stop_all
fi

# ─── Pre-flight checks ──────────────────────────────────────────────────────
echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🔮 MagiStock — Multi-Agent System       ║${NC}"
echo -e "${BLUE}║     Built on AgentField.ai                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Check for .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Copy the example:${NC}"
    echo "    cp .env.example .env"
    echo "    Then set your API key."
    exit 1
fi

# Check Agentfield CLI
if ! command -v af &> /dev/null; then
    echo -e "${RED}❌ Agentfield CLI not found. Install it:${NC}"
    echo "    curl -sSf https://agentfield.ai/get | sh"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found.${NC}"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)

# Create PID directory
mkdir -p "$PID_DIR"

# ─── Start Agentfield Control Plane ─────────────────────────────────────────
echo -e "${GREEN}1/6${NC} Starting Agentfield Control Plane..."
af server &
AF_PID=$!
echo $AF_PID > "$PID_DIR/agentfield-server.pid"
echo -e "     ${GREEN}✓${NC} Control Plane started (PID: $AF_PID)"
sleep 3  # Wait for control plane to be ready

# ─── Start Strategy Agents ──────────────────────────────────────────────────
echo -e "${GREEN}2/6${NC} Starting 🔥 Fire Agent (momentum)..."
cd "$PROJECT_DIR/fire_agent" && $PYTHON main.py &
echo $! > "$PID_DIR/fire-agent.pid"
echo -e "     ${GREEN}✓${NC} Fire Agent started"

echo -e "${GREEN}3/6${NC} Starting 💧 Water Agent (conservative)..."
cd "$PROJECT_DIR/water_agent" && $PYTHON main.py &
echo $! > "$PID_DIR/water-agent.pid"
echo -e "     ${GREEN}✓${NC} Water Agent started"

echo -e "${GREEN}4/6${NC} Starting 🌱 Grass Agent (adaptive)..."
cd "$PROJECT_DIR/grass_agent" && $PYTHON main.py &
echo $! > "$PID_DIR/grass-agent.pid"
echo -e "     ${GREEN}✓${NC} Grass Agent started"

# ─── Start Judge Agent ───────────────────────────────────────────────────────
echo -e "${GREEN}5/6${NC} Starting ⚖️  Judge Agent..."
cd "$PROJECT_DIR/judge_agent" && $PYTHON main.py &
echo $! > "$PID_DIR/judge-agent.pid"
echo -e "     ${GREEN}✓${NC} Judge Agent started"

# ─── Start Orchestrator ─────────────────────────────────────────────────────
echo -e "${GREEN}6/6${NC} Starting 📊 Orchestrator..."
cd "$PROJECT_DIR/orchestrator" && $PYTHON main.py &
echo $! > "$PID_DIR/orchestrator.pid"
echo -e "     ${GREEN}✓${NC} Orchestrator started"

# ─── Ready ───────────────────────────────────────────────────────────────────
sleep 2
echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ All MagiStock agents are running!${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${BLUE}Test with:${NC}"
echo ""
echo '  curl -X POST http://localhost:8080/api/v1/execute/magistock.run_analysis \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{'
echo '      "input": {'
echo '        "ticker": "SPY",'
echo '        "period_days": 252,'
echo '        "risk_tolerance": "medium",'
echo '        "time_horizon": "long",'
echo '        "drawdown_sensitivity": "medium"'
echo '      }'
echo '    }'"'"''
echo ""
echo -e "  ${YELLOW}Stop all:${NC} ./scripts/start_all.sh stop"
echo ""

# Wait for all background processes
wait
