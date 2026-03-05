/**
 * Resonance — DSP Pipeline Latency Benchmark
 * Benchmark B: Filter → FFT → Spectrogram on CPU
 *
 * Measures each DSP stage independently using synthetic audio samples.
 * No microphone or NPU required.
 *
 * Compile:
 *   g++ -O2 -std=c++17 benchmark_dsp.cpp -lfftw3 -lm -o benchmark_dsp
 */

#include <cmath>
#include <cstring>
#include <chrono>
#include <vector>
#include <numeric>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include <fftw3.h>

// ═══════════════════════════════════════════════════
//  Inline copies of the DSP kernels (self-contained)
// ═══════════════════════════════════════════════════

// ── IIR Biquad (high-pass + low-pass chain) ──────
struct Biquad {
    double b0, b1, b2, a1, a2;
    double x1 = 0, x2 = 0, y1 = 0, y2 = 0;

    float process(float in) {
        double out = b0*in + b1*x1 + b2*x2 - a1*y1 - a2*y2;
        x2 = x1; x1 = in;
        y2 = y1; y1 = out;
        return static_cast<float>(out);
    }
};

Biquad make_highpass(float fs, float fc) {
    double w0 = 2.0 * M_PI * fc / fs;
    double alpha = sin(w0) / (2.0 * 0.7071);
    double a0 = 1.0 + alpha;
    return {
        (1.0 + cos(w0)) / 2.0 / a0,
        -(1.0 + cos(w0)) / a0,
        (1.0 + cos(w0)) / 2.0 / a0,
        -2.0 * cos(w0) / a0,
        (1.0 - alpha) / a0,
        0, 0, 0, 0
    };
}

Biquad make_lowpass(float fs, float fc) {
    double w0 = 2.0 * M_PI * fc / fs;
    double alpha = sin(w0) / (2.0 * 0.7071);
    double a0 = 1.0 + alpha;
    return {
        (1.0 - cos(w0)) / 2.0 / a0,
        (1.0 - cos(w0)) / a0,
        (1.0 - cos(w0)) / 2.0 / a0,
        -2.0 * cos(w0) / a0,
        (1.0 - alpha) / a0,
        0, 0, 0, 0
    };
}

// ── FFT Engine (matches resonance::FFTEngine) ─────
class FFTEngine {
    size_t N, hop;
    std::vector<float> ring;
    std::vector<float> window;
    double*        fftIn;
    fftw_complex*  fftOut;
    fftw_plan      plan;
    size_t writeIndex = 0;
    size_t samplesSinceLastFFT = 0;

public:
    FFTEngine(size_t fftSize, size_t hopSize)
        : N(fftSize), hop(hopSize), ring(fftSize, 0.0f)
    {
        fftIn  = (double*)fftw_malloc(sizeof(double) * N);
        fftOut = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * (N/2 + 1));
        plan   = fftw_plan_dft_r2c_1d(N, fftIn, fftOut, FFTW_MEASURE);
        window.resize(N);
        for (size_t i = 0; i < N; ++i)
            window[i] = 0.5f * (1.0f - std::cos(2.0f * M_PI * i / (N - 1)));
    }

    ~FFTEngine() {
        fftw_destroy_plan(plan);
        fftw_free(fftIn);
        fftw_free(fftOut);
    }

    bool pushSample(float x) {
        ring[writeIndex] = x;
        writeIndex = (writeIndex + 1) % N;
        samplesSinceLastFFT++;
        if (samplesSinceLastFFT >= hop) {
            samplesSinceLastFFT = 0;
            return true;
        }
        return false;
    }

    bool getSpectrum(std::vector<float>& out) {
        out.resize(1024);
        for (size_t i = 0; i < N; ++i) {
            size_t idx = (writeIndex + i) % N;
            fftIn[i] = ring[idx] * window[i];
        }
        fftw_execute(plan);
        for (size_t i = 1; i <= 1024; ++i) {
            double re = fftOut[i][0];
            double im = fftOut[i][1];
            out[i-1] = std::log10(std::sqrt(re*re + im*im) + 1e-12);
        }
        return true;
    }
};

