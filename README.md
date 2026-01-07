# Python Basic SIP/RTP Server

A lightweight SIP (Session Initiation Protocol) and RTP (Real-time Transport Protocol) server implemented in Python. This server acts as a basic echo server for voice calls, receiving SIP INVITE messages, establishing RTP streams, and echoing back received audio packets.

## Why This Instead of Asterisk or FreeSWITCH?

When building a voice bot or IVR system, traditional media servers like Asterisk or FreeSWITCH add significant complexity:
- Steep learning curve and configuration overhead
- Resource-intensive setup and maintenance
- Overkill for simple voice processing applications

This Python implementation provides a direct, minimal path from Cisco (or other SIP endpoints) to your Python application, allowing seamless integration with:
- Speech-to-Text (STT) services
- GPT/LLM for natural language processing
- Text-to-Speech (TTS) for responses

Instead of managing a full media server, you get a simple Python script that handles the SIP signaling and RTP transport, letting you focus on the voice AI logic.

## Features

- SIP signaling support (INVITE, BYE, OPTIONS, UPDATE)
- RTP audio streaming (PCMA codec)
- Automatic RTP port allocation
- Thread-safe call management
- Basic call logging

## How It Works

1. **SIP Handling**: Listens on UDP port 5060 for SIP messages
2. **Call Establishment**: Responds to INVITE with 200 OK and SDP offer
3. **RTP Echo**: Starts an RTP server that echoes received audio packets back to the caller
4. **Call Termination**: Handles BYE messages to clean up resources

## Running the Server

### Local Development

```bash
python server.py
```

The server will bind to `127.0.0.1:5060` by default.

### Environment Variables

- `BIND_IP`: IP address to bind the server (default: `0.0.0.0` for containers)
- `ADVERTISED_IP`: IP address advertised in SDP (default: `127.0.0.1`)

## Modifying for Voice Bot

To transform this into a voice bot, modify the `rtp_echo_server` function in `rtp.py`:

1. **Decode Audio**: Convert incoming PCMA RTP packets to PCM audio
2. **Speech-to-Text**: Send audio chunks to STT service (e.g., Google Speech, Azure, Whisper)
3. **Process with GPT**: Send transcribed text to GPT/LLM for response generation
4. **Text-to-Speech**: Convert response text to audio using TTS service
5. **Encode and Send**: Convert TTS audio back to PCMA and send via RTP

Example modification:

```python
def rtp_voice_bot(server_ip, rtp_port, remote_sdp, stop_event):
    # Parse remote SDP for IP/port
    # ...

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_ip, rtp_port))

    audio_buffer = []

    while not stop_event.is_set():
        data, addr = sock.recvfrom(2048)
        # Decode RTP payload to PCM
        pcm_data = decode_pcma(data)
        audio_buffer.append(pcm_data)

        # Process in chunks
        if len(audio_buffer) > CHUNK_SIZE:
            text = stt.process(audio_buffer)
            response = gpt.generate_response(text)
            tts_audio = tts.synthesize(response)
            # Encode to PCMA RTP and send
            rtp_packets = encode_pcma_rtp(tts_audio)
            for packet in rtp_packets:
                sock.sendto(packet, addr)
```

## Dependencies

- Python 3.7+
- No external dependencies (uses only standard library)

## Testing

Run the unit tests:

```bash
python -m unittest tests/test_sip_message.py
```

## Architecture

- `server.py`: Main SIP server loop and call management
- `sip_message.py`: SIP message parsing
- `sip_response.py`: SIP response building
- `sip_utils.py`: Utility functions for extracting caller/callee info
- `rtp.py`: RTP packet handling (currently echo server)
- `tests/`: Unit tests

## Limitations

- Single codec support (PCMA/G.711)
- No security (no authentication, encryption)
- Basic error handling
- Not production-ready (for development/learning only)

## Contributing

Feel free to extend this for your voice bot needs. Key areas for enhancement:
- Multiple codec support
- DTLS-SRTP for encryption
- Call recording
- Integration with popular STT/TTS/GPT APIs