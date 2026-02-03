#pragma once
#include <vector>
#include <fftw3.h>

namespace resonance {

class FFTEngine {
public:
    FFTEngine(size_t fftSize = 2048, size_t hopSize = 512);
    ~FFTEngine();

    // Feed one filtered sample
    bool pushSample(float x);

    // Returns true when a new 1024-bin log spectrum is ready
    bool getSpectrum(std::vector<float>& out1024);

private:
    size_t N, hop;
    size_t writeIndex = 0;
    size_t samplesSinceLastFFT = 0;

    std::vector<float> ring;
    std::vector<float> window;

    double* fftIn;
    fftw_complex* fftOut;
    fftw_plan plan;

    void makeHann();
};

}
