import re

class ICTCaptionCleaner:
    def __init__(self):
        # Dictionary mapping YouTube ASR mistakes to exact ICT terminology
        self.corrections = {
            r"\bthere value gap\b": "Fair Value Gap (FVG)",
            r"\bfair value got\b": "Fair Value Gap (FVG)",
            r"\bolder block\b": "Order Block (OB)",
            r"\border box\b": "Order Block (OB)",
            r"\bjudas wing\b": "Judas Swing",
            r"\bjudas string\b": "Judas Swing",
            r"\bbalanced price\b": "Balanced Price Range (BPR)",
            r"\bmidnight open\b": "Midnight Open (00:00 EST)",
            r"\bequal highs\b": "Relative Equal Highs (EQH)",
            r"\bequal lows\b": "Relative Equal Lows (EQL)",
            r"\bliquidity sweep\b": "Liquidity Sweep",
            r"\bmarket structure shift\b": "Market Structure Shift (MSS)",
            r"\bsilver bullet\b": "Silver Bullet"
        }

    def clean_text(self, text: str) -> str:
        """Applies regex replacements to fix transcription errors."""
        cleaned = text.lower()
        for pattern, replacement in self.corrections.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Capitalize sentences for better LLM comprehension later
        return cleaned.capitalize()