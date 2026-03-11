"""Tests for Whisper transcriber module."""

from unittest.mock import patch, MagicMock


class TestTranscriber:
    """Test Whisper transcription."""

    def test_model_loads(self, tmp_path):
        """Transcriber should load the Whisper model on init."""
        with patch("transcriber.WhisperModel") as MockModel:
            from transcriber import Transcriber
            t = Transcriber(model_size="medium", device="cpu", models_dir=str(tmp_path))
            MockModel.assert_called_once()

    def test_transcribe_returns_text(self, sample_wav, mock_whisper_segments, mock_whisper_info, tmp_path):
        """Transcriber should join segments into a single string."""
        with patch("transcriber.WhisperModel") as MockModel:
            MockModel.return_value.transcribe.return_value = (mock_whisper_segments, mock_whisper_info)

            from transcriber import Transcriber
            t = Transcriber(model_size="medium", device="cpu", models_dir=str(tmp_path))
            result = t.transcribe(sample_wav)

            assert "tere see on eesti keele" in result
            assert "ette ütluse test" in result

    def test_transcribe_empty_audio(self, sample_wav, tmp_path):
        """Empty audio should return empty string."""
        with patch("transcriber.WhisperModel") as MockModel:
            MockModel.return_value.transcribe.return_value = ([], MagicMock())

            from transcriber import Transcriber
            t = Transcriber(model_size="medium", device="cpu", models_dir=str(tmp_path))
            result = t.transcribe(sample_wav)
            assert result == ""

    def test_language_set_to_estonian(self, sample_wav, tmp_path):
        """Whisper should be called with language='et'."""
        with patch("transcriber.WhisperModel") as MockModel:
            MockModel.return_value.transcribe.return_value = ([], MagicMock())

            from transcriber import Transcriber
            t = Transcriber(model_size="medium", device="cpu", models_dir=str(tmp_path))
            t.transcribe(sample_wav)

            call_kwargs = MockModel.return_value.transcribe.call_args.kwargs
            assert call_kwargs.get("language") == "et"
