#include "resonance/fft.hpp"
#include <cmath>

namespace resonance {

FFTEngine::FFTEngine(size_t fftSize, size_t hopSize)
    : N(fftSize), hop(hopSize), ring(fftSize)
{
    fftIn = (double*)fftw_malloc(sizeof(double) * N);
    fftOut = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * (N/2 + 1));
    plan = fftw_plan_dft_r2c_1d(N, fftIn, fftOut, FFTW_MEASURE);
    makeHann();
}

FFTEngine::~FFTEngine() {
    fftw_destroy_plan(plan);
    fftw_free(fftIn);
    fftw_free(fftOut);
}

void FFTEngine::makeHann() {
    window.resize(N);
    for (size_t i = 0; i < N; ++i)
        window[i] = 0.5f * (1.0f - std::cos(2.0f * M_PI * i / (N - 1)));
}

bool FFTEngine::pushSample(float x) {
    ring[writeIndex] = x;
    writeIndex = (writeIndex + 1) % N;
    samplesSinceLastFFT++;

    if (samplesSinceLastFFT >= hop) {
        samplesSinceLastFFT = 0;
        return true;
    }
    return false;
}

bool FFTEngine::getSpectrum(std::vector<float>& out) {
    out.resize(1024);

    // Copy circular buffer → FFT input with window
    for (size_t i = 0; i < N; ++i) {
        size_t idx = (writeIndex + i) % N;
        fftIn[i] = ring[idx] * window[i];
    }

    fftw_execute(plan);

    for (size_t i = 1; i <= 1024; ++i) { // drop DC
        double re = fftOut[i][0];
        double im = fftOut[i][1];
        double mag = std::sqrt(re*re + im*im);
        out[i-1] = std::log10(mag + 1e-12);  // log magnitude
    }

    return true;
}

}
