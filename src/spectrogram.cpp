#include "resonance/spectrogram.hpp"
#include <cstring>

namespace resonance {

SpectrogramRing::SpectrogramRing(size_t b, size_t f)
    : bins(b), frames(f), ring(b * f, 0.0f) {}

void SpectrogramRing::pushFrame(const std::vector<float>& spectrum) {
    if (spectrum.size() != bins)
        return;  // safety

    // Write this frame column-wise: freq × time
    size_t offset = writeFrame * bins;
    std::memcpy(&ring[offset], spectrum.data(), bins * sizeof(float));

    writeFrame = (writeFrame + 1) % frames;
    if (writeFrame == 0)
        full = true;
}

bool SpectrogramRing::isReady() const {
    return full;
}

const float* SpectrogramRing::data() const {
    return ring.data();
}

}
