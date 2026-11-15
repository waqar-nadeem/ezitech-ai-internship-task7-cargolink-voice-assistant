"""
Audio handling and Whisper-based transcription module for CargoLink Voice Note Assistant.
"""

import os
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple

import whisper

# Configure logging to a hidden/log file
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "transcription.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        # Optional: also log to console during development
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("cargolink.transcription")

# Temp storage for uploaded audio
TEMP_DIR = Path(__file__).parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Supported formats
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}

# Load model once (lazy)
_model = None
MODEL_NAME = "base"  # Good balance of speed/accuracy for logistics voice notes


def get_model():
    """Lazy-load the Whisper model to avoid startup delay and memory waste."""
    global _model
    if _model is None:
        logger.info("Loading Whisper model '%s'...", MODEL_NAME)
        _model = whisper.load_model(MODEL_NAME)
        logger.info("Whisper model loaded successfully.")
    return _model


def save_temp_audio(uploaded_file) -> Path:
    """
    Save an uploaded Streamlit file to a temporary location.
    Returns the path to the saved file.
    """
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported audio format: {suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Create a unique temp file
    temp_path = TEMP_DIR / f"upload_{os.urandom(8).hex()}{suffix}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info("Audio saved to temporary path: %s", temp_path)
    return temp_path


def cleanup_temp_file(path: Path) -> None:
    """Delete a temporary audio file after processing."""
    try:
        if path.exists():
            path.unlink()
            logger.info("Temporary audio file deleted: %s", path)
    except Exception as e:
        logger.warning("Failed to delete temp file %s: %s", path, e)


def transcribe_audio(audio_path: Path, language: Optional[str] = None) -> Tuple[str, dict]:
    """
    Transcribe an audio file using OpenAI Whisper (local).

    Args:
        audio_path: Path to the audio file (.wav, .mp3, etc.)
        language: Optional language code (e.g. 'en'). Auto-detect if None.

    Returns:
        Tuple of (transcript_text, metadata_dict)

    Raises:
        FileNotFoundError, RuntimeError, or other exceptions on failure.
    """
    logger.info("Transcription started for file: %s", audio_path)

    if not audio_path.exists():
        logger.error("Audio file not found: %s", audio_path)
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        model = get_model()
        # Use fp16=False for broader CPU compatibility
        result = model.transcribe(
            str(audio_path),
            language=language,
            fp16=False,
            verbose=False,
        )
        text = result.get("text", "").strip()
        meta = {
            "language": result.get("language"),
            "segments": len(result.get("segments", [])),
            "duration": result.get("segments", [{}])[-1].get("end") if result.get("segments") else None,
        }
        logger.info(
            "Transcription succeeded. Language=%s, chars=%d, segments=%d",
            meta.get("language"),
            len(text),
            meta.get("segments"),
        )
        return text, meta
    except Exception as e:
        logger.exception("Transcription failed for %s: %s", audio_path, e)
        raise RuntimeError(f"Transcription failed: {e}") from e


def process_uploaded_audio(uploaded_file, language: Optional[str] = None) -> Tuple[str, dict]:
    """
    End-to-end helper: save upload → transcribe → cleanup.
    Suitable for Streamlit.
    """
    temp_path = None
    try:
        temp_path = save_temp_audio(uploaded_file)
        text, meta = transcribe_audio(temp_path, language=language)
        return text, meta
    finally:
        if temp_path is not None:
            cleanup_temp_file(temp_path)
