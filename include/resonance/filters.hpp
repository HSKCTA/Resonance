#ifndef RESONANCE_FILTERS_HPP
#define RESONANCE_FILTERS_HPP
#include <vector>

namespace resonance{
    struct BiquadCoeffs{
        float b0, b1, b2, a1,a2;
    };

class IsolationFilter {
public:
    IsolationFilter(float sampleRate = 44100.0f);

    float process(float sample);   // one-sample streaming
    void reset();

private:
    float sampleRate;

    BiquadCoeffs hp, lp;
    float hp_z1=0, hp_z2=0;
    float lp_z1=0, lp_z2=0;

    void calcHPF(float f, float q=0.707f);
    void calcLPF(float f, float q=0.707f);
    float biquad(float x, BiquadCoeffs& c, float& z1, float& z2);
};
}
#endif