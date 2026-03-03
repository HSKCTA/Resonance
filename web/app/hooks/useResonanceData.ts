import { useState, useEffect, useRef, useCallback } from "react";
import { io, Socket } from "socket.io-client";

interface NodeBData {
    timestamp: number;
    mse: number;
    rms: number;
    severity: "NORMAL" | "LOW" | "MEDIUM" | "HIGH";
    alert: string | null;
}

interface TrendPoint {
    time: string;
    score: number;
}

interface RmsPoint {
    time: string;
    rms: number;
}

interface ResonanceState {
    connected: boolean;
    mse: number;
    rms: number;
    severity: "NORMAL" | "LOW" | "MEDIUM" | "HIGH";
    status: "healthy" | "warning" | "critical";
    alert: string | null;
    trendData: TrendPoint[];
    rmsHistory: RmsPoint[];
    msgCount: number;
}

const TREND_SIZE = 30;
const RMS_RING_SIZE = 300;  // matches rms_monitor.py

function severityToStatus(
    severity: string,
    mse: number
): "healthy" | "warning" | "critical" {
    if (severity === "HIGH") return "critical";
    if (severity === "MEDIUM" || severity === "LOW" || mse > 0.1) return "warning";
    return "healthy";
}

export function useResonanceData(): ResonanceState {
    const startTimeRef = useRef<number>(Date.now());
    const [connected, setConnected] = useState(false);
    const [mse, setMse] = useState(0);
    const [rms, setRms] = useState(0);
    const [severity, setSeverity] = useState<"NORMAL" | "LOW" | "MEDIUM" | "HIGH">("NORMAL");
    const [alert, setAlert] = useState<string | null>(null);
    const [trendData, setTrendData] = useState<TrendPoint[]>([]);
    const [rmsHistory, setRmsHistory] = useState<RmsPoint[]>([]);
    const [msgCount, setMsgCount] = useState(0);
    const socketRef = useRef<Socket | null>(null);

    // node_b_data: anomaly detection only — mse, severity, alert, trendData
    const handleData = useCallback((data: NodeBData) => {
        setMse(data.mse);
        setSeverity(data.severity);
        setAlert(data.alert);

        const now = new Date();
        const timeStr = `${now.getHours().toString().padStart(2, "0")}:` +
            `${now.getMinutes().toString().padStart(2, "0")}:` +
            `${now.getSeconds().toString().padStart(2, "0")}`;

        setTrendData((prev) => {
            const next = [...prev, { time: timeStr, score: data.mse }];
            if (next.length > TREND_SIZE) next.shift();
            return next;
        });
    }, []);

    useEffect(() => {
        const socket = io({ transports: ["websocket"] });
        socketRef.current = socket;

        socket.on("connect", () => setConnected(true));
        socket.on("disconnect", () => setConnected(false));
        socket.on("node_b_data", handleData);

        // node_a_rms: high-frequency RMS only — rms, rmsHistory, msgCount
        // elapsed seconds matches rms_monitor.py x-axis exactly
        socket.on("node_a_rms", (data: { rms: number; timestamp: number }) => {
            const elapsed = ((Date.now() - startTimeRef.current) / 1000).toFixed(1);

            setRms(data.rms);
            setMsgCount((c) => c + 1);
            setRmsHistory((prev) => {
                const next = [...prev, { time: elapsed, rms: data.rms }];
                if (next.length > RMS_RING_SIZE) next.shift();
                return next;
            });
        });

        return () => {
            socket.disconnect();
        };
    }, [handleData]);

    const status = severityToStatus(severity, mse);

    return { connected, mse, rms, severity, status, alert, trendData, rmsHistory, msgCount };
}