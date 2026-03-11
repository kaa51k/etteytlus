# Iteration Cycle: Build → Install → Validate → Test → Cleanup

## Step 1: BUILD
Agent writes/modifies code following TDD (see tdd-workflow skill).

## Step 2: INSTALL (simulate fresh laptop)
```powershell
.\install.bat
```
Expected: venv created, packages installed, Whisper model downloaded, ffmpeg present.

## Step 3: VALIDATE INSTALL (smoke tests)
```powershell
.\venv\Scripts\python.exe -c "from faster_whisper import WhisperModel; print('OK: Whisper')"
.\venv\Scripts\python.exe -c "import anthropic; print('OK: Anthropic')"
.\venv\Scripts\python.exe -c "import openai; print('OK: OpenAI')"
.\venv\Scripts\python.exe -c "from google import genai; print('OK: Gemini')"
.\venv\Scripts\python.exe -c "import sounddevice; print('OK: Audio')"
.\venv\Scripts\python.exe -c "import flask; print('OK: Flask')"
.\venv\Scripts\python.exe -c "import numpy; print('OK: NumPy')"
```
All should print OK. Any failure = install bug.

## Step 4: RUN TESTS
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v --tb=short -m "not hardware"
```
All green = proceed. Any red = fix before continuing.

## Step 5: LIVE TEST (human in the loop)
```powershell
# Copy config.env.example to config.env, set MODEL and API key
copy config.env.example config.env
# Edit config.env, then:
.\start.bat
```
- Open http://localhost:8080
- Speak Estonian into mic (or play ERR podcast)
- Verify: text appears, corrections applied, copy button works
- Ctrl+C to stop

## Step 6: CLEANUP
```powershell
# Soft (keeps config + ffmpeg):
.\uninstall.bat

# Full (nuclear):
powershell -ExecutionPolicy Bypass -File uninstall.ps1 -Full
```

## Step 7: VERIFY CLEAN STATE
```powershell
# These should NOT exist after cleanup:
Test-Path venv      # Should be False
Test-Path models    # Should be False
Test-Path output    # Should be False
# These SHOULD still exist (soft cleanup):
Test-Path src       # Should be True
Test-Path config.env.example  # Should be True
```

## Step 8: REPEAT
Go to Step 2 for another fresh install cycle.

## Checklist Per Iteration
```
[ ] Code changes (TDD green)
[ ] Cleanup previous install
[ ] Fresh install.bat
[ ] Smoke tests pass
[ ] pytest green
[ ] Live mic test (if relevant changes)
[ ] Cleanup
[ ] git commit + push
```
