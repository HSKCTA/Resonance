import express from "express";
import http from "http";
import { Server } from "socket.io";
import zmq from "zeromq";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    maxHttpBufferSize: 2e6,
    cors: { origin: "*" },
});

// Serve built assets in production
app.use(express.static(path.join(__dirname, "dist")));

// ZeroMQ endpoints — configurable for Docker (defaults for local dev)
const ZMQ_NODE_B = process.env.ZMQ_NODE_B || "tcp://127.0.0.1:5557";
const ZMQ_NODE_A = process.env.ZMQ_NODE_A || "tcp://127.0.0.1:5555";

// ZeroMQ Subscriber — connects to Node B inference output
// Node B publishes JSON: { timestamp, mse, rms, severity, alert }
let latestData = null;
let msgCount = 0;

async function runSubscriber() {
    const sock = new zmq.Subscriber();
    try {
        sock.connect(ZMQ_NODE_B);
        console.log(`[Server] ZMQ connected to Node B (${ZMQ_NODE_B})`);
        sock.subscribe("");

        for await (const [msg] of sock) {
            try {
                latestData = JSON.parse(msg.toString());
                msgCount++;
            } catch (err) {
                console.error("[Server] ZMQ parse error:", err.message);
            }
        }
    } catch (err) {
        console.error("[Server] ZMQ connection error:", err.message);
    }
}

// Throttled emit — 2 msg/sec to browser
setInterval(() => {
    if (latestData && io.engine.clientsCount > 0) {
        io.emit("node_b_data", latestData);
        if (msgCount % 20 < 2) {
            console.log(
                `[Relay] #${msgCount} → ${io.engine.clientsCount} client(s) | RMS=${latestData.rms?.toFixed(5)} | MSE=${latestData.mse?.toFixed(5)} | severity=${latestData.severity}`
            );
        }
    }
}, 500);

runSubscriber();

// ─── Second ZMQ Subscriber — Node A (port 5555) for high-frequency RMS ───
// rms_monitor.py subscribes here and gets ~100ms updates.
// We mirror that so the dashboard spectrogram matches rms_monitor.py.
async function runNodeASubscriber() {
    const sockA = new zmq.Subscriber();
    sockA.connect(ZMQ_NODE_A);
    sockA.subscribe("");

    for await (const msgs of sockA) {
        try {
            // Frame 0 is the JSON header
            const header = JSON.parse(msgs[0].toString());
            if (header.rms !== undefined) {
                io.emit("node_a_rms", {
                    rms: header.rms,
                    timestamp: header.timestamp_ms
                });
            }
        } catch (err) {
            console.error("[Server] Node A parse error:", err.message);
        }
    }
}

runNodeASubscriber();

io.on("connection", (socket) => {
    console.log("[Server] Browser connected:", socket.id);
    socket.on("disconnect", () => {
        console.log("[Server] Browser disconnected:", socket.id);
    });
});

const PORT = 3001;
server.listen(PORT, () => {
    console.log(`[Server] Resonance backend on http://localhost:${PORT}`);
});
