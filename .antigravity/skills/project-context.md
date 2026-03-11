# Project: etteytlus (e-etteütlus AI Competition)

## What This Is
A pipeline for the Estonian national dictation competition (e-etteütlus).
4 laptops, each running one AI model (Claude, GPT, Grok, Gemini), independently:
1. Capture audio from laptop mic (radio playing nearby)
2. Transcribe with Whisper (faster-whisper, local, Estonian)
3. Correct grammar/spelling via LLM API
4. Display corrected text in browser with copy button

## Key Constraints
- Target: Windows 11 laptops
- Operator skill level: non-technical (one-click install + start)
- All 4 laptops run identical code, differ only in config.env (MODEL + API key)
- Whisper runs locally (no cloud STT dependency)
- Audio source: laptop mic listening to physical radio

## Tech Stack
- Python 3.11 in venv
- faster-whisper (CTranslate2 backend)
- sounddevice + numpy + scipy for mic capture
- anthropic, openai, google-genai for LLM APIs
- Flask for local web display
- PowerShell scripts for install/uninstall

## Architecture
```
audio_capture.py → WAV chunks → transcriber.py → raw text → corrector.py → clean text → web_display.py
```

Each chunk is 30s with 5s overlap. The corrector receives the tail of the previous corrected chunk for continuity.

## Estonian Language Notes
- The correction prompt is in Estonian (see src/prompt.py)
- Whisper language parameter: "et"
- Test with any Estonian audio (ERR podcasts, vikerraadio.err.ee)
- Key test phrase: "Tere, see on eesti keele etteütluse test."

## API Models
| Provider   | Model ID                    | Client Library |
|------------|-----------------------------|----------------|
| Anthropic  | claude-sonnet-4-20250514    | anthropic      |
| OpenAI     | gpt-4o                      | openai         |
| xAI        | grok-3                      | openai (custom base_url) |
| Google     | gemini-2.0-flash            | google-genai   |
