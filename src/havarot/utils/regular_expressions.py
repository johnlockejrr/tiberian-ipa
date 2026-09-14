"""Regular expressions used throughout havarot (ported from havarotjs)."""

from __future__ import annotations

import re

# Positive lookahead to split a word into clusters
cluster_split_group = re.compile(
    r"(?=[\u05BE\u05C3\u05C6\u05D0-\u05F2\u2000-\u206F\u2E00-\u2E7F"
    r"'!\"#$%&()*+,\-./:;<=>?@\[\]^_`{|}~])"
)

# Deprecated alias
cluster_slit_group = cluster_split_group

consonants = re.compile(r"[\u05D0-\u05F2]")
dagesh = re.compile(r"[\u05BC]")
heb_chars = re.compile(r"[\u0590-\u05FF\uFB1D-\uFB4F]")
ligatures = re.compile(r"[\u05C1-\u05C2]")
meteg = re.compile(r"\u05BD")
punctuation = re.compile(r"[\u05BE\u05C0\u05C3\u05C6]")
punctuation_capture_group = re.compile(r"([\u05BE\u05C0\u05C3\u05C6])")
rafe = re.compile(r"\u05BF")

# Split text into word groups (maqqef / hyphen / whitespace)
split_group = re.compile(
    r"(\S*\u05BE(?=\S*\u05BE)|\S*\u05BE(?!\S*\u05BE)|\S*-(?!\S*-)|\S*-(?=\S*-)|\S*\s*)"
)

sheva = re.compile(r"\u05B0")
taamim = re.compile(r"[\u0591-\u05AE]")
taamim_capture_group = re.compile(r"([\u0591-\u05AE])")
vowels = re.compile(r"[\u05B1-\u05BB\u05C7]")
vowels_capture_group = re.compile(r"([\u05B1-\u05BB\u05C7])")
vowels_capture_group_with_sheva = re.compile(r"([\u05B0-\u05BB\u05C7])")

jerusalem_test = re.compile(
    r"(?P<vowel>[\u05B8\u05B7])(?P<hiriq>\u05B4)"
    r"(?P<taamimMatch>" + taamim.pattern + r"|\u05BD)(?P<mem>\u05DD.*)$"
)
