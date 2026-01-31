#include "resonance/ear.hpp"
#include <iostream>

namespace resonance {

Ear::Ear(int sr, size_t bufferSize)
    : stream(nullptr),
      sampleRate(sr),
      ringBufferSize(bufferSize),
      buffer(bufferSize)
{
    Pa_Initialize();
}

Ear::~Ear() {
    stop();
    Pa_Terminate();
}

bool Ear::pushSample(float sample) {
    size_t h = head.load(std::memory_order_relaxed);
    size_t next = (h + 1) % ringBufferSize;

    // buffer full → drop sample
    if (next == tail.load(std::memory_order_acquire))
        return false;

    buffer[h] = sample;
    head.store(next, std::memory_order_release);
    return true;
}

bool Ear::popSample(float& sample) {
    size_t t = tail.load(std::memory_order_relaxed);

    if (t == head.load(std::memory_order_acquire))
        return false; // empty

    sample = buffer[t];
    tail.store((t + 1) % ringBufferSize, std::memory_order_release);
    return true;
}

int Ear::paCallback(
    const void* inputBuffer,
    void*,
    unsigned long framesPerBuffer,
    const PaStreamCallbackTimeInfo*,
    PaStreamCallbackFlags,
    void* userData)
{
    auto* ear = static_cast<Ear*>(userData);
    const float* in = static_cast<const float*>(inputBuffer);

    if (!in)
        return paContinue;

    for (unsigned long i = 0; i < framesPerBuffer; ++i)
        ear->pushSample(in[i]);

    return paContinue;
}

bool Ear::start() {
    PaError err = Pa_OpenDefaultStream(
        &stream,
        1, 0,
        paFloat32,
        sampleRate,
        256,
        paCallback,
        this
    );

    if (err != paNoError) {
        std::cerr << "PortAudio open failed\n";
        return false;
    }

    return Pa_StartStream(stream) == paNoError;
}

bool Ear::stop() {
    if (stream) {
        Pa_StopStream(stream);
        Pa_CloseStream(stream);
        stream = nullptr;
    }
    return true;
}

}
