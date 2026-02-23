#ifndef RESONANCE_EAR_HPP
#define RESONANCE_EAR_HPP

#include <portaudio.h>
#include <atomic>
#include <vector>
#include <string>

namespace resonance{


class Ear{
    public:
    // deviceHint: optional substring to match against PortAudio device names.
    //   e.g. "Logitech", "USB Audio", "G430"  → selects first matching input device.
    //   If empty or no match, falls back to the system default input device.
    Ear(int sampleRate=44100, size_t bufferSize=8192,
        const std::string& deviceHint="");
    ~Ear();

    Ear(const Ear&)=delete;
    Ear& operator=(const Ear&)=delete;
    
    bool start();
    bool stop();
    //task 1.1 LOck free extraction for the rest of the system
    bool popSample(float& sample);

    private:
        static int paCallback(const void* inputBuffer, void* outputBuffer, unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo* timeInfo,PaStreamCallbackFlags statusFlags,void* userData);
        bool pushSample(float sample);

        // Finds a PortAudio device whose name contains deviceHint (case-sensitive).
        // Returns paNoDevice if no match found.
        PaDeviceIndex findDevice() const;

        PaStream* stream=nullptr;
        int sampleRate;
        std::string deviceHint;

        const size_t ringBufferSize;
        std::vector<float> buffer;

        //Atomic indices for the lock free operations 
        std::atomic<size_t> head{0}; //Producer Writes here
        std::atomic<size_t> tail{0}; //Consumer reads from here
    
};

}//namespace resonance
#endif