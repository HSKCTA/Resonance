#ifndef RESONANCE_BROADCASTER_HPP
#define RESONANCE_BROADCASTER_HPP

#include <zmq.hpp>
#include <string>
#include <cstdint>

namespace resonance {

class Broadcaster {
public:
    Broadcaster(const std::string& endpoint = "tcp://*:5555");
    ~Broadcaster();

    void send(
        const float* spectrogram,   // pointer to 1024×64 floats
        size_t bins,                // 1024
        size_t frames,              // 64
        uint64_t timestamp_ms
    );

private:
    zmq::context_t context;
    zmq::socket_t publisher;
};

} // namespace resonance

#endif
