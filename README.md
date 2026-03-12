# etteytlus — e-etteütlus AI Competition

Four AI models compete in the Estonian national dictation competition ([e-etteütlus](https://etteytlus.err.ee/)).

Each laptop independently listens, transcribes, and corrects — producing dictation-quality Estonian text in near-real-time.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Windows 11 Laptop                              │
│                                                 │
│  Laptop Mic ──▶ Whisper (local) ──▶ LLM API    │
│  (radio audio)  (faster-whisper)    (correction)│
│                                          │      │
│                         http://localhost:8080    │
│                         Live corrected text      │
└─────────────────────────────────────────────────┘
```

| Laptop | Model  | API Provider |
|--------|--------|--------------|
| 1      | Claude | Anthropic    |
| 2      | GPT-4o | OpenAI       |
| 3      | Grok-3 | xAI          |
| 4      | Gemini | Google       |

## Quick Start (Windows 11)

You'll repeat these steps on all 4 laptops. Each laptop gets **identical code** — only the config file differs.

> 💡 **Tip:** Download the ZIP (or clone) once, copy the extracted folder to a USB stick, then copy it to each laptop. Each laptop only needs its own `config.env`.

### Prerequisites

- **Windows 10 or 11** (64-bit)
- **Internet connection** (needed for LLM API calls and first-time downloads)
- **Microphone** (built-in laptop mic is fine)
- **GPU is optional** — NVIDIA GPU with CUDA speeds up Whisper, but CPU works fine

That's it. **Git is not required.** Python and ffmpeg are installed automatically by `install.bat`.

### Step 1 — Get the Code

**Option A — Download ZIP** (recommended):
1. Go to https://github.com/kaa51k/etteytlus
2. Click the green **Code** button → **Download ZIP**
3. Extract the ZIP to a folder (e.g. `C:\etteytlus`)

**Option B — Git clone** (if you have Git):
```
git clone https://github.com/kaa51k/etteytlus.git
cd etteytlus
```

### Step 2 — Install — double-click `install.bat`

Handles everything: Python venv, packages, ffmpeg, Whisper model download.

### Step 3 — Configure

```
copy config.env.example config.env
```

Edit `config.env` — set `MODEL=` and the matching API key.

### Step 4 — Run — double-click `start.bat`

Open http://localhost:8080 in your browser. Speak Estonian near the mic.

### Step 5 — Reset — double-click `uninstall.bat`

Removes venv, models, output. Keeps your config and source code.
For a full reset: `powershell -File uninstall.ps1 -Full`

## Setting Up 4 Laptops

Each laptop gets identical code. Only `config.env` differs:

| Laptop | MODEL=   | API Key Needed       |
|--------|----------|----------------------|
| 1      | `claude` | `ANTHROPIC_API_KEY`  |
| 2      | `gpt`    | `OPENAI_API_KEY`     |
| 3      | `grok`   | `XAI_API_KEY`        |
| 4      | `gemini` | `GOOGLE_API_KEY`     |

## Competition Day

1. Place laptops near the radio
2. `start.bat` on each, ~1 min before broadcast
3. Verify live indicator + mic signal in browser
4. Hands off during broadcast (~15–20 min)
5. Click **Copy Full Text** on each
6. Paste into https://etteytlus.err.ee/vasta/
7. Screenshot each submission

## Requirements

- Windows 10/11 (64-bit)
- Python 3.10–3.12 (auto-installed by `install.bat` if missing)
- Internet connection (for LLM API calls)
- Microphone (built-in or USB)
- GPU optional (NVIDIA + CUDA speeds up Whisper)

## Development

Developed using [Google Antigravity](https://antigravity.google/) with autonomous multi-agent TDD.

```bash
# Run tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## API Keys

| Model  | Console                     | Approx. cost |
|--------|-----------------------------|--------------| 
| Claude | console.anthropic.com       | ~$0.10       |
| GPT    | platform.openai.com         | ~$0.15       |
| Grok   | console.x.ai               | Free tier    |
| Gemini | aistudio.google.com         | Free tier    |

## Fallback

Audio chunks are saved locally. If live correction fails, re-run Whisper post-broadcast and submit same day.

## License

MIT — see [LICENSE](LICENSE)

---

Built by [Priit Kaasik](https://github.com/kaa51k) for the [eesti.ai](https://eesti.ai) e-etteütlus AI competition 🇪🇪
