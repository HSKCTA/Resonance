#include "resonance/broadcaster.hpp"
#include <zmq.hpp>
#include <sstream>

namespace resonance {

Broadcaster::Broadcaster(const std::string& endpoint)
    : context(1), publisher(context, zmq::socket_type::pub)
{
    int hwm = 5;
    publisher.setsockopt(ZMQ_SNDHWM, &hwm, sizeof(hwm));
    publisher.bind(endpoint);
}

Broadcaster::~Broadcaster() {
    publisher.close();
}

void Broadcaster::send(const float* data, size_t bins, size_t frames, uint64_t ts)
{
    // ---------- Frame 0: JSON header ----------
    std::ostringstream json;
    json << "{"
         << "\"timestamp_ms\":" << ts << ","
         << "\"bins\":" << bins << ","
         << "\"frames\":" << frames << ","
         << "\"dtype\":\"float32\""
         << "}";

    std::string header = json.str();
    zmq::message_t headerMsg(header.size());
    memcpy(headerMsg.data(), header.data(), header.size());

    publisher.send(headerMsg, zmq::send_flags::sndmore);

    // ---------- Frame 1: raw tensor ----------
    size_t bytes = bins * frames * sizeof(float);
    zmq::message_t dataMsg(bytes);
    memcpy(dataMsg.data(), data, bytes);

    publisher.send(dataMsg, zmq::send_flags::none);
}

}
