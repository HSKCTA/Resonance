from inference.zmq_listener import ZMQSpectrogramListener
from inference.ae_inference import AutoencoderInference
from inference.anomaly_score import AnomalyScorer
from llm.translator import WorkerAlertGenerator


def main():
    # -------------------------
    # Initialize components
    # -------------------------
    zmq_listener = ZMQSpectrogramListener(
        endpoint="tcp://localhost:5555"
    )

    ae_engine = AutoencoderInference(
        onnx_model_path="onnx/autoencoder.onnx"
    )

    scorer = AnomalyScorer()

    # Local LLM (change language if needed: "mr", "hi", "en")
    alert_generator = WorkerAlertGenerator(
        model="phi3",
        language="mr"
    )

    print("[NODE B] Resonance AI Inference Started")

    # -------------------------
    # Main loop
    # -------------------------
    while True:
        spec, metadata = zmq_listener.receive()

        # Autoencoder reconstruction
        recon = ae_engine.reconstruct(spec)

        # Anomaly logic
        score = scorer.reconstruction_error(spec, recon)
        is_anomaly = scorer.is_anomaly(score)
        severity = scorer.severity(score)

        print(
            f"[NODE B] Score: {score:.6f} | "
            f"Severity: {severity} | "
            f"Anomaly: {is_anomaly} | "
            f"Meta: {metadata}"
        )

        # -------------------------
        # LLM alert (ONLY on anomaly)
        # -------------------------
        if is_anomaly:
            fault = "असामान्य कंपन"  # can be improved later

            try:
                alert_msg = alert_generator.generate_alert(
                    fault=fault,
                    severity=severity
                )
                print("[ALERT]", alert_msg)
            except Exception as e:
                print("[LLM ERROR]", e)


if __name__ == "__main__":
    main()
