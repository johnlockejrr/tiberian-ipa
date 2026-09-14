"""Syllabification engine (ported from havarotjs)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Union

from ..cluster import Cluster
from ..syllable import Syllable
from .regular_expressions import vowels

ClusterOrSyllable = Union[Cluster, Syllable]


def _create_new_syllable(
    result: List[ClusterOrSyllable],
    syl: List[Cluster],
    is_closed: bool = False,
) -> List[Cluster]:
    result.append(Syllable(syl, isClosed=is_closed))
    return []


def _group_final(arr: List[Cluster]) -> List[ClusterOrSyllable]:
    length = len(arr)
    i = 0
    syl: List[Cluster] = []
    result: List[ClusterOrSyllable] = []
    vowel_present = False

    final_cluster = arr[i]
    syl.insert(0, final_cluster)

    if final_cluster.isPunctuation and i + 1 < length and arr[i + 1]:
        i += 1
        final_cluster = arr[i]
        syl.insert(0, final_cluster)

    if final_cluster.hasVowel:
        vowel_present = True
        i += 1
    elif final_cluster.isShureq:
        i += 1
        if i <= length and i < length and arr[i]:
            syl.insert(0, arr[i])
        vowel_present = True
        i += 1
    else:
        i += 1

    while not vowel_present:
        nxt = arr[i] if i < length else None
        if not nxt:
            break
        syl.insert(0, nxt)
        if nxt.isShureq:
            i += 1
            if i < length and arr[i]:
                syl.insert(0, arr[i])
            vowel_present = True
        else:
            vowel_present = nxt.hasVowel or nxt.isShureq
        i += 1
        if i > length:
            break

    filtered = [c for c in final_cluster.chars if c.sequencePosition != 4]
    final_char = filtered[-1].text if filtered else ""
    has_final_vowel = bool(vowels.search(final_char))
    prev_has_sheva = False
    if final_cluster.prev is not None and final_cluster.prev.value is not None:
        prev_has_sheva = bool(getattr(final_cluster.prev.value, "hasSheva", False))

    is_closed = (
        not final_cluster.isShureq
        and not final_cluster.isMater
        and (not re.search(r"\u05D0", final_cluster.text) or prev_has_sheva)
        and not re.search(r"\u05D4(?!\u05bc)", final_cluster.text)
        and not has_final_vowel
    )

    final_syllable = Syllable(syl, isClosed=is_closed)
    remainder: List[ClusterOrSyllable] = list(arr[i:]) if i < length else []
    result = remainder if remainder else []
    result.insert(0, final_syllable)
    return result


def _group_shevas(arr: List[ClusterOrSyllable], options: Dict[str, Any]) -> List[ClusterOrSyllable]:
    length = len(arr)
    syl: List[Cluster] = []
    result: List[ClusterOrSyllable] = []
    sheva_present = False

    for index in range(length):
        cluster = arr[index]
        if isinstance(cluster, Syllable):
            result.append(cluster)
            continue

        cluster_has_sheva = cluster.hasSheva

        if sheva_present and cluster_has_sheva:
            syl = _create_new_syllable(result, syl)
            syl.insert(0, cluster)
            continue

        if cluster_has_sheva and cluster.hasMeteg and options.get("shevaWithMeteg"):
            syl.insert(0, cluster)
            syl = _create_new_syllable(result, syl)
            continue

        consonant = cluster.chars[0].text if cluster.chars else ""
        prev_item = arr[index - 1] if index > 0 else None
        prev_consonant = ""
        if prev_item is not None and not isinstance(prev_item, Syllable) and prev_item.chars:
            prev_consonant = prev_item.chars[0].text
        next_cluster_vowel = arr[index + 1] if index + 1 < length else None

        if (
            not sheva_present
            and cluster_has_sheva
            and (
                consonant != prev_consonant
                or (
                    isinstance(next_cluster_vowel, Cluster)
                    and next_cluster_vowel.hasShortVowel
                )
            )
        ):
            sheva_present = True
            syl.insert(0, cluster)
            continue

        if sheva_present and (cluster.hasShortVowel or cluster.hasHalfVowel):
            if options.get("shevaAfterMeteg") and cluster.hasMeteg:
                syl = _create_new_syllable(result, syl)
                syl.insert(0, cluster)
                continue

            dagesh_re = re.compile(r"\u05BC")
            prev = syl[0].text
            sqnmlvy = re.compile(r"[שסצקנמלוי]")
            waw_consecutive = re.compile(r"וַ")

            if dagesh_re.search(prev):
                syl = _create_new_syllable(result, syl)
            elif (
                (options.get("sqnmlvy") or (options.get("shevaAfterMeteg") and cluster.hasMeteg))
                and sqnmlvy.search(prev)
                and waw_consecutive.search(cluster.text)
            ):
                syl = _create_new_syllable(result, syl)
                result.append(Syllable([cluster]))
                sheva_present = False
                continue
            elif options.get("article") and re.search(r"[ילמ]", prev) and re.search(r"הַ", cluster.text):
                syl = _create_new_syllable(result, syl)
                result.append(Syllable([cluster]))
                sheva_present = False
                continue

            syl.insert(0, cluster)
            syl = _create_new_syllable(result, syl, True)
            sheva_present = False
            continue

        if sheva_present and cluster.hasLongVowel:
            if options.get("longVowels") or (cluster.hasMeteg and options.get("shevaAfterMeteg")):
                syl = _create_new_syllable(result, syl)
                result.append(cluster)
                sheva_present = False
            else:
                syl.insert(0, cluster)
                syl = _create_new_syllable(result, syl, True)
                sheva_present = False
            continue

        if sheva_present and cluster.isShureq:
            if (
                not options.get("wawShureq")
                and (not options.get("shevaAfterMeteg") or not cluster.hasMeteg)
                and length - 1 == index
            ):
                syl.insert(0, cluster)
                syl = _create_new_syllable(result, syl, True)
            else:
                syl = _create_new_syllable(result, syl)
                result.append(cluster)
                sheva_present = False
            continue

        if sheva_present and cluster.isMater and options.get("longVowels"):
            syl = _create_new_syllable(result, syl)
            result.append(cluster)
            sheva_present = False
            continue

        if sheva_present and not cluster.hasVowel:
            syl.insert(0, cluster)
            continue

        result.append(cluster)

    if syl:
        _create_new_syllable(result, syl)
    return result


def _group_maters(arr: List[ClusterOrSyllable], strict: bool = True) -> List[ClusterOrSyllable]:
    length = len(arr)
    syl: List[Cluster] = []
    result: List[ClusterOrSyllable] = []

    index = 0
    while index < length:
        cluster = arr[index]
        if isinstance(cluster, Syllable):
            result.append(cluster)
            index += 1
            continue

        if cluster.isMater:
            syl.insert(0, cluster)
            nxt = arr[index + 1] if index + 1 < length else None
            if nxt is None and strict:
                word = "".join(i.text for i in arr)
                raise ValueError(
                    f"The cluster {cluster.text} is a mater, but nothing precedes it in {word}"
                )
            if isinstance(nxt, Syllable):
                word = "".join(i.text for i in arr)
                if strict:
                    raise ValueError(
                        f"Syllable {nxt.text} should not precede a Cluster with a Mater in {word}"
                    )
                syl[0:0] = list(nxt.clusters)
            elif nxt is not None:
                assert isinstance(nxt, Cluster)
                syl.insert(0, nxt)
            syl = _create_new_syllable(result, syl)
            index += 2
            continue

        if not cluster.hasVowel and re.search(r"א", cluster.text):
            syl.insert(0, cluster)
            nxt = arr[index + 1] if index + 1 < length else None
            if nxt is None and strict:
                word = "".join(i.text for i in arr)
                raise ValueError(
                    f"The cluster {cluster.text} is a quiesced alef, but nothing precedes it in {word}"
                )
            if isinstance(nxt, Syllable):
                result.append(cluster)
                index += 1
                continue
            if nxt is not None:
                assert isinstance(nxt, Cluster)
                syl.insert(0, nxt)
            syl = _create_new_syllable(result, syl)
            index += 2
            continue

        result.append(cluster)
        index += 1

    return result


def _group_shureqs(arr: List[ClusterOrSyllable], strict: bool = True) -> List[ClusterOrSyllable]:
    length = len(arr)
    syl: List[Cluster] = []
    result: List[ClusterOrSyllable] = []

    index = 0
    while index < length:
        cluster = arr[index]
        if isinstance(cluster, Syllable):
            result.append(cluster)
            index += 1
            continue

        if cluster.isShureq:
            syl.insert(0, cluster)
            nxt = arr[index + 1] if index + 1 < length else None
            if strict and isinstance(nxt, Syllable):
                word = "".join(i.text for i in arr)
                raise ValueError(
                    f"Syllable {nxt.text} should not precede a Cluster with a Shureq in {word}"
                )
            if nxt is not None:
                if isinstance(nxt, Cluster):
                    syl.insert(0, nxt)
                elif isinstance(nxt, Syllable):
                    # Non-strict path: JS unshifts the Syllable; flatten clusters instead
                    for c in reversed(nxt.clusters):
                        syl.insert(0, c)
            syl = _create_new_syllable(result, syl)
            index += 2 if nxt is not None else 1
            continue

        result.append(cluster)
        index += 1

    return result


def _group_clusters(arr: List[Cluster], options: Dict[str, Any]) -> List[ClusterOrSyllable]:
    rev = list(reversed(arr))
    final_grouped = _group_final(rev)
    shevas_grouped = _group_shevas(final_grouped, options)
    shureq_groups = _group_shureqs(shevas_grouped, options.get("strict", True))
    maters_groups = _group_maters(shureq_groups, options.get("strict", True))
    return list(reversed(maters_groups))


def _set_is_closed(syllable: Syllable, index: int, arr: List[Syllable]) -> None:
    if index == len(arr) - 1:
        return
    if not syllable.isClosed:
        dagesh_re = re.compile(r"\u05BC")
        has_short_vowel = any(c.hasShortVowel for c in syllable.clusters)
        # JS: !!(syllable.clusters.filter((cluster) => !cluster.hasVowel).length - 1)
        no_vowel_count = sum(1 for c in syllable.clusters if not c.hasVowel)
        has_no_vowel = has_short_vowel or bool(no_vowel_count - 1)
        prev = arr[index + 1]
        prev_dagesh = bool(dagesh_re.search(prev.clusters[0].text))
        syllable.isClosed = (has_short_vowel or has_no_vowel) and prev_dagesh


def _set_is_accented(syllable: Syllable) -> None:
    if syllable.isAccented:
        return

    jerusalem_final = re.compile(r"\u05B4\u05DD")
    jerusalem_prev = re.compile(r"ל[\u05B8\u05B7]")
    prev = syllable.prev.value if syllable.prev else None

    if jerusalem_final.search(syllable.text) and prev and jerusalem_prev.search(prev.text):
        prev.isAccented = True
        return

    segolta = re.compile(r"\u0592")
    if segolta.search(syllable.text):
        if syllable.isFinal and prev:
            while prev:
                if segolta.search(prev.text):
                    prev.isAccented = True
                    return
                prev = prev.prev.value if prev.prev else None
        syllable.isAccented = True
        return

    zarqa = re.compile(r"\u05AE")
    if zarqa.search(syllable.text):
        zarqa_helper = re.compile(r"\u0598")
        if syllable.isFinal and prev:
            while prev:
                if zarqa_helper.search(prev.text):
                    prev.isAccented = True
                    return
                prev = prev.prev.value if prev.prev else None

    sinnorit = re.compile(r"\u0598")
    if sinnorit.search(syllable.text):
        syllable.isAccented = False
        return

    pashta = re.compile(r"\u0599")
    syl_text = syllable.text
    if syllable.isFinal and pashta.search(syl_text):
        qadma = re.compile(r"\u05A8")
        while prev:
            if pashta.search(prev.text) or qadma.search(prev.text):
                return
            prev = prev.prev.value if prev.prev else None

    telisha_qetana = re.compile(r"\u05A9")
    if telisha_qetana.search(syllable.text):
        while prev:
            if telisha_qetana.search(prev.text):
                prev.isAccented = True
                return
            prev = prev.prev.value if prev.prev else None
        syllable.isAccented = True
        return

    teslisha_gedola = re.compile(r"\u05A0")
    if teslisha_gedola.search(syllable.text):
        nxt = syllable.next.value if syllable.next else None
        while nxt:
            if teslisha_gedola.search(nxt.text):
                nxt.isAccented = True
                return
            nxt = nxt.next.value if nxt.next else None
        syllable.isAccented = True
        return

    ole = re.compile(r"\u05AB")
    if ole.search(syllable.text):
        yored = re.compile(r"\u05A5")
        nxt = syllable.next.value if syllable.next else None
        while nxt:
            if yored.search(nxt.text):
                nxt.isAccented = True
                syllable.isAccented = False
                return
            nxt = nxt.next.value if nxt.next else None
        syllable.isAccented = True
        return

    dechi = re.compile(r"\u05AD")
    if dechi.search(syllable.text):
        nxt = syllable.next.value if syllable.next else None
        while nxt:
            if nxt.next is None:
                nxt.isAccented = True
                return
            nxt = nxt.next.value if nxt.next else None

    geresh_muqdam = re.compile(r"\u059D")
    if geresh_muqdam.search(syllable.text):
        syllable.isAccented = False
        return

    is_accented = any(c.hasTaamim or c.hasSilluq for c in syllable.clusters)
    syllable.isAccented = is_accented


def _cluster_pos(cluster: Cluster, i: int) -> Dict[str, Any]:
    return {"cluster": cluster, "pos": i}


def _reinsert_latin(syls: List[Syllable], latin: List[Dict[str, Any]]) -> List[Syllable]:
    num_of_syls = len(syls)
    index = 0
    while index < len(latin):
        group = latin[index]
        partial: List[Cluster] = []
        if group["pos"] == 0:
            partial.append(group["cluster"])
            while index + 1 < len(latin) and latin[index + 1]["pos"] == group["pos"] + 1:
                partial.append(latin[index + 1]["cluster"])
                index += 1
            first_syl = syls[0]
            syls[0] = Syllable(
                partial + list(first_syl.clusters),
                isAccented=first_syl.isAccented,
                isClosed=first_syl.isClosed,
                isFinal=first_syl.isFinal,
            )
        else:
            last_syl = syls[num_of_syls - 1]
            while index < len(latin):
                partial.append(latin[index]["cluster"])
                index += 1
            syls[num_of_syls - 1] = Syllable(
                list(last_syl.clusters) + partial,
                isAccented=last_syl.isAccented,
                isClosed=last_syl.isClosed,
                isFinal=last_syl.isFinal,
            )
            break
        index += 1
    return syls


def syllabify(
    clusters: List[Cluster],
    options: Dict[str, Any],
    is_word_in_construct: bool,
) -> List[Syllable]:
    remove_latin = [c for c in clusters if not c.isNotHebrew]
    latin_clusters = [
        _cluster_pos(c, i) for i, c in enumerate(clusters) if c.isNotHebrew
    ]
    grouped = _group_clusters(remove_latin, options)
    syllables: List[Syllable] = [
        g if isinstance(g, Syllable) else Syllable([g]) for g in grouped
    ]

    if not syllables:
        return []

    first, *rest = syllables
    first.siblings = rest

    syllables[-1].isFinal = True
    for i, s in enumerate(syllables):
        _set_is_closed(s, i, syllables)
    for s in syllables:
        _set_is_accented(s)

    if not any(s.isAccented for s in syllables) and not is_word_in_construct:
        syllables[-1].isAccented = True

    for s in syllables:
        for c in s.clusters:
            c.syllable = s

    if latin_clusters:
        return _reinsert_latin(syllables, latin_clusters)
    return syllables
