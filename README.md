# CargoLink Voice Note Assistant – Task 1

**Intern:** Waqar Nadeem  
**Client:** CargoLink Logistics  
**Technology:** Artificial Intelligence  
**Task:** Implement Whisper-based transcription pipeline with logging and architecture decision

## Overview

This repository implements the first deliverable of the CargoLink Voice Note Assistant: a robust speech-to-text backend using **local OpenAI Whisper**. Drivers and coordinators can upload short voice notes; the app transcribes them, shows the raw text, logs every event, and deletes temporary audio files immediately after processing.

## Features (Task 1)

- ✅ New Python module `transcription.py` for audio handling & transcription
- ✅ Local OpenAI Whisper integration wrapped in try/except
- ✅ Structured logging of start / success / failure events to `logs/transcription.log`
- ✅ Architecture Decision Record (`architecture_decision.md` ≈ 300+ words) documenting local vs API trade-offs and the chosen option
- ✅ Streamlit UI accepts audio upload and displays the raw transcript
- ✅ Temporary storage in `temp/` with automatic deletion after processing
- ✅ Supports `.wav`, `.mp3`, `.m4a`, `.ogg`, `.flac`, `.webm`

## Quick Start

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

On first transcription the `base` Whisper model will be downloaded (~140 MB). Subsequent runs are much faster.

## Project Structure

```
cargolink-voice-assistant/
├── app.py                      # Streamlit UI
├── transcription.py            # Audio handling + Whisper pipeline
├── architecture_decision.md    # Pros/cons & final decision (local Whisper)
├── requirements.txt
├── README.md
├── logs/
│   └── transcription.log       # Start / success / failure events
└── temp/                       # Temporary audio storage (auto-cleaned)
```

## Architecture Decision Summary

We evaluated **local Whisper** vs **cloud Speech-to-Text APIs**.

**Chosen:** Local OpenAI Whisper (`base` model)

**Key reasons:**
- Privacy – logistics voice notes stay on the server
- Zero ongoing cost
- Full control and offline capability
- Matches the project brief’s emphasis on open-source Whisper

Full analysis (pros/cons, consequences, implementation notes) is in [`architecture_decision.md`](architecture_decision.md).

## Logging

All transcription events are written to:

```
logs/transcription.log
```

Example entries:

```
2026-11-15 12:00:00 | INFO | cargolink.transcription | Transcription started for file: ...
2026-11-15 12:00:05 | INFO | cargolink.transcription | Transcription succeeded. Language=en, chars=142, segments=3
```

## Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| Transcription function returns text for .wav/.mp3 files and logs errors to a file | ✅ |
| Architecture decision document (≈300 words) with pros/cons and chosen option | ✅ |
| Audio files are stored in a temp folder and deleted after processing | ✅ |

## What I did and why

1. Created a clean, reusable `transcription.py` module that isolates all Whisper and file-I/O logic from the UI.
2. Chose the official `openai-whisper` package with the `base` model – a practical balance of accuracy and resource use for short logistics notes.
3. Implemented lazy model loading, comprehensive try/except blocks, and a `finally` clause that always deletes the temporary audio file.
4. Added structured logging so mentors and future maintainers can debug failures without looking at the UI.
5. Wrote a proper Architecture Decision Record so the choice of local Whisper is transparent and revisitable in later tasks (especially Task 5 deployment).
6. Built a minimal but functional Streamlit interface that satisfies “upload → show raw transcript”.

This foundation will be extended in subsequent tasks with LLM action extraction, a confirmation UI, WER evaluation dashboard, and a secure CI/CD pipeline.

## License

Internship project – for educational and client demonstration purposes.
