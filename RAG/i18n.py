"""Language detection and the few fixed phrases that are localised.

Localised text is taken from the official sentences already published in the knowledge base
(HI-/KN-/TA-FRAUD-01, HI-/KN-/TA-PEN-01) rather than translated here, so wording stays official.
Eligibility detail lines are English for now; only the disclaimer is localised.
"""
from __future__ import annotations

LANGUAGES = ("en", "hi", "kn", "ta")

_BLOCKS = {
    "hi": (0x0900, 0x097F),
    "ta": (0x0B80, 0x0BFF),
    "kn": (0x0C80, 0x0CFF),
}


def detect_language(text: str, default: str = "en") -> str:
    """Language by dominant script. Roman-script text (including Hinglish) counts as English."""
    counts = {lang: 0 for lang in _BLOCKS}
    latin = 0
    for ch in text:
        code = ord(ch)
        for lang, (low, high) in _BLOCKS.items():
            if low <= code <= high:
                counts[lang] += 1
                break
        else:
            if ch.isascii() and ch.isalpha():
                latin += 1
    best = max(counts, key=counts.get)
    if counts[best] and counts[best] >= latin:
        return best
    return "en" if latin else default


# Sentences copied from the KB (HI/KN/TA-FRAUD-01 and HI-PEN-01).
FINAL_DECISION = {
    "en": "This is a preliminary check only. The concerned government department makes the final decision after verification.",
    "hi": "आवेदन करने से मंजूरी पक्की नहीं होती। दस्तावेज़ जांच के बाद संबंधित विभाग ही अंतिम निर्णय लेता है।",
    "kn": "ಪ್ರತಿ ಯೋಜನೆಯ ಅರ್ಜಿಯ ಮೇಲೆ ಸಂಬಂಧಪಟ್ಟ ಸರ್ಕಾರಿ ಇಲಾಖೆಯೇ ಅಂತಿಮ ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ.",
    "ta": "அனைத்து விண்ணப்பங்களிலும் சம்பந்தப்பட்ட அரசுத் துறையே இறுதி முடிவை எடுக்கும்.",
}
ZERO_FEE = {
    "en": "There is no fee for any scheme application or benefit release (₹0). Do not pay any agent or middleman.",
    "hi": "किसी भी योजना के आवेदन फॉर्म के लिए कोई सरकारी शुल्क (₹0) नहीं है। किसी दलाल, एजेंट या बिचौलिए को पैसा न दें।",
    "kn": "ಯಾವುದೇ ಯೋಜನೆಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಅಥವಾ ಹಣ ಬಿಡುಗಡೆ ಮಾಡಲು ಶುಲ್ಕ (₹0) ಇಲ್ಲ. ಮಧ್ಯವರ್ತಿಗಳಿಗೆ ಅಥವಾ ಏಜೆಂಟ್‌ಗಳಿಗೆ ಹಣ ನೀಡಬೇಡಿ.",
    "ta": "எந்த நலத்திட்ட விண்ணப்பத்திற்கும் அல்லது உதவித்தொகை விடுவிப்பதற்கும் கட்டணம் (₹0) கிடையாது. இடைத்தரகர்கள் அல்லது ஏஜென்டுகளுக்கு பணம் கொடுக்க வேண்டாம்.",
}
FRAUD_REPORT = {
    "en": "Report it immediately to the fraud_desk (MitraSeva Portal > Report Fraud, or a District Collectorate Vigilance Counter). Reporting never delays your genuine application.",
    "hi": "यदि कोई व्यक्ति पैसे या OTP मांगे, तो तुरंत fraud_desk पर शिकायत दर्ज कराएँ।",
    "kn": "ಯಾರಾದರೂ ಹಣ ಅಥವಾ OTP ಕೇಳಿದರೆ ತಕ್ಷಣ fraud_desk ಗೆ ದೂರು ನೀಡಿ.",
    "ta": "யாராவது பணம் அல்லது OTP கேட்டால் உடனடியாக fraud_desk-இல் புகார் அளியுங்கள்.",
}
NEVER_SHARE_OTP = {
    "en": "Never share your OTP, bank PIN or password with anyone. No government official will ask for them, and no genuine caller can get your application approved.",
    "hi": "सरकारी अधिकारी कभी फोन पर OTP, बैंक PIN या पैसे नहीं मांगते। अपना OTP किसी के भी साथ साझा न करें।",
    "kn": "ನಿಮ್ಮ OTP, ಬ್ಯಾಂಕ್ PIN ಅಥವಾ ಪಾಸ್‌ವರ್ಡ್ ಅನ್ನು ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",
    "ta": "உங்கள் OTP, வங்கி PIN அல்லது கடவுச்சொல்லை யாரிடமும் பகிர வேண்டாம்.",
}
