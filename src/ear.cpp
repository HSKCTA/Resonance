#include "resonance/ear.hpp"
#include <iostream>
#include <cstring>

namespace resonance {

Ear::Ear(int sr, size_t bufferSize, const std::string& hint)
    : stream(nullptr),
      sampleRate(sr),
      deviceHint(hint),
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

PaDeviceIndex Ear::findDevice() const {
    if (deviceHint.empty())
        return paNoDevice;

    int numDevices = Pa_GetDeviceCount();
    for (int i = 0; i < numDevices; ++i) {
        const PaDeviceInfo* info = Pa_GetDeviceInfo(i);
        if (info && info->maxInputChannels > 0 &&
            std::strstr(info->name, deviceHint.c_str()) != nullptr) {
            std::cout << "[Ear] Matched device " << i
                      << ": \"" << info->name << "\"\n";
            return static_cast<PaDeviceIndex>(i);
        }
    }

    std::cerr << "[Ear] No device matching \"" << deviceHint
              << "\" — falling back to default\n";
    std::cerr << "[Ear] Available input devices:\n";
    int numDev = Pa_GetDeviceCount();
    for (int i = 0; i < numDev; ++i) {
        const PaDeviceInfo* info = Pa_GetDeviceInfo(i);
        if (info && info->maxInputChannels > 0)
            std::cerr << "       [" << i << "] " << info->name << "\n";
    }
    return paNoDevice;
}

bool Ear::start() {
    PaDeviceIndex deviceIdx = findDevice();

    PaStreamParameters inputParams;
    if (deviceIdx != paNoDevice) {
        inputParams.device = deviceIdx;
    } else {
        inputParams.device = Pa_GetDefaultInputDevice();
    }

    if (inputParams.device == paNoDevice) {
        std::cerr << "PortAudio: no input device available\n";
        return false;
    }

    const PaDeviceInfo* devInfo = Pa_GetDeviceInfo(inputParams.device);
    inputParams.channelCount     = 1;
    inputParams.sampleFormat     = paFloat32;
    inputParams.suggestedLatency = devInfo->defaultLowInputLatency;
    inputParams.hostApiSpecificStreamInfo = nullptr;

    std::cout << "[Ear] Opening device " << inputParams.device
              << ": \"" << devInfo->name << "\"  @ "
              << sampleRate << " Hz\n";

    PaError err = Pa_OpenStream(
        &stream,
        &inputParams,
        nullptr,        // no output
        sampleRate,
        256,
        paClipOff,
        paCallback,
        this
    );

    if (err != paNoError) {
        std::cerr << "PortAudio open failed: " << Pa_GetErrorText(err) << "\n";
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