// ── Spectrogram Ring (matches resonance::SpectrogramRing) ──
class SpectrogramRing {
    size_t bins, frames;
    std::vector<float> ring;
    size_t writeFrame = 0;
    bool full = false;

public:
    SpectrogramRing(size_t b, size_t f)
        : bins(b), frames(f), ring(b * f, 0.0f) {}

    void pushFrame(const std::vector<float>& spectrum) {
        if (spectrum.size() != bins) return;
        std::memcpy(&ring[writeFrame * bins], spectrum.data(), bins * sizeof(float));
        writeFrame = (writeFrame + 1) % frames;
        full = (writeFrame == 0);
    }

    bool isReady() const { return full; }
    const float* data() const { return ring.data(); }
    size_t size() const { return bins * frames; }
};

// ═══════════════════════════════════════════════════
//  Helpers
// ═══════════════════════════════════════════════════

struct Stats {
    double mean, stddev, minv, maxv, p95, p99;
};

Stats compute(std::vector<double>& v) {
    std::sort(v.begin(), v.end());
    double sum = std::accumulate(v.begin(), v.end(), 0.0);
    double m   = sum / v.size();
    double sq  = 0;
    for (auto x : v) sq += (x - m) * (x - m);
    return {
        m,
        std::sqrt(sq / v.size()),
        v.front(),
        v.back(),
        v[static_cast<size_t>(v.size() * 0.95)],
        v[static_cast<size_t>(v.size() * 0.99)]
    };
}

void printStats(const char* label, Stats& s) {
    std::cout << "  " << std::left << std::setw(22) << label
              << std::right << std::fixed << std::setprecision(3)
              << "Mean: " << std::setw(8) << s.mean << " µs"
              << "  Std: " << std::setw(8) << s.stddev << " µs"
              << "  Min: " << std::setw(8) << s.minv << " µs"
              << "  Max: " << std::setw(8) << s.maxv << " µs"
              << "\n";
}

// ═══════════════════════════════════════════════════
//  Main benchmark
// ═══════════════════════════════════════════════════

