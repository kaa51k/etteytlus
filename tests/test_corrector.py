"""Tests for LLM corrector module."""

import pytest
from unittest.mock import MagicMock, patch


class TestCorrectorInit:
    """Test corrector initialization for all 4 models."""

    def test_claude_init(self):
        """Claude corrector should initialize with Anthropic client."""
        with patch("corrector.anthropic") as mock_anthropic:
            from corrector import Corrector
            c = Corrector("claude", "sk-ant-test")
            assert c.model == "claude"
            mock_anthropic.Anthropic.assert_called_once_with(api_key="sk-ant-test")

    def test_gpt_init(self):
        """GPT corrector should initialize with OpenAI client."""
        with patch("corrector.openai") as mock_openai:
            from corrector import Corrector
            c = Corrector("gpt", "sk-test")
            assert c.model == "gpt"
            mock_openai.OpenAI.assert_called_once_with(api_key="sk-test")

    def test_grok_init(self):
        """Grok corrector should use OpenAI client with xAI base_url."""
        with patch("corrector.openai") as mock_openai:
            from corrector import Corrector
            c = Corrector("grok", "xai-test")
            assert c.model == "grok"
            mock_openai.OpenAI.assert_called_once_with(
                api_key="xai-test",
                base_url="https://api.x.ai/v1",
            )

    def test_gemini_init(self):
        """Gemini corrector should initialize with Google genai client."""
        with patch("corrector.genai") as mock_genai:
            from corrector import Corrector
            c = Corrector("gemini", "AIza-test")
            assert c.model == "gemini"
            mock_genai.Client.assert_called_once_with(api_key="AIza-test")

    def test_invalid_model_raises(self):
        """Unknown model name should raise ValueError."""
        from corrector import Corrector
        with pytest.raises(ValueError, match="Unknown model"):
            Corrector("bard", "some-key")


class TestCorrectorCorrect:
    """Test the correction method for each model."""

    def test_claude_correction(self, sample_transcription, sample_corrected):
        """Claude should return corrected text from API response."""
        with patch("corrector.anthropic") as mock_anthropic:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text=sample_corrected)]
            mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_response

            from corrector import Corrector
            c = Corrector("claude", "sk-ant-test")
            result = c.correct(sample_transcription)
            assert result == sample_corrected

    def test_gpt_correction(self, sample_transcription, sample_corrected):
        """GPT should return corrected text from API response."""
        with patch("corrector.openai") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content=sample_corrected))]
            mock_openai.OpenAI.return_value.chat.completions.create.return_value = mock_response

            from corrector import Corrector
            c = Corrector("gpt", "sk-test")
            result = c.correct(sample_transcription)
            assert result == sample_corrected

    def test_error_fallback_returns_raw(self, sample_transcription):
        """On API error, corrector should return the raw transcription."""
        with patch("corrector.anthropic") as mock_anthropic:
            mock_anthropic.Anthropic.return_value.messages.create.side_effect = Exception("API down")

            from corrector import Corrector
            c = Corrector("claude", "sk-ant-test")
            result = c.correct(sample_transcription)
            assert result == sample_transcription

    def test_previous_tail_passed_to_prompt(self, sample_transcription):
        """Previous tail should be included in the prompt sent to the API."""
        with patch("corrector.anthropic") as mock_anthropic:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="corrected")]
            mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_response

            from corrector import Corrector
            c = Corrector("claude", "sk-ant-test")
            c.correct(sample_transcription, previous_tail="eelmine lause")

            call_args = mock_anthropic.Anthropic.return_value.messages.create.call_args
            prompt_text = call_args.kwargs["messages"][0]["content"]
            assert "eelmine lause" in prompt_text
