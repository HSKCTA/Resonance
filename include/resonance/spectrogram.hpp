#ifndef RESONANCE_SPECTROGRAM_HPP
#define RESONANCE_SPECTROGRAM_HPP

#include <vector>
#include <cstddef>

namespace resonance {

class SpectrogramRing {
public:
    SpectrogramRing(size_t bins = 1024, size_t frames = 64);

    // Push one FFT frame (size = bins)
    void pushFrame(const std::vector<float>& spectrum);

    // True when we have 64 frames ready
    bool isReady() const;

    // Get pointer to contiguous (bins × frames) tensor
    const float* data() const;

    size_t getBins() const { return bins; }
    size_t getFrames() const { return frames; }

private:
    size_t bins;
    size_t frames;

    std::vector<float> ring;   // size = bins × frames
    size_t writeFrame = 0;
    bool full = false;
};

}

#endif
