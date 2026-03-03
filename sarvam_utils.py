# sarvam_utils.py
"""
Sarvam AI wrappers for STT (Saaras v3) and Translation (Mayura v1).
Replace SARVAM_KEY with your real subscription key before running.
"""

SARVAM_KEY = "sk_aqm3d74w_15Z1tgVdVhrLR6CVjS8tpIiq"  # ← MUST CHANGE


def _get_client():
    try:
        from sarvamai import SarvamAI
        return SarvamAI(api_subscription_key=SARVAM_KEY)
    except ImportError:
        return None


def stt_from_file(wav_path: str, lang: str = "en-IN") -> str:
    """Transcribe a WAV file using Sarvam Saaras v3."""
    client = _get_client()
    if client is None:
        return "[Mock STT] sarvamai not installed – pip install sarvamai"
    try:
        with open(wav_path, "rb") as f:
            r = client.speech_to_text.transcribe(
                file=f,
                model="saaras:v3",
                mode="transcribe",
                language_code=lang,
            )
        return r.get("text", "")
    except Exception as e:
        return f"STT failed: {e}"


def translate_to_hindi(text: str) -> str:
    """Translate English text to Hindi using Sarvam Mayura v1."""
    client = _get_client()
    if client is None:
        return f"[Mock Translation – install sarvamai]\n{text}"
    try:
        r = client.text.translate(
            input=text,
            source_language_code="en-IN",
            target_language_code="hi-IN",
            model="mayura:v1",
        )
        return r.get("translated", text)
    except Exception as e:
        return f"Translate failed: {e}"
