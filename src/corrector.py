"""LLM-based text correction for Estonian dictation."""

import os
from prompt import format_prompt


class Corrector:
    """Sends raw transcription to an LLM API for grammar/spelling correction."""

    def __init__(self, model: str, api_key: str):
        """
        Args:
            model: One of 'claude', 'gpt', 'grok', 'gemini'.
            api_key: The API key for the chosen model.
        """
        self.model = model.lower()
        self.api_key = api_key
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize the appropriate API client."""
        if self.model == "claude":
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
            self._model_id = "claude-sonnet-4-20250514"

        elif self.model == "gpt":
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)
            self._model_id = "gpt-4o"

        elif self.model == "grok":
            import openai
            self._client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
            )
            self._model_id = "grok-3"

        elif self.model == "gemini":
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._model_id = "gemini-2.0-flash"

        else:
            raise ValueError(f"Unknown model: {self.model}. Use: claude, gpt, grok, gemini")

        print(f"  [corrector] Initialized {self.model} ({self._model_id})")

    def correct(self, transcription: str, previous_tail: str = "") -> str:
        """Send transcription to LLM for correction.

        Args:
            transcription: Raw Whisper output.
            previous_tail: End of previous corrected chunk for continuity.

        Returns:
            Corrected Estonian text.
        """
        prompt = format_prompt(transcription, previous_tail)

        try:
            if self.model == "claude":
                return self._correct_claude(prompt)
            elif self.model in ("gpt", "grok"):
                return self._correct_openai(prompt)
            elif self.model == "gemini":
                return self._correct_gemini(prompt)
        except Exception as e:
            print(f"  [corrector] ERROR: {e}")
            return transcription  # Fallback: return raw text

    def _correct_claude(self, prompt: str) -> str:
        response = self._client.messages.create(
            model=self._model_id,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        print(f"  [corrector] Claude returned {len(text)} chars")
        return text

    def _correct_openai(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.1,
        )
        text = response.choices[0].message.content.strip()
        print(f"  [corrector] {self.model} returned {len(text)} chars")
        return text

    def _correct_gemini(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model_id,
            contents=prompt,
        )
        text = response.text.strip()
        print(f"  [corrector] Gemini returned {len(text)} chars")
        return text
