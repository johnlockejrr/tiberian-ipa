"""Character ↔ name maps (ported from havarotjs)."""

from __future__ import annotations

from typing import Dict

taamim_char_to_name_map: Dict[str, str] = {
    "\u0591": "ETNAHTA",
    "\u0592": "SEGOL_ACCENT",
    "\u0593": "SHALSHELET",
    "\u0594": "ZAQEF_QATAN",
    "\u0595": "ZAQEF_GADOL",
    "\u0596": "TIPEHA",
    "\u0597": "REVIA",
    "\u0598": "ZARQA",
    "\u0599": "PASHTA",
    "\u059A": "YETIV",
    "\u059B": "TEVIR",
    "\u059C": "GERESH",
    "\u059D": "GERESH_MUQDAM",
    "\u059E": "GERSHAYIM",
    "\u059F": "QARNEY_PARA",
    "\u05A0": "TELISHA_GEDOLA",
    "\u05A1": "PAZER",
    "\u05A2": "ATNAH_HAFUKH",
    "\u05A3": "MUNAH",
    "\u05A4": "MAHAPAKH",
    "\u05A5": "MERKHA",
    "\u05A6": "MERKHA_KEFULA",
    "\u05A7": "DARGA",
    "\u05A8": "QADMA",
    "\u05A9": "TELISHA_QETANA",
    "\u05AA": "YERAH_BEN_YOMO",
    "\u05AB": "OLE",
    "\u05AC": "ILUY",
    "\u05AD": "DEHI",
    "\u05AE": "ZINOR",
}


def is_char_taam(char: str) -> bool:
    return char in taamim_char_to_name_map


taamim_name_to_char_map: Dict[str, str] = {
    "ETNAHTA": "\u0591",
    "SEGOL_ACCENT": "\u0592",
    "SHALSHELET": "\u0593",
    "ZAQEF_QATAN": "\u0594",
    "ZAQEF_GADOL": "\u0595",
    "TIPEHA": "\u0596",
    "REVIA": "\u0597",
    "ZARQA": "\u0598",
    "PASHTA": "\u0599",
    "YETIV": "\u059A",
    "TEVIR": "\u059B",
    "GERESH": "\u059C",
    "GERESH_MUQDAM": "\u059D",
    "GERSHAYIM": "\u059E",
    "QARNEY_PARA": "\u059F",
    "TELISHA_GEDOLA": "\u05A0",
    "PAZER": "\u05A1",
    "ATNAH_HAFUKH": "\u05A2",
    "MUNAH": "\u05A3",
    "MAHAPAKH": "\u05A4",
    "MERKHA": "\u05A5",
    "MERKHA_KEFULA": "\u05A6",
    "DARGA": "\u05A7",
    "QADMA": "\u05A8",
    "TELISHA_QETANA": "\u05A9",
    "YERAH_BEN_YOMO": "\u05AA",
    "OLE": "\u05AB",
    "ILUY": "\u05AC",
    "DEHI": "\u05AD",
    "ZINOR": "\u05AE",
}

vowel_char_to_name_map: Dict[str, str] = {
    "\u05B1": "HATAF_SEGOL",
    "\u05B2": "HATAF_PATAH",
    "\u05B3": "HATAF_QAMATS",
    "\u05B4": "HIRIQ",
    "\u05B5": "TSERE",
    "\u05B6": "SEGOL",
    "\u05B7": "PATAH",
    "\u05B8": "QAMATS",
    "\u05B9": "HOLAM",
    "\u05BA": "HOLAM_HASER",
    "\u05BB": "QUBUTS",
    "\u05C7": "QAMATS_QATAN",
}


def is_char_vowel(char: str) -> bool:
    return char in vowel_char_to_name_map


vowel_name_to_char_map: Dict[str, str] = {
    "HATAF_SEGOL": "\u05B1",
    "HATAF_PATAH": "\u05B2",
    "HATAF_QAMATS": "\u05B3",
    "HIRIQ": "\u05B4",
    "TSERE": "\u05B5",
    "SEGOL": "\u05B6",
    "PATAH": "\u05B7",
    "QAMATS": "\u05B8",
    "HOLAM": "\u05B9",
    "HOLAM_HASER": "\u05BA",
    "QUBUTS": "\u05BB",
    "QAMATS_QATAN": "\u05C7",
}

