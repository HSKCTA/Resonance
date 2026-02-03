#include "resonance/ear.hpp"
#include "resonance/safety.hpp"
#include "resonance/filters.hpp"
#include "resonance/fft.hpp"
#include "resonance/spectrogram.hpp"
#include "resonance/broadcaster.hpp"

#include <iostream>
#include <iomanip>
#include <thread>
#include <chrono>

int main() {
    constexpr float SAMPLE_RATE = 44100.0f;

    resonance::Ear ear(44100, 8192);
    resonance::IsolationFilter filter(SAMPLE_RATE);
    resonance::SafetyGate safety(0.7f, 4096);
    resonance::FFTEngine fft(2048, 512);
    resonance::SpectrogramRing spectrogram(1024, 64);
    resonance::Broadcaster broadcaster("tcp://*:5555");

    std::cout << "--- Project Resonance: Node A (The Ear) ---\n";

    if (!ear.start()) {
        std::cerr << "FATAL: Could not start PortAudio stream\n";
        return -1;
    }

    std::cout << "Ear online. Streaming vibration → AI…\n";

    float sample = 0.0f;
    uint32_t sampleCounter = 0;

    while (true) {
        if (!ear.popSample(sample)) {
            std::this_thread::yield();
            continue;
        }

        // ---------- Physics-first DSP ----------
        float filtered = filter.process(sample);

        // ---------- Deterministic Safety ----------
        safety.push(filtered);

        if (safety.isTripped()) {
            std::cout << "\n[SAFETY] RMS threshold exceeded — AI bypassed\n";
            continue; // do not feed FFT or AI
        }

        // ---------- FFT hop scheduler ----------
        if (!fft.pushSample(filtered))
            continue;

        // ---------- FFT frame ----------
        std::vector<float> spectrum;
        fft.getSpectrum(spectrum);   // 1024 bins (log-magnitude)

        // ---------- Spectrogram builder ----------
        spectrogram.pushFrame(spectrum);

        // ---------- When we have 64 frames, publish ----------
        if (spectrogram.isReady()) {
            uint64_t ts = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();

            broadcaster.send(
                spectrogram.data(),
                spectrogram.getBins(),
                spectrogram.getFrames(),
                ts
            );
        }

        // ---------- Throttled RMS display ----------
        if (++sampleCounter >= 4410) {
            float rms = safety.lastRMS();
            std::cout << "\rRMS: "
                      << std::fixed << std::setprecision(5)
                      << rms
                      << "  STATUS: NORMAL"
                      << std::flush;
            sampleCounter = 0;
        }
    }

    ear.stop();
    return 0;
}
