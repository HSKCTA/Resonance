#include "resonance/safety.hpp"
#include <cmath>

namespace resonance {

SafetyGate::SafetyGate(float thresh, size_t win)
    : threshold(thresh),
      windowSize(win),
      window(win, 0.0f) {}

void SafetyGate::push(float sample) {
    float old = window[index];
    sumSq -= old * old;

    window[index] = sample;
    sumSq += sample * sample;

    // clamp against FP drift
    if (sumSq < 0.0f)
        sumSq = 0.0f;

    index = (index + 1) % windowSize;

    rms = std::sqrt(sumSq / windowSize);

    if (rms > threshold)
        tripped = true;
}

bool SafetyGate::isTripped() const {
    return tripped;
}

float SafetyGate::lastRMS() const {
    return rms;
}

}
