"""Shared correction prompt for all LLM models."""

CORRECTION_PROMPT = """Sa osaled eesti keele etteütluses. Sinu ülesanne on parandada automaatse kõnetuvastuse (Whisper) toorest väljundit, et saada keeleliselt korrektne etteütluse tekst.

Reeglid:
- Paranda kõik õigekirja-, grammatika- ja kirjavahemärgistuse vead.
- Ära lisa ega eemalda sisu — paranda ainult keelt ja vormistust.
- Järgi eesti keele õigekirjareegleid (ÕS).
- Kasuta korrektset suurtähte lausete alguses ja pärisnimedes.
- Ühenda kõnetuvastuse katkendlikud laused loogilisteks lõikudeks.
- Väljasta ainult parandatud tekst, mitte midagi muud.

Kõnetuvastuse toorväljund:
{transcription}"""


def format_prompt(transcription: str, previous_tail: str = "") -> str:
    """Format the correction prompt with transcription text.

    Args:
        transcription: Raw Whisper output text.
        previous_tail: Last ~50 words of previous corrected chunk (for continuity).

    Returns:
        Formatted prompt string.
    """
    prompt = CORRECTION_PROMPT.format(transcription=transcription)

    if previous_tail:
        prompt += f"\n\nEelmise lõigu viimased laused (kontekstiks, ära korda neid):\n{previous_tail}"

    return prompt
