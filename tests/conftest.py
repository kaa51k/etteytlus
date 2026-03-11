"""Shared test fixtures for etteytlus."""

import os
import sys
import pytest
import numpy as np

# Add src to path so tests can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def sample_audio():
    """Generate a 3-second synthetic audio signal (16kHz mono float32)."""
    sample_rate = 16000
    duration = 3.0
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    # 440Hz sine wave at 50% amplitude
    audio = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    return audio, sample_rate


@pytest.fixture
def sample_wav(tmp_path, sample_audio):
    """Write sample audio to a WAV file and return the path."""
    from scipy.io import wavfile

    audio, sr = sample_audio
    wav_path = tmp_path / "test_audio.wav"
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(str(wav_path), sr, audio_int16)
    return str(wav_path)


@pytest.fixture
def sample_transcription():
    """Sample raw Whisper output (deliberately imperfect Estonian)."""
    return "tere see on eesti keele ette ütluse test me räägime täna ilmast"


@pytest.fixture
def sample_corrected():
    """Expected corrected output."""
    return "Tere, see on eesti keele etteütluse test. Me räägime täna ilmast."


@pytest.fixture
def mock_whisper_segments():
    """Mock Whisper segment objects."""

    class MockSegment:
        def __init__(self, text):
            self.text = text

    return [
        MockSegment("tere see on eesti keele"),
        MockSegment("ette ütluse test"),
    ]


@pytest.fixture
def mock_whisper_info():
    """Mock Whisper transcription info."""

    class MockInfo:
        language = "et"
        language_probability = 0.98

    return MockInfo()


@pytest.fixture
def config_env(tmp_path):
    """Create a temporary config.env file."""
    config = tmp_path / "config.env"
    config.write_text(
        "MODEL=claude\n"
        "ANTHROPIC_API_KEY=sk-ant-test-key-12345\n"
        "OPENAI_API_KEY=sk-test-key\n"
        "XAI_API_KEY=xai-test-key\n"
        "GOOGLE_API_KEY=AIza-test-key\n"
        "CHUNK_DURATION=30\n"
        "OVERLAP_DURATION=5\n"
        "WHISPER_MODEL=medium\n"
        "WHISPER_DEVICE=cpu\n"
        "WEB_PORT=8080\n"
    )
    return str(config)
