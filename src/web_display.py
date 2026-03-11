"""Flask web display showing live corrected text."""

import json
import threading
from flask import Flask, render_template, jsonify


class WebDisplay:
    """Simple Flask server showing live pipeline status and corrected text."""

    def __init__(self, model_name: str, port: int = 8080):
        self.model_name = model_name
        self.port = port
        self.chunks = []  # List of {"number": int, "raw": str, "corrected": str, "status": str}
        self.full_text = ""
        self.mic_level = 0.0
        self.is_live = False
        self._lock = threading.Lock()

        self.app = Flask(__name__, template_folder="../templates")
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/")
        def index():
            return render_template("display.html", model=self.model_name)

        @self.app.route("/api/status")
        def status():
            with self._lock:
                return jsonify({
                    "model": self.model_name,
                    "is_live": self.is_live,
                    "mic_level": self.mic_level,
                    "chunk_count": len(self.chunks),
                    "full_text": self.full_text,
                    "chunks": self.chunks[-5:],  # Last 5 for status display
                })

    def update_chunk(self, number: int, raw: str = "", corrected: str = "", status: str = "processing"):
        """Update or add a chunk's status."""
        with self._lock:
            # Find existing or create new
            existing = next((c for c in self.chunks if c["number"] == number), None)
            if existing:
                if raw:
                    existing["raw"] = raw
                if corrected:
                    existing["corrected"] = corrected
                existing["status"] = status
            else:
                self.chunks.append({
                    "number": number,
                    "raw": raw,
                    "corrected": corrected,
                    "status": status,
                })

            # Rebuild full text from all corrected chunks
            self.full_text = "\n\n".join(
                c["corrected"] for c in sorted(self.chunks, key=lambda x: x["number"])
                if c["corrected"]
            )

    def set_mic_level(self, level: float):
        with self._lock:
            self.mic_level = level

    def set_live(self, is_live: bool):
        with self._lock:
            self.is_live = is_live

    def start(self):
        """Start Flask in a background thread."""
        self.set_live(True)
        thread = threading.Thread(
            target=lambda: self.app.run(host="0.0.0.0", port=self.port, debug=False, use_reloader=False),
            daemon=True,
        )
        thread.start()
        print(f"  [web] Display running at http://localhost:{self.port}")