consonant_char_to_name_map: Dict[str, str] = {
    "\u05D0": "ALEF",
    "\u05D1": "BET",
    "\u05D2": "GIMEL",
    "\u05D3": "DALET",
    "\u05D4": "HE",
    "\u05D5": "VAV",
    "\u05D6": "ZAYIN",
    "\u05D7": "HET",
    "\u05D8": "TET",
    "\u05D9": "YOD",
    "\u05DA": "FINAL_KAF",
    "\u05DB": "KAF",
    "\u05DC": "LAMED",
    "\u05DD": "FINAL_MEM",
    "\u05DE": "MEM",
    "\u05DF": "FINAL_NUN",
    "\u05E0": "NUN",
    "\u05E1": "SAMEKH",
    "\u05E2": "AYIN",
    "\u05E3": "FINAL_PE",
    "\u05E4": "PE",
    "\u05E5": "FINAL_TSADI",
    "\u05E6": "TSADI",
    "\u05E7": "QOF",
    "\u05E8": "RESH",
    "\u05E9": "SHIN",
    "\u05EA": "TAV",
}


def is_char_consonant(char: str) -> bool:
    return char in consonant_char_to_name_map


consonant_name_to_char_map: Dict[str, str] = {
    "ALEF": "\u05D0",
    "BET": "\u05D1",
    "GIMEL": "\u05D2",
    "DALET": "\u05D3",
    "HE": "\u05D4",
    "VAV": "\u05D5",
    "ZAYIN": "\u05D6",
    "HET": "\u05D7",
    "TET": "\u05D8",
    "YOD": "\u05D9",
    "FINAL_KAF": "\u05DA",
    "KAF": "\u05DB",
    "LAMED": "\u05DC",
    "FINAL_MEM": "\u05DD",
    "MEM": "\u05DE",
    "FINAL_NUN": "\u05DF",
    "NUN": "\u05E0",
    "SAMEKH": "\u05E1",
    "AYIN": "\u05E2",
    "FINAL_PE": "\u05E3",
    "PE": "\u05E4",
    "FINAL_TSADI": "\u05E5",
    "TSADI": "\u05E6",
    "QOF": "\u05E7",
    "RESH": "\u05E8",
    "SHIN": "\u05E9",
    "TAV": "\u05EA",
}

char_to_name_map: Dict[str, str] = {
    **taamim_char_to_name_map,
    **vowel_char_to_name_map,
    **consonant_char_to_name_map,
    "\u05B0": "SHEVA",
    "\u05BC": "DAGESH",
    "\u05BF": "RAFE",
    "\u05BE": "MAQAF",
    "\u05C0": "PASEQ",
    "\u05C3": "SOF_PASUQ",
    "\u05C6": "NUN_HAFUKHA",
    "\u05F3": "GERESH_PUNCTUATION",
    "\u05F4": "GERSHAYIM_PUNCTUATION",
    "\u05C1": "SHIN_DOT",
    "\u05C2": "SIN_DOT",
    "\u05AF": "MASORA_CIRCLE",
    "\u05C4": "UPPER_DOT",
    "\u05C5": "LOWER_DOT",
    "\u05EF": "YOD_TRIANGLE",
    "\u05F0": "DOUBLE_VAV",
    "\u05F1": "VAV_YOD",
    "\u05F2": "DOUBLE_YOD",
}


def is_hebrew_character(char: str) -> bool:
    return char in char_to_name_map


name_to_char_map: Dict[str, str] = {
    **taamim_name_to_char_map,
    **vowel_name_to_char_map,
    **consonant_name_to_char_map,
    "SHEVA": "\u05B0",
    "DAGESH": "\u05BC",
    "RAFE": "\u05BF",
    "MAQAF": "\u05BE",
    "PASEQ": "\u05C0",
    "SOF_PASUQ": "\u05C3",
    "NUN_HAFUKHA": "\u05C6",
    "GERESH_PUNCTUATION": "\u05F3",
    "GERSHAYIM_PUNCTUATION": "\u05F4",
    "SHIN_DOT": "\u05C1",
    "SIN_DOT": "\u05C2",
    "MASORA_CIRCLE": "\u05AF",
    "UPPER_DOT": "\u05C4",
    "LOWER_DOT": "\u05C5",
    "YOD_TRIANGLE": "\u05EF",
    "DOUBLE_VAV": "\u05F0",
    "VAV_YOD": "\u05F1",
    "DOUBLE_YOD": "\u05F2",
}


def is_hebrew_character_name(name: str) -> bool:
    return name in name_to_char_map
