"""Tests for LLM corrector module."""

import pytest
from unittest.mock import MagicMock, patch


class TestCorrectorInit:
    """Test corrector initialization for all 4 models."""

    def test_claude_init(self):
        """Claude corrector should initialize with Anthropic client."""
        with patch("anthropic.Anthropic") as MockAnthropic:
            from corrector import Corrector
            c = Corrector("claude", "sk-ant-test")
            assert c.model == "claude"
            MockAnthropic.assert_called_once_with(api_key="sk-ant-test")

    def test_gpt_init(self):
        """GPT corrector should initialize with OpenAI client."""
        with patch("openai.OpenAI") as MockOpenAI:
            from corrector import Corrector
            c = Corrector("gpt", "sk-test")
            assert c.model == "gpt"
            MockOpenAI.assert_called_once_with(api_key="sk-test")

    def test_grok_init(self):
        """Grok corrector should use OpenAI client with xAI base_url."""
        with patch("openai.OpenAI") as MockOpenAI:
            from corrector import Corrector
            c = Corrector("grok", "xai-test")
            assert c.model == "grok"
            MockOpenAI.assert_called_once_with(
                api_key="xai-test",
                base_url="https://api.x.ai/v1",
            )

    def test_gemini_init(self):
        """Gemini corrector should initialize with Google genai client."""
        with patch("google.genai.Client") as MockClient:
            from corrector import Corrector
            c = Corrector("gemini", "AIza-test")
            assert c.model == "gemini"
            MockClient.assert_called_once_with(api_key="AIza-test")

    def test_invalid_model_raises(self):
        """Unknown model name should raise ValueError."""
        from corrector import Corrector
        with pytest.raises(ValueError, match="Unknown model"):
            Corrector("bard", "some-key")


class TestCorrectorCorrect:
    """Test the correction method for each model."""

    def test_claude_correction(self, sample_transcription, sample_corrected):
        """Claude should return corrected text from API response."""
        with patch("anthropic.Anthropic") as MockAnthropic:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text=sample_corrected)]
            MockAnthropic.return_value.messages.create.return_value = mock_response

            from corrector import Corrector
            c = Corrector("claude", "sk-ant-test")
            result = c.correct(sample_transcription)
            assert result == sample_corrected

    def test_gpt_correction(self, sample_transcription, sample_corrected):
        """GPT should return corrected text from API response."""
        with patch("openai.OpenAI") as MockOpenAI:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content=sample_corrected))]
            MockOpenAI.return_value.chat.completions.create.return_value = mock_response

            from corrector import Corrector
            c = Corrector("gpt", "sk-test")
            result = c.correct(sample_transcription)
            assert result == sample_corrected

    def test_error_fallback_returns_raw(self, sample_transcription):
        """On API error, corrector should return the raw transcription."""
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value.messages.create.side_effect = Exception("API down")

            from corrector import Corrector
            c = Corrector("claude", "sk-ant-test")
            result = c.correct(sample_transcription)
            assert result == sample_transcription

    def test_previous_tail_passed_to_prompt(self, sample_transcription):
        """Previous tail should be included in the prompt sent to the API."""
        with patch("anthropic.Anthropic") as MockAnthropic:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="corrected")]
            MockAnthropic.return_value.messages.create.return_value = mock_response

            from corrector import Corrector
            c = Corrector("claude", "sk-ant-test")
            c.correct(sample_transcription, previous_tail="eelmine lause")

            call_args = MockAnthropic.return_value.messages.create.call_args
            prompt_text = call_args.kwargs["messages"][0]["content"]
            assert "eelmine lause" in prompt_text
