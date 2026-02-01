#include "resonance/ear.hpp"
#include "resonance/safety.hpp"
#include "resonance/filters.hpp"
#include <iostream>
#include <iomanip>
#include <thread> // For yield/sleep

int main() {
    // 1. Instantiate the Full Driver Stack
    resonance::Ear ear(44100, 8192);
    resonance::IsolationFilter filter(44100.0f); // Add this
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
            // Task 1.2: Physics-First Filter
            float filtered = filter.process(sample);
            
            // Task 1.3: Deterministic Safety Gate
            safety.push(filtered);

            if (++sampleCounter >= 4410) { 
                float rms = safety.lastRMS();

                std::cout << "\rRMS: "
                          << std::fixed << std::setprecision(5)
                          << rms
                          << "  STATUS: "
                          << (safety.isTripped() ? "CRITICAL" : "NORMAL")
                          << std::flush;

                if (safety.isTripped()) {
                    std::cout << "\n[SAFETY] RMS threshold exceeded — AI bypassed\n";
                    // Note: Tripped is a latch in your current safety logic
                }
                sampleCounter = 0;
            }
        } else {
            // Buffer empty: Yield CPU to keep the system responsive
            std::this_thread::yield(); 
        }
    }

    ear.stop();
    return 0;
}