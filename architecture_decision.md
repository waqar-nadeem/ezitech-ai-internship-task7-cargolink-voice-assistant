# Architecture Decision Record: Speech-to-Text Backend for CargoLink Voice Note Assistant

**Date:** 15 November 2026  
**Status:** Accepted  
**Deciders:** Waqar Nadeem (Intern), Ezitech Mentors  
**Context:** Task 1 – Implement Whisper-based transcription pipeline with logging and architecture decision

## Context and Problem Statement

CargoLink Logistics needs a reliable speech-to-text service that turns driver and coordinator voice notes into text so that downstream LLM modules can extract actionable logistics tasks. The system must run inside a Streamlit web application, support common audio formats (.wav, .mp3), handle errors gracefully, log all events, and store audio only temporarily.

Two primary options exist:

1. **Local OpenAI Whisper (open-source, ggml-compatible models)**  
2. **Cloud API** (OpenAI Whisper API, Google Speech-to-Text, Azure Speech, AssemblyAI, etc.)

## Decision Drivers

- Data privacy and confidentiality of logistics operations
- Cost predictability for an internship / early-stage deployment
- Latency and offline capability
- Ease of integration with the existing Streamlit stack
- Accuracy on noisy / accented voice notes typical in logistics
- Deployment constraints (Streamlit Community Cloud later in the project)

## Options Considered

### Option A – Local Whisper (openai-whisper / faster-whisper)

**Pros**
- Complete data privacy: audio never leaves the server.
- Zero per-minute cost after the one-time model download.
- Works offline; useful for warehouse or low-connectivity scenarios.
- Full control over model size (tiny → large) and decoding parameters.
- Easy to wrap with try/except, structured logging, and temporary file lifecycle.
- Matches the brief’s explicit mention of “OpenAI Whisper (ggml)”.

**Cons**
- Higher RAM / CPU (or GPU) requirements; “base” model is acceptable, “large” is heavy for free-tier Streamlit Cloud.
- Cold-start latency when the model is first loaded.
- Slightly lower accuracy than the latest cloud models on very noisy audio unless fine-tuned.
- Model download and packaging must be handled carefully for reproducible deploys.

### Option B – Cloud Speech-to-Text API

**Pros**
- Near state-of-the-art accuracy out of the box.
- Minimal local compute; ideal for Streamlit Community Cloud free tier.
- Built-in language detection, speaker diarization, and punctuation in many providers.
- Simple HTTP client; no large model files to manage.

**Cons**
- Audio leaves the organisation’s control → potential compliance and privacy issues for logistics data.
- Ongoing cost (per minute or per character) that scales with usage.
- Requires API keys, network connectivity, and rate-limit handling.
- Vendor lock-in and possible latency spikes.

## Decision

We choose **Option A – Local OpenAI Whisper** (model size “base”) for the following reasons:

1. Privacy is a hard requirement for internal logistics voice notes that may contain shipment IDs, addresses, and operational details.
2. The internship project emphasises open-source tooling and an architecture decision document; local Whisper satisfies both.
3. For the expected volume (dozens of short notes per day) the hardware footprint of the “base” model is manageable, and we can later swap to `faster-whisper` or a quantized ggml model if Streamlit Cloud resource limits become an issue.
4. Temporary file storage + immediate deletion after transcription keeps the attack surface small and complies with the “delete after processing” acceptance criterion.

## Consequences

- Positive: Full control, no recurring costs, strong privacy story for the client hand-over package.
- Negative: Must monitor memory usage; may need to fall back to a smaller model or add a GPU option for production.
- Neutral: Logging and error handling are implemented identically regardless of the backend, so swapping to an API later would be a contained change.

## Implementation Notes

- Model is loaded lazily on first request and cached in memory.
- All audio is written to a `temp/` directory with a random name, transcribed, then deleted in a `finally` block.
- Start, success, and failure events are written to `logs/transcription.log`.
- The Streamlit UI simply calls `process_uploaded_audio()` and displays the returned text.

This decision will be revisited in Task 5 when the deployment pipeline and resource constraints of Streamlit Community Cloud are fully known.
