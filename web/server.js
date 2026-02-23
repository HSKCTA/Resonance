const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const zmq = require('zeromq');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Serve static files from 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// ZeroMQ Subscriber
async function runSubscriber() {
    const sock = new zmq.Subscriber();

    try {
        sock.connect("tcp://127.0.0.1:5557");
        console.log("Node.js Server connected to Node B (ZMQ:5557)");
        sock.subscribe(""); // Subscribe to all topics

        for await (const [msg] of sock) {
            try {
                const data = JSON.parse(msg.toString());
                // Broadcast to all connected web clients
                io.emit('node_b_data', data);
            } catch (err) {
                console.error("Error parsing ZMQ message:", err);
            }
        }
    } catch (err) {
        console.error("ZMQ Connection Error:", err);
    }
}

runSubscriber();

io.on('connection', (socket) => {
    console.log('Web Client Connected:', socket.id);
    socket.on('disconnect', () => {
        console.log('Web Client Disconnected:', socket.id);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Node.js Web Server running on http://localhost:${PORT}`);
});
