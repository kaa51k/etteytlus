# TDD Workflow for etteytlus

## Test-First Rules
1. Write the test BEFORE the implementation
2. Run the test — it MUST fail (red)
3. Write minimal code to pass (green)
4. Refactor while keeping green
5. Commit after each green cycle

## Test Organization
```
tests/
├── conftest.py              # Shared fixtures
├── test_audio_capture.py    # Mic recording, chunks, overlap
├── test_transcriber.py      # Whisper model, transcription
├── test_corrector.py        # LLM clients, prompt, correction
├── test_prompt.py           # Prompt formatting
├── test_pipeline.py         # End-to-end orchestration
└── test_web_display.py      # Flask routes, API, text updates
```

## Mocking Strategy
- `sounddevice`: mock `sd.rec()` and `sd.wait()` with synthetic numpy arrays
- `faster-whisper`: mock `WhisperModel` to return canned segments
- `anthropic`: mock `client.messages.create()` returning corrected text
- `openai`: mock `client.chat.completions.create()` for GPT and Grok
- `google-genai`: mock `client.models.generate_content()` for Gemini
- File I/O: use `tmp_path` pytest fixture for all output directories

## Markers
Use pytest markers to separate hardware-dependent tests:
```python
import pytest

@pytest.mark.hardware
def test_real_mic_capture():
    """Only runs locally with a real microphone."""
    ...
```

## Running
```bash
# All tests (excluding hardware):
python -m pytest tests/ -v --tb=short -m "not hardware"

# Single module:
python -m pytest tests/test_corrector.py -v

# With coverage:
python -m pytest tests/ --cov=src --cov-report=term-missing

# Stop on first failure:
python -m pytest tests/ -v -x
```

## Coverage Targets
- src/corrector.py: 90%+
- src/transcriber.py: 90%+
- src/prompt.py: 100%
- src/pipeline.py: 80%+
- src/audio_capture.py: 70%+ (hardware-dependent parts excluded)
- src/web_display.py: 80%+
