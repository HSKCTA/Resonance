import requests
import json
import logging
import time

class LLMHandler:
    def __init__(self, url="http://localhost:11434/api/generate", model="llama3"):
        self.url = url
        self.model = model
        
    def check_connection(self):
        try:
            # Test connection to Ollama
            response = requests.get(self.url.replace("/api/generate", "/"))
            if response.status_code == 200:
                logging.info(f"Connected to Ollama at {self.url}")
                return True
            return False
        except requests.exceptions.ConnectionError:
            logging.warning(f"Could not connect to Ollama at {self.url}. LLM features will be disabled.")
            return False

    def generate_alert(self, anomaly_score, detection_details):
        """
        Generates a worker-friendly alert using the local LLM.
        """
        prompt = f"""
        You are an industrial AI assistant. 
        A machine fault has been detected.
        
        Technical Details:
        - Reconstruction Error (MSE): {anomaly_score:.4f}
        - Severity: {detection_details.get('severity', 'Unknown')}
        - Message: {detection_details.get('message', 'Harmonic distortion detected')}
        
        Task:
        Translate this into a clear, concise instruction for a factory worker in English.
        Do not explain the AI model. Focus on the physical check required.
        Example output: "High vibration detected. Please check the motor bearings immediately."
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=10) # 10s timeout
            if response.status_code == 200:
                response_json = response.json()
                return response_json.get("response", "Alert generated but empty response.")
            else:
                logging.error(f"Ollama returned error: {response.text}")
                return f"Error detecting fault: Severity {detection_details.get('severity')}. Please check machine."
                
        except Exception as e:
            logging.error(f"Failed to query LLM: {e}")
            return f"FAULT DETECTED (Severity: {detection_details.get('severity')}). Check machine immediately."

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    handler = LLMHandler(model="phi3") # Use phi3 or llama3 depending on what's installed
    if handler.check_connection():
        print(handler.generate_alert(0.25, {"severity": "HIGH", "message": "High frequency noise"}))
