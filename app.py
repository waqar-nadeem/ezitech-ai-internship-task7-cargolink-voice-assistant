"""
CargoLink Logistics – Voice Note Assistant
Task 1: Whisper-based transcription pipeline with logging
"""

import streamlit as st
from pathlib import Path

from transcription import process_uploaded_audio, LOG_FILE, TEMP_DIR

st.set_page_config(
    page_title="CargoLink Voice Note Assistant",
    page_icon="🚛",
    layout="centered",
)

st.title("🚛 CargoLink Voice Note Assistant")
st.caption("Task 1 – Speech-to-Text Pipeline (Whisper)")

st.markdown(
    """
Upload a short voice note from a driver or coordinator.  
The app will transcribe it locally with OpenAI Whisper and show the raw text below.
"""
)

# Sidebar info
with st.sidebar:
    st.header("About")
    st.markdown(
        """
        **Architecture:** Local Whisper (`base` model)  
        **Logging:** `logs/transcription.log`  
        **Temp storage:** `temp/` (auto-deleted after processing)
        """
    )
    st.markdown("---")
    st.markdown("See `architecture_decision.md` for the full trade-off analysis.")

uploaded_file = st.file_uploader(
    "Upload voice note (.wav, .mp3, .m4a, .ogg, .flac, .webm)",
    type=["wav", "mp3", "m4a", "ogg", "flac", "webm"],
    help="Short voice notes work best. The file is stored temporarily and deleted after transcription.",
)

if uploaded_file is not None:
    st.audio(uploaded_file, format=f"audio/{Path(uploaded_file.name).suffix[1:]}")

    col1, col2 = st.columns([1, 3])
    with col1:
        language = st.selectbox(
            "Language (optional)",
            options=[None, "en", "es", "fr", "de", "ur", "hi", "ar"],
            format_func=lambda x: "Auto-detect" if x is None else x,
        )
    with col2:
        st.write("")  # spacing
        transcribe_btn = st.button("Transcribe", type="primary", use_container_width=True)

    if transcribe_btn:
        with st.spinner("Transcribing with Whisper… this may take a few seconds on first run (model download)."):
            try:
                transcript, meta = process_uploaded_audio(uploaded_file, language=language)
                st.success("Transcription complete")
                st.subheader("Raw Transcript")
                st.text_area(
                    "Transcript",
                    value=transcript or "(empty)",
                    height=200,
                    label_visibility="collapsed",
                )
                with st.expander("Metadata"):
                    st.json(meta)
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                st.info("Check `logs/transcription.log` for details.")

st.markdown("---")
st.caption(
    f"Temp dir: `{TEMP_DIR}` · Log file: `{LOG_FILE}` · "
    "Audio files are deleted immediately after processing."
)
