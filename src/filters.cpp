#include "resonance/filters.hpp"
#include <cmath>

namespace resonance {

IsolationFilter::IsolationFilter(float sr)
    : sampleRate(sr)
{
    calcHPF(150.0f);     // remove DC, hum, speech
    calcLPF(12000.0f);  // remove ultrasonic junk
    reset();
}

void IsolationFilter::reset() {
    hp_z1 = hp_z2 = 0.0f;
    lp_z1 = lp_z2 = 0.0f;
}

// RBJ HIGH PASS FILTER
void IsolationFilter::calcHPF(float f, float q) {
    float w = 2.0f * M_PI * f / sampleRate;
    float c = cos(w);
    float s = sin(w);
    float a = s / (2.0f * q);

    float a0 = 1.0f + a;

    hp.b0 =  (1.0f + c) / (2.0f * a0);
    hp.b1 = -(1.0f + c) / a0;
    hp.b2 =  (1.0f + c) / (2.0f * a0);
    hp.a1 = -2.0f * c / a0;
    hp.a2 = (1.0f - a) / a0;
}

// RBJ LOW PASS FILTER
void IsolationFilter::calcLPF(float f, float q) {
    float w = 2.0f * M_PI * f / sampleRate;
    float c = cos(w);
    float s = sin(w);
    float a = s / (2.0f * q);

    float a0 = 1.0f + a;

    lp.b0 = (1.0f - c) / (2.0f * a0);
    lp.b1 = (1.0f - c) / a0;
    lp.b2 = (1.0f - c) / (2.0f * a0);
    lp.a1 = -2.0f * c / a0;
    lp.a2 = (1.0f - a) / a0;
}


// BIQUAD CORE (DF-II)
float IsolationFilter::biquad(float x, BiquadCoeffs& c, float& z1, float& z2) {
    float y = c.b0 * x + z1;
    z1 = c.b1 * x - c.a1 * y + z2;
    z2 = c.b2 * x - c.a2 * y;
    return y;
}

// STREAMING FILTER
float IsolationFilter::process(float x) {
    x = biquad(x, hp, hp_z1, hp_z2);
    x = biquad(x, lp, lp_z1, lp_z2);
    return x;
}

} // namespace resonance
