#include "resonance/ear.hpp"
#include "resonance/safety.hpp"
#include <iostream>
#include <iomanip>

int main() {
    resonance::Ear ear(44100, 8192);
    resonance::SafetyGate safety(0.7f, 4096);

    std::cout << "--- Project Resonance: Sensor Driver Test ---\n";

    if (!ear.start()) {
        std::cerr << "FATAL: Could not start PortAudio stream\n";
        return -1;
    }

    std::cout << "Ear Online. Monitoring vibration...\n";

    float sample = 0.0f;
    uint32_t sampleCounter = 0;

    while (true) {
        if (ear.popSample(sample)) {
            safety.push(sample);

            if (++sampleCounter >= 4410) { // ~100ms at 44.1kHz
                float rms = safety.lastRMS();

                std::cout << "\rRMS: "
                          << std::fixed << std::setprecision(5)
                          << rms
                          << "  STATUS: "
                          << (safety.isTripped() ? "CRITICAL" : "NORMAL")
                          << std::flush;

                if (safety.isTripped()) {
                    std::cout << "\n[SAFETY] RMS threshold exceeded — AI bypassed\n";
                }

                sampleCounter = 0;
            }
        }
        // No
        //  sleep — let the loop drain the ring buffer
    }

    ear.stop();
    return 0;
}
