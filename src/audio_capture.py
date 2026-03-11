"""Audio capture from laptop microphone into WAV chunks."""

import os
import time
import threading
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

SAMPLE_RATE = 16000  # Whisper expects 16kHz


class AudioCapture:
    """Records audio from the default microphone in fixed-duration chunks."""

    def __init__(self, chunk_duration: int = 30, overlap: int = 5, output_dir: str = "output/chunks"):
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.output_dir = output_dir
        self.sample_rate = SAMPLE_RATE
        self._running = False
        self._chunk_count = 0
        self._callbacks = []

        os.makedirs(output_dir, exist_ok=True)

    def on_chunk_ready(self, callback):
        """Register a callback: callback(chunk_path, chunk_number)."""
        self._callbacks.append(callback)

    def _notify(self, chunk_path: str, chunk_number: int):
        for cb in self._callbacks:
            try:
                cb(chunk_path, chunk_number)
            except Exception as e:
                print(f"  [audio] callback error: {e}")

    def get_mic_level(self) -> float:
        """Record a short sample and return the RMS level (0.0–1.0)."""
        try:
            audio = sd.rec(int(0.5 * self.sample_rate), samplerate=self.sample_rate,
                           channels=1, dtype="float32")
            sd.wait()
            rms = float(np.sqrt(np.mean(audio ** 2)))
            return min(rms * 10, 1.0)  # Scale for display
        except Exception:
            return 0.0

    def start(self):
        """Start recording in a background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        print(f"  [audio] Recording started (chunks={self.chunk_duration}s, overlap={self.overlap}s)")

    def stop(self):
        """Stop recording."""
        self._running = False
        if hasattr(self, "_thread"):
            self._thread.join(timeout=5)
        print(f"  [audio] Recording stopped. {self._chunk_count} chunks saved.")

    def _record_loop(self):
        """Main recording loop — captures overlapping chunks."""
        record_samples = self.chunk_duration * self.sample_rate
        overlap_samples = self.overlap * self.sample_rate
        step_samples = record_samples - overlap_samples

        # First chunk: full duration
        buffer = sd.rec(record_samples, samplerate=self.sample_rate,
                        channels=1, dtype="float32")
        sd.wait()

        self._chunk_count += 1
        path = self._save_chunk(buffer, self._chunk_count)
        self._notify(path, self._chunk_count)

        # Subsequent chunks: keep overlap from previous
        while self._running:
            # Record only the non-overlapping portion
            new_audio = sd.rec(step_samples, samplerate=self.sample_rate,
                               channels=1, dtype="float32")
            sd.wait()

            if not self._running:
                break

            # Combine overlap from end of previous + new recording
            overlap_part = buffer[-overlap_samples:]
            buffer = np.concatenate([overlap_part, new_audio])

            self._chunk_count += 1
            path = self._save_chunk(buffer, self._chunk_count)
            self._notify(path, self._chunk_count)

    def _save_chunk(self, audio: np.ndarray, number: int) -> str:
        """Save audio buffer to WAV file."""
        filename = f"chunk_{number:04d}.wav"
        filepath = os.path.join(self.output_dir, filename)
        # Convert float32 to int16 for WAV
        audio_int16 = (audio * 32767).astype(np.int16)
        wavfile.write(filepath, self.sample_rate, audio_int16)
        print(f"  [audio] Saved {filename} ({len(audio) / self.sample_rate:.1f}s)")
        return filepath
