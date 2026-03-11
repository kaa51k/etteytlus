"""Whisper transcription using faster-whisper."""

import os
from faster_whisper import WhisperModel


class Transcriber:
    """Transcribes WAV audio files to Estonian text using Whisper."""

    def __init__(self, model_size: str = "medium", device: str = "auto",
                 models_dir: str = "models"):
        os.makedirs(models_dir, exist_ok=True)

        print(f"  [whisper] Loading model '{model_size}' on device '{device}'...")

        compute_type = "float16" if device == "cuda" else "auto"
        if device == "auto":
            compute_type = "auto"

        self.model = WhisperModel(
            model_size,
            device=device if device != "auto" else "auto",
            compute_type=compute_type,
            download_root=models_dir,
        )
        print(f"  [whisper] Model ready.")

    def transcribe(self, audio_path: str) -> str:
        """Transcribe a WAV file to text.

        Args:
            audio_path: Path to a 16kHz mono WAV file.

        Returns:
            Raw transcription text.
        """
        segments, info = self.model.transcribe(
            audio_path,
            language="et",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=300,
            ),
        )

        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())

        full_text = " ".join(text_parts)
        print(f"  [whisper] Transcribed: {len(full_text)} chars")
        return full_text
