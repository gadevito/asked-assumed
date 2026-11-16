import re
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
def english(t):
    t = re.sub(r'`[^`]*`|https?://\S+|\*\*', ' ', t)
    letters = [c for c in t if c.isalpha()]
    if not letters or sum(not c.isascii() for c in letters) / len(letters) > 0.02: return False
    try: return detect(t) == 'en'
    except Exception: return False
