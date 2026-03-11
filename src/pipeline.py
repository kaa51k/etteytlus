"""eesti.ai — e-etteütlus pipeline orchestrator."""

import os
import sys
import time
import signal
import threading
from pathlib import Path
from dotenv import dotenv_values

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_capture import AudioCapture
from transcriber import Transcriber
from corrector import Corrector
from web_display import WebDisplay


def load_config() -> dict:
    """Load configuration from config.env."""
    project_dir = Path(__file__).parent.parent
    config_path = project_dir / "config.env"

    if not config_path.exists():
        print("  ERROR: config.env not found!")
        print("  Copy config.env.example to config.env and edit it.")
        sys.exit(1)

    config = dotenv_values(config_path)

    # Validate
    model = config.get("MODEL", "").lower()
    if model not in ("claude", "gpt", "grok", "gemini"):
        print(f"  ERROR: Invalid MODEL='{model}' in config.env")
        print("  Use one of: claude, gpt, grok, gemini")
        sys.exit(1)

    # Get the right API key
    key_map = {
        "claude": "ANTHROPIC_API_KEY",
        "gpt": "OPENAI_API_KEY",
        "grok": "XAI_API_KEY",
        "gemini": "GOOGLE_API_KEY",
    }
    api_key = config.get(key_map[model], "")
    if not api_key or "YOUR_" in api_key:
        print(f"  ERROR: {key_map[model]} not set in config.env")
        sys.exit(1)

    return {
        "model": model,
        "api_key": api_key,
        "chunk_duration": int(config.get("CHUNK_DURATION", 30)),
        "overlap": int(config.get("OVERLAP_DURATION", 5)),
        "whisper_model": config.get("WHISPER_MODEL", "medium"),
        "whisper_device": config.get("WHISPER_DEVICE", "auto"),
        "web_port": int(config.get("WEB_PORT", 8080)),
    }


def main():
    print()
    print("  ========================================")
    print("    eesti.ai — e-etteütlus pipeline")
    print("  ========================================")
    print()

    # Load config
    config = load_config()
    print(f"  Model:   {config['model']}")
    print(f"  Whisper: {config['whisper_model']} on {config['whisper_device']}")
    print()

    project_dir = Path(__file__).parent.parent
    output_dir = project_dir / "output"
    chunks_dir = output_dir / "chunks"
    transcriptions_dir = output_dir / "transcriptions"
    corrected_dir = output_dir / "corrected"

    for d in [chunks_dir, transcriptions_dir, corrected_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Initialize components
    print("  Initializing components...")

    web = WebDisplay(model_name=config["model"], port=config["web_port"])
    web.start()

    transcriber = Transcriber(
        model_size=config["whisper_model"],
        device=config["whisper_device"],
        models_dir=str(project_dir / "models"),
    )

    corrector_client = Corrector(model=config["model"], api_key=config["api_key"])

    audio = AudioCapture(
        chunk_duration=config["chunk_duration"],
        overlap=config["overlap"],
        output_dir=str(chunks_dir),
    )

    # Track previous chunk for continuity
    previous_tail = ""
    processing_lock = threading.Lock()

    def process_chunk(chunk_path: str, chunk_number: int):
        """Called when a new audio chunk is ready."""
        nonlocal previous_tail

        with processing_lock:
            web.update_chunk(chunk_number, status="transcribing")

            # Step 1: Transcribe
            print(f"\n  --- Chunk {chunk_number} ---")
            raw_text = transcriber.transcribe(chunk_path)

            # Save raw transcription
            raw_path = transcriptions_dir / f"chunk_{chunk_number:04d}.txt"
            raw_path.write_text(raw_text, encoding="utf-8")

            web.update_chunk(chunk_number, raw=raw_text, status="correcting")

            if not raw_text.strip():
                print(f"  [pipeline] Chunk {chunk_number}: empty transcription, skipping correction")
                web.update_chunk(chunk_number, corrected="", status="done")
                return

            # Step 2: Correct with LLM
            corrected = corrector_client.correct(raw_text, previous_tail)

            # Save corrected text
            corrected_path = corrected_dir / f"chunk_{chunk_number:04d}.txt"
            corrected_path.write_text(corrected, encoding="utf-8")

            web.update_chunk(chunk_number, corrected=corrected, status="done")

            # Keep tail for next chunk's context
            words = corrected.split()
            previous_tail = " ".join(words[-50:]) if len(words) > 50 else corrected

            print(f"  [pipeline] Chunk {chunk_number}: done ({len(corrected)} chars)")

    audio.on_chunk_ready(process_chunk)

    # Periodic mic level update
    def update_mic_level():
        while True:
            level = audio.get_mic_level()
            web.set_mic_level(level)
            time.sleep(0.5)

    mic_thread = threading.Thread(target=update_mic_level, daemon=True)
    mic_thread.start()

    # Start recording
    print()
    print(f"  🟢 LIVE — listening on microphone")
    print(f"  📺 Open http://localhost:{config['web_port']} in your browser")
    print(f"  Press Ctrl+C to stop")
    print()

    audio.start()

    # Wait for Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Stopping...")
        audio.stop()
        web.set_live(False)

        # Save final combined text
        final_path = output_dir / "final_text.txt"
        final_path.write_text(web.full_text, encoding="utf-8")
        print(f"  Final text saved to: {final_path}")
        print(f"  Total chunks: {len(web.chunks)}")
        print()
        print("  Done! Copy the text from the browser or from output/final_text.txt")


if __name__ == "__main__":
    main()
