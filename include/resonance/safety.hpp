#pragma once
#include <cstddef>
#include <vector>

namespace resonance{
    class SafetyGate{
        public:

        SafetyGate(float threshold,size_t windowSize =4096);
        //feed one Raw smaple
        void push(float sample);
        //true if vibration exceeded limit
        bool isTripped() const;
        //most recent RMS
        float lastRMS() const;
    
        private:
        const float threshold;
        const size_t windowSize;
        std::vector<float> window;
        size_t index = 0;
        float sumSq = 0.0f;
        float rms=0.0f;
        bool tripped=false;

    };
}
