#!/usr/bin/env python3
"""
rms_monitor.py — Resonance Hardware Verification Tool
=====================================================

Real-time RMS plotter for validating the vibration sensor + C++ broadcaster
pipeline.  Subscribes to the ZeroMQ PUB socket, computes RMS from raw
float32 spectrogram data, and plots a live scrolling graph.

Usage
-----
    python rms_monitor.py                     # default endpoint
    python rms_monitor.py tcp://192.168.1.5:5555   # custom endpoint

Expected ZMQ multipart message (sent by broadcaster.cpp):
    Frame 0  – JSON header  {"timestamp_ms": …, "bins": …, "frames": …, "dtype": "float32"}
    Frame 1  – raw float32 tensor bytes  (bins × frames floats)

What to look for:
    • Tap sensor   → sharp RMS spike
    • Run motor    → sustained elevated RMS
    • Idle         → RMS ≈ 0
"""

import sys
import json
import struct
import math
import time
from collections import deque

import zmq
import matplotlib
matplotlib.use("TkAgg")  # lightweight backend, no web server
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ─── Configuration ───────────────────────────────────────────────────────────

DEFAULT_ENDPOINT = "tcp://127.0.0.1:5555"
RING_SIZE        = 300        # number of samples kept in the scrolling window
POLL_TIMEOUT_MS  = 10         # zmq.poll timeout  → <50 ms refresh target
ANIM_INTERVAL_MS = 30         # matplotlib timer  → ~33 fps redraw

# ─── ZMQ Setup ───────────────────────────────────────────────────────────────
# We use a SUB socket that subscribes to ALL messages (empty topic filter).
# zmq.CONFLATE = 1 tells ZMQ to keep only the *latest* message in the receive
# buffer, which prevents stale-data buildup when the plot can't keep up.

def create_subscriber(endpoint: str) -> zmq.Socket:
    """Create and connect a ZMQ SUB socket to the broadcaster."""
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, b"")       # subscribe to everything
    # NOTE: zmq.CONFLATE cannot be used here — it is incompatible with
    # multipart messages (causes assertion `!_more` crash).  Instead we
    # keep RCVHWM small and drain all queued messages in poll_and_update(),
    # always using only the latest value.
    sock.setsockopt(zmq.RCVHWM, 4)            # small receive high-water mark
    sock.connect(endpoint)
    print(f"[rms_monitor] SUB connected → {endpoint}")
    return sock

# ─── RMS Computation ─────────────────────────────────────────────────────────
# The header from broadcaster.cpp contains bins, frames, dtype but NOT rms.
# We compute RMS ourselves from the raw float32 tensor:
#     RMS = sqrt( (1/N) * Σ x² )

def compute_rms(raw_bytes: bytes, n_floats: int) -> float:
    """Compute RMS from raw little-endian float32 tensor bytes."""
    if n_floats == 0:
        return 0.0
    # Unpack all floats at once (little-endian float32 = '<f')
    fmt = f"<{n_floats}f"
    values = struct.unpack(fmt, raw_bytes[:n_floats * 4])
    sum_sq = sum(v * v for v in values)
    return math.sqrt(sum_sq / n_floats)

# ─── Ring Buffers ─────────────────────────────────────────────────────────────

rms_buf  = deque([0.0] * RING_SIZE, maxlen=RING_SIZE)   # y-axis: RMS values
time_buf = deque([0.0] * RING_SIZE, maxlen=RING_SIZE)   # x-axis: elapsed sec

t_start     = time.monotonic()
msg_count   = 0
last_rms    = 0.0

# ─── Receive + Update ────────────────────────────────────────────────────────

def poll_and_update(sock: zmq.Socket) -> None:
    """Non-blocking poll: drain all available messages, keep latest RMS."""
    global msg_count, last_rms

    while sock.poll(POLL_TIMEOUT_MS, zmq.POLLIN):
        try:
            frames = sock.recv_multipart(zmq.NOBLOCK)
        except zmq.Again:
            break

        if len(frames) < 2:
            continue   # malformed message, skip

        # ── Parse JSON header (Frame 0) ──
        try:
            header = json.loads(frames[0])
        except json.JSONDecodeError:
            continue

        bins   = header.get("bins", 0)
        n_frames = header.get("frames", 0)
        n_floats = bins * n_frames

        # ── If header already contains an rms field, use it directly ──
        if "rms" in header:
            rms = float(header["rms"])
        else:
            # Compute from raw tensor (Frame 1)
            rms = compute_rms(frames[1], n_floats)

        last_rms = rms
        msg_count += 1

        elapsed = time.monotonic() - t_start
        rms_buf.append(rms)
        time_buf.append(elapsed)

# ─── Plotting ────────────────────────────────────────────────────────────────

def build_figure():
    """Create the matplotlib figure and axes."""
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    (line,) = ax.plot([], [], color="#89b4fa", linewidth=1.4)

    ax.set_title("Resonance — Live RMS Monitor", color="#cdd6f4", fontsize=14,
                 fontweight="bold", pad=10)
    ax.set_xlabel("Time (s)", color="#a6adc8")
    ax.set_ylabel("RMS", color="#a6adc8")
    ax.tick_params(colors="#6c7086")
    for spine in ax.spines.values():
        spine.set_color("#313244")

    ax.grid(True, color="#313244", linewidth=0.5, alpha=0.6)

    # Status text (top-left corner)
    status_text = ax.text(
        0.01, 0.95, "", transform=ax.transAxes,
        fontsize=9, color="#a6adc8", verticalalignment="top",
        fontfamily="monospace",
    )

    return fig, ax, line, status_text


def make_update_fn(sock, ax, line, status_text):
    """Return the animation callback bound to the socket + plot elements."""

    def update(_frame_number):
        poll_and_update(sock)

        xs = list(time_buf)
        ys = list(rms_buf)
        line.set_data(xs, ys)

        if xs[-1] > 0:
            ax.set_xlim(max(0, xs[-1] - 15), xs[-1] + 0.5)

        if ys:
            y_max = max(ys) * 1.25 or 0.01
            ax.set_ylim(0, y_max)

        status_text.set_text(
            f"msgs: {msg_count:>6}   rms: {last_rms:.6f}"
        )
        return (line, status_text)

    return update

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    endpoint = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENDPOINT
    print(f"[rms_monitor] Resonance Hardware Verification Tool")
    print(f"[rms_monitor] Ring buffer : {RING_SIZE} samples")
    print(f"[rms_monitor] Connecting  : {endpoint}")
    print(f"[rms_monitor] Ctrl+C to quit.\n")

    sock = create_subscriber(endpoint)
    fig, ax, line, status_text = build_figure()

    _anim = animation.FuncAnimation(
        fig,
        make_update_fn(sock, ax, line, status_text),
        interval=ANIM_INTERVAL_MS,
        blit=False,       # full redraw needed for dynamic xlim/ylim
        cache_frame_data=False,
    )

    try:
        plt.tight_layout()
        plt.show()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print("\n[rms_monitor] Shut down.")


if __name__ == "__main__":
    main()
