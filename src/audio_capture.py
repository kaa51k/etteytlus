"""Audio capture from laptop microphone into WAV chunks via continuous stream."""

import os
import time
import threading
import queue
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

SAMPLE_RATE = 16000  # Whisper expects 16kHz


class AudioCapture:
    """Records audio from the default microphone in fixed-duration chunks using a stream."""

    def __init__(self, chunk_duration: int = 30, overlap: int = 5, output_dir: str = "output/chunks"):
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.output_dir = output_dir
        self.sample_rate = SAMPLE_RATE
        self._running = False
        self._chunk_count = 0
        self._callbacks = []
        
        # Audio buffering
        self._queue = queue.Queue()
        self._buffer = np.zeros(0, dtype=np.float32)
        self._buffer_lock = threading.Lock()

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
        """Calculate RMS level (0.0–1.0) from the recent buffer without calling sd.rec()."""
        with self._buffer_lock:
            # Look at the last 0.5 seconds approximately
            samples_to_check = int(0.5 * self.sample_rate)
            if len(self._buffer) == 0:
                return 0.0
            
            # Use up to 0.5s of the most recent audio
            audio = self._buffer[-samples_to_check:]
            
        try:
            # Cast to float64 to avoid overflow encountered in square warnings
            audio_f64 = audio.astype(np.float64)
            rms = float(np.sqrt(np.mean(audio_f64 ** 2)))
            return min(rms * 10, 1.0)  # Scale for display
        except Exception:
            return 0.0

    def _audio_callback(self, indata, frames, time, status):
        """Called by sounddevice stream for each audio block."""
        if status:
            print(f"  [audio stream status] {status}")
        self._queue.put(indata.copy())

    def start(self):
        """Start recording in a background stream + thread."""
        self._running = True
        
        # Start the continuous InputStream
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._audio_callback
        )
        self._stream.start()
        
        # Start the processing thread
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        print(f"  [audio] Stream started (chunks={self.chunk_duration}s, overlap={self.overlap}s)")

    def stop(self):
        """Stop recording."""
        self._running = False
        if hasattr(self, "_stream"):
            self._stream.stop()
            self._stream.close()
            
        if hasattr(self, "_thread"):
            self._thread.join(timeout=5)
            
        print(f"  [audio] Recording stopped. {self._chunk_count} chunks saved.")

    def _process_loop(self):
        """Main loop that takes continuous input and emits overlapping chunks."""
        record_samples = self.chunk_duration * self.sample_rate
        overlap_samples = self.overlap * self.sample_rate
        step_samples = record_samples - overlap_samples

        while self._running:
            # Drain the queue to the buffer
            try:
                while True:
                    data = self._queue.get_nowait()
                    with self._buffer_lock:
                        self._buffer = np.concatenate((self._buffer, data.flatten()))
            except queue.Empty:
                pass
                
            # Check if we have enough data for a chunk
            with self._buffer_lock:
                buffer_len = len(self._buffer)
                
            if buffer_len >= record_samples:
                # We have enough data
                with self._buffer_lock:
                    chunk_audio = self._buffer[:record_samples].copy()
                    # Slide the buffer forward
                    self._buffer = self._buffer[step_samples:]
                    
                self._chunk_count += 1
                path = self._save_chunk(chunk_audio, self._chunk_count)
                # Notify in separate thread/callback
                self._notify(path, self._chunk_count)
            else:
                # Wait a bit before checking again
                time.sleep(0.1)

    def _save_chunk(self, audio: np.ndarray, number: int) -> str:
        """Save audio buffer to WAV file."""
        filename = f"chunk_{number:04d}.wav"
        filepath = os.path.join(self.output_dir, filename)
        # Convert float32 [-1.0, 1.0] to int16
        audio_int16 = (audio * 32767).astype(np.int16)
        wavfile.write(filepath, self.sample_rate, audio_int16)
        print(f"  [audio] Saved {filename} ({len(audio) / self.sample_rate:.1f}s)")
        return filepath
