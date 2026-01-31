#ifndef RESONANCE_EAR_HPP
#define RESONANCE_EAR_HPP

#include <portaudio.h>
#include <atomic>
#include<vector>

namespace resonance{


class Ear{
    public:
    Ear(int sampleRate=44100,size_t bufferSize=8192);
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

        PaStream* stream=nullptr;
        int sampleRate;

        const size_t ringBufferSize;
        std::vector<float> buffer;

        //Atomic indices for the lock free operations 
        std::atomic<size_t> head{0}; //Producer Writes here
        std::atomic<size_t> tail{0}; //Consumer reads from here
    
};

}//namespace resonance
#endif