int main() {
    constexpr float  SAMPLE_RATE  = 44100.0f;
    constexpr size_t FFT_SIZE     = 2048;
    constexpr size_t HOP_SIZE     = 512;
    constexpr size_t FREQ_BINS    = 1024;
    constexpr size_t TIME_FRAMES  = 64;
    constexpr int    RUNS         = 1000;
    constexpr int    WARMUP       = 50;

    // ── Generate synthetic audio buffer ─────────────
    // ~3 seconds of mixed sinusoids (simulates motor vibration)
    const size_t totalSamples = static_cast<size_t>(SAMPLE_RATE * 3.0f);
    std::vector<float> audio(totalSamples);
    for (size_t i = 0; i < totalSamples; ++i) {
        float t = static_cast<float>(i) / SAMPLE_RATE;
        audio[i] = 0.3f * std::sin(2.0f * M_PI * 120.0f * t)   // 1× shaft
                 + 0.1f * std::sin(2.0f * M_PI * 240.0f * t)   // 2× shaft
                 + 0.05f * std::sin(2.0f * M_PI * 5000.0f * t) // bearing harmonic
                 + 0.02f * (static_cast<float>(rand()) / RAND_MAX - 0.5f); // noise
    }

    // ── Init DSP chain ──────────────────────────────
    auto hp = make_highpass(SAMPLE_RATE, 100.0f);
    auto lp = make_lowpass(SAMPLE_RATE, 12000.0f);
    FFTEngine fft(FFT_SIZE, HOP_SIZE);
    SpectrogramRing spec(FREQ_BINS, TIME_FRAMES);

    std::vector<double> filterTimes, fftTimes, spectrogramTimes, totalTimes;

    std::cout << "\n====================================================\n";
    std::cout << "  RESONANCE — DSP PIPELINE LATENCY BENCHMARK\n";
    std::cout << "====================================================\n\n";
    std::cout << "  Config:\n";
    std::cout << "    Sample rate   : " << SAMPLE_RATE << " Hz\n";
    std::cout << "    FFT size      : " << FFT_SIZE << " points\n";
    std::cout << "    Hop size      : " << HOP_SIZE << " (75% overlap)\n";
    std::cout << "    Freq bins     : " << FREQ_BINS << "\n";
    std::cout << "    Time frames   : " << TIME_FRAMES << "\n";
    std::cout << "    Runs          : " << RUNS << " + " << WARMUP << " warmup\n\n";
    std::cout << "  Running..." << std::flush;

    // We measure the time to process one full spectrogram (64 FFT hops)
    // Each hop = 512 samples filtered + 1 FFT + 1 spectrogram push

    size_t sampleIdx = 0;

    auto nextSample = [&]() -> float {
        float s = audio[sampleIdx % audio.size()];
        sampleIdx++;
        return s;
    };

    // ── Warmup ──────────────────────────────────────
    for (int w = 0; w < WARMUP; ++w) {
        while (!spec.isReady()) {
            float sample = nextSample();
            float filtered = lp.process(hp.process(sample));
            if (!fft.pushSample(filtered)) continue;
            std::vector<float> spectrum;
            fft.getSpectrum(spectrum);
            spec.pushFrame(spectrum);
        }
        // Reset spectrogram readiness by pushing one more frame
        std::vector<float> dummy(FREQ_BINS, 0.0f);
        spec.pushFrame(dummy);
    }

    // ── Timed runs ──────────────────────────────────
    for (int r = 0; r < RUNS; ++r) {
        double filterTotal = 0, fftTotal = 0, specTotal = 0;

        auto t_start = std::chrono::high_resolution_clock::now();

        while (!spec.isReady()) {
            // ── Filter stage ────
            float sample = nextSample();
            auto tf0 = std::chrono::high_resolution_clock::now();
            float filtered = lp.process(hp.process(sample));
            auto tf1 = std::chrono::high_resolution_clock::now();
            filterTotal += std::chrono::duration<double, std::micro>(tf1 - tf0).count();

            if (!fft.pushSample(filtered)) continue;

            // ── FFT stage ───────
            std::vector<float> spectrum;
            auto t_fft0 = std::chrono::high_resolution_clock::now();
            fft.getSpectrum(spectrum);
            auto t_fft1 = std::chrono::high_resolution_clock::now();
            fftTotal += std::chrono::duration<double, std::micro>(t_fft1 - t_fft0).count();

            // ── Spectrogram stage ─
            auto t_sp0 = std::chrono::high_resolution_clock::now();
            spec.pushFrame(spectrum);
            auto t_sp1 = std::chrono::high_resolution_clock::now();
            specTotal += std::chrono::duration<double, std::micro>(t_sp1 - t_sp0).count();
        }

        auto t_end = std::chrono::high_resolution_clock::now();
        double totalUs = std::chrono::duration<double, std::micro>(t_end - t_start).count();

        filterTimes.push_back(filterTotal);
        fftTimes.push_back(fftTotal);
        spectrogramTimes.push_back(specTotal);
        totalTimes.push_back(totalUs);

        // Reset for next run
        std::vector<float> dummy(FREQ_BINS, 0.0f);
        spec.pushFrame(dummy);
    }

    // ── Report ──────────────────────────────────────
    auto fsStats = compute(filterTimes);
    auto ffStats = compute(fftTimes);
    auto spStats = compute(spectrogramTimes);
    auto ttStats = compute(totalTimes);

    std::cout << "\r                        \n";
    std::cout << "----------------------------------------------------\n";
    std::cout << "  Per-spectrogram (64 FFT hops) latency:\n";
    std::cout << "----------------------------------------------------\n";
    printStats("Filter (HP+LP):", fsStats);
    printStats("FFT (64 hops):", ffStats);
    printStats("Spectrogram build:", spStats);
    std::cout << "----------------------------------------------------\n";
    printStats("Total DSP:", ttStats);
    std::cout << "====================================================\n\n";

    std::cout << "  Summary (per spectrogram frame):\n";
    std::cout << "    Filter time       : " << std::fixed << std::setprecision(3)
              << fsStats.mean / 1000.0 << " ms\n";
    std::cout << "    FFT time          : " << ffStats.mean / 1000.0 << " ms\n";
    std::cout << "    Spectrogram time  : " << spStats.mean / 1000.0 << " ms\n";
    std::cout << "    Total DSP latency : " << ttStats.mean / 1000.0 << " ms\n";
    std::cout << "    Worst case        : " << ttStats.maxv / 1000.0 << " ms\n";
    std::cout << "\n====================================================\n";

    return 0;
}
