#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Resonance — Start All Services
# ─────────────────────────────────────────────────────────────
# Starts: Node A, Node B (inference), RMS Monitor, Web Server, Dashboard
# Usage:  ./runall.sh          (start everything)
#         ./runall.sh stop     (kill all Resonance processes)
# ─────────────────────────────────────────────────────────────

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/.venv/bin/activate"
LOG_DIR="$ROOT/.logs"
mkdir -p "$LOG_DIR"

# Local LLM endpoint (OpenAI-compatible: Ollama, llama.cpp, vLLM, LM Studio)
export LLM_URL="${LLM_URL:-http://localhost:11434/v1/chat/completions}"
export LLM_MODEL="${LLM_MODEL:-mistral:7b}"
# export LLM_API_KEY=""  # uncomment if your server needs auth

# ZMQ — override for local dev (config.py defaults to host.docker.internal for Docker)
export ZMQ_ENDPOINT="${ZMQ_ENDPOINT:-tcp://localhost:5555}"

# ─── Colors ──────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# ─── Stop All ────────────────────────────────────────────────
stop_all() {
    echo -e "${YELLOW}Stopping all Resonance processes...${NC}"
    pkill -f "resonance_node_a" 2>/dev/null || true
    pkill -f "inference/main.py" 2>/dev/null || true
    pkill -f "rms_monitor.py"   2>/dev/null || true
    pkill -f "node server.js"   2>/dev/null || true
    pkill -f "vite"             2>/dev/null || true
    # Free ports (separate from process launch to avoid killing new processes)
    fuser -k 5555/tcp 2>/dev/null || true
    fuser -k 5557/tcp 2>/dev/null || true
    fuser -k 3001/tcp 2>/dev/null || true
    fuser -k 5173/tcp 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}All processes stopped.${NC}"
}

if [[ "$1" == "stop" ]]; then
    stop_all
    exit 0
fi

# ─── Stop any leftover processes first ───────────────────────
stop_all

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       Project Resonance — Starting All      ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ─── 1. Node A (C++ — The Ear) ──────────────────────────────
echo -e "${GREEN}[1/5]${NC} Starting Node A (The Ear)..."
"$ROOT/build/resonance_node_a" > "$LOG_DIR/node_a.log" 2>&1 &
PID_NODE_A=$!
sleep 2

# Check if Node A started successfully
if kill -0 $PID_NODE_A 2>/dev/null; then
    echo -e "       ${GREEN}✓${NC} Node A running (PID $PID_NODE_A)"
    # Show which device was matched
    grep -o '\[Ear\].*' "$LOG_DIR/node_a.log" 2>/dev/null | head -2 | while read line; do
        echo -e "       ${CYAN}$line${NC}"
    done
else
    echo -e "       ${RED}✗ Node A failed to start. Check $LOG_DIR/node_a.log${NC}"
    exit 1
fi

# ─── 2. Node B (Python — Inference) ─────────────────────────
echo -e "${GREEN}[2/5]${NC} Starting Node B (Inference + LLM)..."
(set +e; source "$VENV" && cd "$ROOT/python/inference" && python -u main.py) > "$LOG_DIR/node_b.log" 2>&1 &
PID_NODE_B=$!
sleep 3

if kill -0 $PID_NODE_B 2>/dev/null; then
    echo -e "       ${GREEN}✓${NC} Node B running (PID $PID_NODE_B)"
    if grep -q "Loading model" "$LOG_DIR/node_b.log" 2>/dev/null; then
        echo -e "       ${CYAN}ONNX model loaded${NC}"
    fi
else
    echo -e "       ${RED}✗ Node B failed. Check $LOG_DIR/node_b.log${NC}"
fi

# ─── 3. RMS Monitor (Python — matplotlib) ───────────────────
echo -e "${GREEN}[3/5]${NC} Starting RMS Monitor..."
(source "$VENV" && python "$ROOT/python/utils/rms_monitor.py") > "$LOG_DIR/rms_monitor.log" 2>&1 &
PID_RMS=$!
sleep 1

if kill -0 $PID_RMS 2>/dev/null; then
    echo -e "       ${GREEN}✓${NC} RMS Monitor running (PID $PID_RMS)"
else
    echo -e "       ${YELLOW}⚠ RMS Monitor may need a display (X11/Wayland)${NC}"
fi

# ─── 4. Web Backend Server (Node.js) ────────────────────────
echo -e "${GREEN}[4/5]${NC} Starting Web Server..."
(cd "$ROOT/web" && node server.js) > "$LOG_DIR/server.log" 2>&1 &
PID_SERVER=$!
sleep 1

if kill -0 $PID_SERVER 2>/dev/null; then
    echo -e "       ${GREEN}✓${NC} Web Server running on http://localhost:3001 (PID $PID_SERVER)"
else
    echo -e "       ${RED}✗ Server failed. Check $LOG_DIR/server.log${NC}"
fi

# ─── 5. Vite Dashboard ──────────────────────────────────────
echo -e "${GREEN}[5/5]${NC} Starting Dashboard (Vite)..."
(cd "$ROOT/web" && npx vite --port 5173) > "$LOG_DIR/vite.log" 2>&1 &
PID_VITE=$!
sleep 2

if kill -0 $PID_VITE 2>/dev/null; then
    echo -e "       ${GREEN}✓${NC} Dashboard running on http://localhost:5173 (PID $PID_VITE)"
else
    echo -e "       ${RED}✗ Vite failed. Check $LOG_DIR/vite.log${NC}"
fi

# ─── Summary ────────────────────────────────────────────────
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN} All services started!${NC}"
echo ""
echo -e "  Dashboard:    ${CYAN}http://localhost:5173/${NC}"
echo -e "  RMS Monitor:  ${CYAN}matplotlib window${NC}"
echo -e "  Logs:         ${CYAN}$LOG_DIR/${NC}"
echo ""
echo -e "  Stop all:     ${YELLOW}./runall.sh stop${NC}"
echo -e "  Or press:     ${YELLOW}Ctrl+C${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"

# ─── Wait & cleanup on Ctrl+C ───────────────────────────────
cleanup() {
    echo ""
    stop_all
    exit 0
}
trap cleanup SIGINT SIGTERM

# Keep script alive so Ctrl+C can stop everything
wait
