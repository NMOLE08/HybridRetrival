"""Conservative text normalization for identifier parsing."""
import re

# All replacements are one code point, preserving original string offsets.
_DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d"
_TABLE = str.maketrans({c: "-" for c in _DASHES})


def normalize_dashes(text):
    return text.translate(_TABLE)


def normalize_text(text):
    return re.sub(r"\s+", " ", normalize_dashes(text)).strip().casefold()
