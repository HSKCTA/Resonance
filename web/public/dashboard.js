const socket = io();

// UI Elements
const mseValueEl = document.getElementById('mse-value');
const statusBadgeEl = document.getElementById('status-badge');
const statusTextEl = document.getElementById('status-text');
const alertAreaEl = document.querySelector('.alert-area');
const alertContentEl = document.getElementById('alert-content');

// --- Gauge Chart ---
const ctxGauge = document.getElementById('gaugeChart').getContext('2d');
const gaugeChart = new Chart(ctxGauge, {
    type: 'doughnut',
    data: {
        labels: ['MSE', 'Max'],
        datasets: [{
            data: [0, 100],
            backgroundColor: ['#10b981', '#1e293b'],
            borderWidth: 0,
            cutout: '85%',
            rotation: 225,
            circumference: 270,
            borderRadius: 10
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
});

// --- History Chart ---
const ctxHistory = document.getElementById('historyChart').getContext('2d');
const gradient = ctxHistory.createLinearGradient(0, 0, 0, 400);
gradient.addColorStop(0, 'rgba(59, 130, 246, 0.5)');
gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

const historyChart = new Chart(ctxHistory, {
    type: 'line',
    data: {
        labels: Array(50).fill(''),
        datasets: [{
            label: 'Reconstruction Error',
            data: Array(50).fill(null),
            borderColor: '#3b82f6',
            backgroundColor: gradient,
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointRadius: 0,
            pointHoverRadius: 5
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { display: false },
            y: {
                beginAtZero: true,
                max: 0.5,
                grid: { color: '#334155', tickLength: 0 },
                ticks: { color: '#94a3b8', font: { size: 10 } }
            }
        },
        plugins: { legend: { display: false } },
        interaction: { intersect: false, mode: 'index' }
    }
});

// --- Spectrogram ---
const specCanvas = document.getElementById('spectrogramCanvas');
const specCtx = specCanvas.getContext('2d');
// Internal resolution
specCanvas.width = 64;
specCanvas.height = 1024; // Full resolution for the larger view

// --- Socket Events ---
socket.on('connect', () => {
    statusTextEl.textContent = "ONLINE";
    statusTextEl.textContent = "ONLINE";
    statusBadgeEl.style.backgroundColor = "rgba(16, 185, 129, 0.2)";
    statusBadgeEl.style.color = "#10b981";
});

socket.on('disconnect', () => {
    statusTextEl.textContent = "OFFLINE";
    statusBadgeEl.style.backgroundColor = "rgba(239, 68, 68, 0.2)";
    statusBadgeEl.style.color = "#ef4444";
});

socket.on('node_b_data', (data) => {
    // 1. Update Gauge
    const normalizedScore = Math.min((data.mse / 0.25) * 100, 100);
    gaugeChart.data.datasets[0].data = [normalizedScore, 100 - normalizedScore];

    // Color Logic
    let color = '#10b981'; // Green
    if (data.severity === 'HIGH') color = '#ef4444';
    else if (data.severity === 'MEDIUM' || data.severity === 'LOW') color = '#f59e0b';

    gaugeChart.data.datasets[0].backgroundColor[0] = color;
    gaugeChart.update();

    // Update Value Text
    mseValueEl.textContent = data.mse.toFixed(4);
    mseValueEl.style.color = color;

    // 2. Update History
    const historyData = historyChart.data.datasets[0].data;
    historyData.push(data.mse);
    historyData.shift();
    historyChart.update('none');

    // 3. Alert Logic
    // 3. Alert Logic (Restored)
    if (data.severity !== 'NORMAL') {
        alertContentEl.innerHTML = `
            <div style="animation: pulse 1s infinite; font-size: 40px; color: ${color}; margin-bottom: 10px;">
                <ion-icon name="warning"></ion-icon>
            </div>
            <h3 style="margin: 0; color: white;">${data.alert || "Anomaly Detected"}</h3>
            <p style="margin: 5px 0 0 0; color: ${color}; font-weight: bold;">Severity: ${data.severity}</p>
        `;
        // Flash the card background
        alertAreaEl.style.background = `linear-gradient(135deg, ${color}20, transparent)`;

        // ALSO ADD TO AI CHAT
        const msg = data.alert || `Anomaly Detected (Severity: ${data.severity})`;
        const chatBox = document.getElementById('ai-chat-box');
        // Simple debounce: don't add if same as last message
        const lastMsg = chatBox.lastElementChild;
        if (!lastMsg || !lastMsg.textContent.includes(msg)) {
            addAiMessage(msg, 'alert');
            // Auto-open chat on high severity? Optional.
            // if (data.severity === 'HIGH') document.getElementById('ai-chat-window').classList.add('open');
        }

    } else {
        alertContentEl.innerHTML = `
            <ion-icon name="checkmark-circle-outline" style="font-size: 48px; color: #10b981; opacity: 0.5;"></ion-icon>
            <p style="margin-top: 10px; color: #94a3b8;">System Normal</p>
        `;
        alertAreaEl.style.background = "";
    }

    // 4. Spectrogram
    if (data.spectrogram) {
        renderSpectrogram(data.spectrogram);
    }
});

// AI Chat Helpers
function addAiMessage(text, type = 'system') {
    const chatBox = document.getElementById('ai-chat-box');
    if (!chatBox) return; // Guard

    const msgDiv = document.createElement('div');
    msgDiv.className = `ai-message ${type}`;

    let icon = type === 'alert' ? 'warning' : 'sparkles';
    if (type === 'system') icon = 'information-circle';

    msgDiv.innerHTML = `
        <ion-icon name="${icon}"></ion-icon>
        <div>${text}</div>
    `;

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Toggle AI Chat Window
window.toggleAiChat = function () {
    const chatWindow = document.getElementById('ai-chat-window');
    chatWindow.classList.toggle('open');
}

// Toggle Drawer Menu
window.toggleMenu = function () {
    const drawer = document.getElementById('drawer-menu');
    drawer.classList.toggle('open');
}

// Ensure charts resize when layout changes
window.addEventListener('resize', () => {
    gaugeChart.resize();
    historyChart.resize();
});

// End of socket.on is handled above


function renderSpectrogram(base64Data) {
    const binaryString = atob(base64Data);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) { bytes[i] = binaryString.charCodeAt(i); }
    const floats = new Float32Array(bytes.buffer);

    // Spectrogram Dimensions
    const width = 64;
    const height = 1024; // Original Data Height

    // We want to fit this into our 64x256 canvas
    // So we will skip rows/downsample or just render full and let CSS scale?
    // CSS scaling is bad for performance if image is huge.
    // Let's render 1:1 but only top 256 freq bins (Low frequency usually most important)
    // OR we can stride.

    const imgData = specCtx.createImageData(width, specCanvas.height);

    // Simple render (taking first 256 frequency bins for visibility)
    for (let y = 0; y < specCanvas.height; y++) {
        for (let x = 0; x < width; x++) {
            // Map to float array index. Floats is flat 1024x64. 
            // Logic: Data[time][freq] ? Or Data[freq][time]?
            // Python: (1, 1024, 64) -> 1024 freq, 64 time.
            // Flat array: freq0_t0, freq0_t1... freq1_t0...

            // We want Time on X, Freq on Y.
            // Source index: (y * 4) * 64 + x   (Downsampling 1024->256 by taking every 4th bin?)
            const srcIdx = (y * 4) * 64 + x;

            let val = 0;
            if (srcIdx < floats.length) val = floats[srcIdx];

            const intensity = Math.min(Math.max((val + 0.5) * 1.5, 0), 1) * 255;
            const pxIdx = (y * width + x) * 4;

            // Inferno Map
            imgData.data[pxIdx + 0] = intensity;     // R
            imgData.data[pxIdx + 1] = intensity * 0.2; // G
            imgData.data[pxIdx + 2] = intensity * 0.05; // B
            imgData.data[pxIdx + 3] = 255;
        }
    }
    specCtx.putImageData(imgData, 0, 0);
}
