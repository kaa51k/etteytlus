"""Tests for prompt formatting."""

from prompt import format_prompt, CORRECTION_PROMPT


class TestCorrectionPrompt:
    """Test the shared correction prompt template."""

    def test_prompt_contains_rules(self):
        """Prompt must include Estonian correction rules."""
        assert "õigekirja" in CORRECTION_PROMPT
        assert "ÕS" in CORRECTION_PROMPT
        assert "suurtähte" in CORRECTION_PROMPT

    def test_prompt_has_placeholder(self):
        """Prompt must have {transcription} placeholder."""
        assert "{transcription}" in CORRECTION_PROMPT


class TestFormatPrompt:
    """Test prompt formatting with transcription input."""

    def test_basic_formatting(self, sample_transcription):
        """Transcription text should be inserted into prompt."""
        result = format_prompt(sample_transcription)
        assert sample_transcription in result
        assert "{transcription}" not in result

    def test_without_previous_tail(self, sample_transcription):
        """Without previous_tail, no continuity section should appear."""
        result = format_prompt(sample_transcription)
        assert "Eelmise" not in result

    def test_with_previous_tail(self, sample_transcription):
        """With previous_tail, continuity context should be appended."""
        tail = "Eelmine lause oli siin."
        result = format_prompt(sample_transcription, previous_tail=tail)
        assert tail in result
        assert "Eelmise" in result

    def test_empty_previous_tail_ignored(self, sample_transcription):
        """Empty string previous_tail should behave like no tail."""
        result = format_prompt(sample_transcription, previous_tail="")
        assert "Eelmise" not in result
