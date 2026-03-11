"""Tests for audio capture module."""

import os
import numpy as np
from unittest.mock import patch, MagicMock


class TestAudioCapture:
    """Test mic audio capture into WAV chunks."""

    def _make_capture(self, tmp_path, chunk_duration=3, overlap=1):
        from audio_capture import AudioCapture
        return AudioCapture(
            chunk_duration=chunk_duration,
            overlap=overlap,
            output_dir=str(tmp_path),
        )

    def test_init_creates_output_dir(self, tmp_path):
        """Output directory should be created on init."""
        out = tmp_path / "chunks"
        from audio_capture import AudioCapture
        AudioCapture(chunk_duration=3, overlap=1, output_dir=str(out))
        assert out.exists()

    def test_save_chunk_creates_wav(self, tmp_path, sample_audio):
        """Saving a chunk should create a valid WAV file."""
        capture = self._make_capture(tmp_path)
        audio, sr = sample_audio
        path = capture._save_chunk(audio.reshape(-1, 1), 1)
        assert os.path.exists(path)
        assert path.endswith(".wav")

    def test_callback_registration(self, tmp_path):
        """Registered callbacks should be stored."""
        capture = self._make_capture(tmp_path)
        callback = MagicMock()
        capture.on_chunk_ready(callback)
        assert callback in capture._callbacks

    def test_notify_calls_callbacks(self, tmp_path):
        """Notify should call all registered callbacks."""
        capture = self._make_capture(tmp_path)
        cb1 = MagicMock()
        cb2 = MagicMock()
        capture.on_chunk_ready(cb1)
        capture.on_chunk_ready(cb2)
        capture._notify("path/to/chunk.wav", 1)
        cb1.assert_called_once_with("path/to/chunk.wav", 1)
        cb2.assert_called_once_with("path/to/chunk.wav", 1)

    def test_mic_level_returns_float(self, tmp_path):
        """get_mic_level should return a float between 0 and 1."""
        with patch("audio_capture.sd") as mock_sd:
            mock_sd.rec.return_value = np.zeros((8000, 1), dtype=np.float32)
            mock_sd.wait.return_value = None

            capture = self._make_capture(tmp_path)
            level = capture.get_mic_level()
            assert isinstance(level, float)
            assert 0.0 <= level <= 1.0
