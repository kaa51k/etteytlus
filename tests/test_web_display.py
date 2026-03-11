"""Tests for Flask web display."""

import json
from unittest.mock import patch


class TestWebDisplay:
    """Test the Flask web display server."""

    def _make_display(self):
        from web_display import WebDisplay
        display = WebDisplay(model_name="claude", port=8099)
        return display

    def test_index_returns_html(self):
        """GET / should return HTML containing model name."""
        display = self._make_display()
        with display.app.test_client() as client:
            resp = client.get("/")
            assert resp.status_code == 200
            assert b"claude" in resp.data

    def test_status_returns_json(self):
        """GET /api/status should return valid JSON."""
        display = self._make_display()
        with display.app.test_client() as client:
            resp = client.get("/api/status")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert data["model"] == "claude"
            assert data["chunk_count"] == 0
            assert data["full_text"] == ""

    def test_chunk_update_appears_in_status(self):
        """After updating a chunk, status should reflect it."""
        display = self._make_display()
        display.update_chunk(1, raw="raw text", corrected="Corrected text.", status="done")

        with display.app.test_client() as client:
            data = json.loads(client.get("/api/status").data)
            assert data["chunk_count"] == 1
            assert "Corrected text." in data["full_text"]

    def test_multiple_chunks_concatenated(self):
        """Full text should be all corrected chunks joined."""
        display = self._make_display()
        display.update_chunk(1, corrected="First chunk.", status="done")
        display.update_chunk(2, corrected="Second chunk.", status="done")

        with display.app.test_client() as client:
            data = json.loads(client.get("/api/status").data)
            assert "First chunk." in data["full_text"]
            assert "Second chunk." in data["full_text"]
            assert data["chunk_count"] == 2

    def test_mic_level_update(self):
        """Mic level should be reflected in status."""
        display = self._make_display()
        display.set_mic_level(0.75)

        with display.app.test_client() as client:
            data = json.loads(client.get("/api/status").data)
            assert data["mic_level"] == 0.75
