#!/usr/bin/env python3
"""Diffing module based on Python difflib"""

from difflib import Differ
from typing import List, Tuple, Optional, Iterable


Markup = List[Tuple[Optional[str],str]]
BitextMarkup = Tuple[Markup, Markup]
BitextDiff = List[BitextMarkup]
InfoChunk = Tuple[str, int, int]
InfoLine = List[InfoChunk]


DIFF_MINUS_WHOLE = "diffminus whole"
DIFF_MINUS = "diffminus"
DIFF_PLUS_WHOLE = "diffplus whole"
DIFF_PLUS = "diffplus"


def clean_hunk_markup(state: str, hunk: List[str]) -> BitextDiff:
    if state == " ":
        assert len(hunk) == 1
        src, tgt = hunk[0].split("\t", maxsplit=2)
        return [((None, src), (None, tgt))]

    elif state == "-":
        assert len(hunk) == 1
        src, tgt = hunk[0].split("\t", maxsplit=2)
        return [((DIFF_MINUS_WHOLE, src), (DIFF_MINUS_WHOLE, tgt))]

    elif state == "+":
        assert len(hunk) == 1
        src, tgt = hunk[0].split("\t", maxsplit=2)
        return [((DIFF_PLUS_WHOLE, src), (DIFF_PLUS_WHOLE, tgt))]

    elif state == "-+":
        assert len(hunk) == 2
        src1, tgt1 = hunk[0].split("\t", maxsplit=2)
        src2, tgt2 = hunk[1].split("\t", maxsplit=2)
        return [((DIFF_MINUS_WHOLE, src1), (DIFF_MINUS_WHOLE, tgt1)),
                ((DIFF_PLUS_WHOLE, src2), (DIFF_PLUS_WHOLE, tgt2))]

    else:
        raise ValueError(f"Unknown state {state}")


def hybrid_hunk_markup(state: str, hunk: List[str]) -> BitextDiff:
    if state == "-+?":
        assert len(hunk) == 3
        src1, tgt1 = hunk[0].split("\t", maxsplit=2)
        src2, tgt2 = hunk[1].split("\t", maxsplit=2)
        return [((DIFF_MINUS_WHOLE, src1), (DIFF_MINUS_WHOLE, tgt1)),
                ((DIFF_PLUS_WHOLE, src2), (DIFF_PLUS_WHOLE, tgt2))]

    elif state == "-?+":
        assert len(hunk) == 3
        src1, tgt1 = hunk[0].split("\t", maxsplit=2)
        src2, tgt2 = hunk[2].split("\t", maxsplit=2)
        return [((DIFF_MINUS_WHOLE, src1), (DIFF_MINUS_WHOLE, tgt1)),
                ((DIFF_PLUS_WHOLE, src2), (DIFF_PLUS_WHOLE, tgt2))]

    elif state == "-?+?":
        assert len(hunk) == 4
        src1, tgt1 = hunk[0].split("\t", maxsplit=2)
        src2, tgt2 = hunk[2].split("\t", maxsplit=2)
        return [((DIFF_MINUS_WHOLE, src1), (DIFF_MINUS_WHOLE, tgt1)),
                ((DIFF_PLUS_WHOLE, src2), (DIFF_PLUS_WHOLE, tgt2))]

    else:
        raise ValueError(f"Unknown state {state}")


class DiffLine:
    op: str
    content: str

    def __init__(self, diffline: str) -> None:
        assert len(diffline) > 1
        self.op = diffline[0]
        self.content = diffline[2:]

        if self.op != "?":
            assert self.content.count("\t") == 1


def _parse_infoline(info_content: str) -> List[Tuple[str, int, int]]:

    mode = info_content[0]
    start = 0
    groups = []

    for i, char in enumerate(info_content[1:]):
        if char != mode:
            groups.append((mode, start, i + 1))
            mode = char
            start = i + 1

    groups.append((mode, start, len(info_content)))
    return groups


def _parse_difflines(difflines: Iterable[DiffLine]) -> Iterable[BitextDiff]:

    start = 0
    something = True
    state: str = ""

    valid_transitions = {
        ("", " "),
        ("", "-"),
        ("", "+"),
        ("-", "?"),
        ("-", "+"),
        ("+", "?"),
        ("-?", "+"),
        ("-+", "?"),
        ("-?+", "?")}

    hybrid_hunks = {"-?+", "-+?", "-?+?"}
    clean_hunks = {" ", "-", "+", "-+"}

    def process_hunk(state: str, hunk: List[str]) -> BitextDiff:
        # there are three types of hunks: hybrid, clean and empty
        assert state != ""  # hunk must not be empty -> otherwise we would be
                            # able to add stuff.

        if state in hybrid_hunks:
            return hybrid_hunk_markup(state, hunk)

        elif state in clean_hunks:
            return clean_hunk_markup(state, hunk)

        else:
            assert False  # there are no other hunk types

        ## just yield different types of HUNK and the hunks will have specialized methods to generate markup

    hunk_state = ""
    hunk_content = []

    for i, diffline in enumerate(difflines):

        if (hunk_state, diffline.op) in valid_transitions:
            # can we add to the hunk?
            hunk_state = hunk_state + diffline.op
            hunk_content.append(diffline.content)
        else:
            # cannot add to the hunk.
            yield process_hunk(hunk_state, hunk_content)

            hunk_state = diffline.op
            hunk_content = [diffline.content]

    # is there something left in the hunk?
    if hunk_content:
        yield process_hunk(hunk_state, hunk_content)


def diff_bitexts(rev1_src: List[str], rev1_tgt: List[str],
                 rev2_src: List[str], rev2_tgt: List[str]) -> BitextDiff:
    """Bitext diff, respecting the number of items in revisions.

    Do not assume anything about the diff - most general diff for filters
    which add, remove or change lines.

    Try to guess which lines have been changed - this is delegated to the
    Python Differ class
    """
    assert len(rev1_src) == len(rev1_tgt)
    assert len(rev2_src) == len(rev2_tgt)

    tabsep_rev1 = [f"{src}\t{tgt}" for src, tgt in zip(rev1_src, rev1_tgt)]
    tabsep_rev2 = [f"{src}\t{tgt}" for src, tgt in zip(rev2_src, rev2_tgt)]


    d = Differ()
    difflines = d.compare(tabsep_rev1, tabsep_rev2)

    diff = []
    for partial_diff in _parse_difflines(DiffLine(d) for d in difflines):
        diff.extend(partial_diff)

    return diff


# Test code follows.

def main():

    text1_src = """1. Beautiful is better than ugly.
2. Explicit is better than implicit.
3. Simple is better than complex.
4. Complexy is better than complicated.
6. Cat is better than dog.
4. Complexy is better than complicated.
6. Cat is better than dog.
ahoj
bravo
abeat""".splitlines()

    text1_tgt="""Lepší pěkný než hnusný
Lepší explicitní než implicitní
Lepší jednoduchý než složitý
lepší komplexnost než demence
kočky josu lepší jak psi
Lepší byt než hnízdo
kočky jsou lepší jak psi
bet
delta
fero""".splitlines()

    text2_src = """1. Beautiful is better than ugly.
3.   Simple is better than complex.
4. Complicatedf is better than complex.
5. Flat is better than nested.
6. Cat is better.
5. Flat is better than nested.
6. Cat is better.
ahoj
bravo
beat""".splitlines()

    text2_tgt = """Lepší pěkný než hnusný
Lepší jednoduchý než složitý
lepší komplexnost nežli demence
Lepší byt než hnízdo
kočky jsou lepší jak psi
Lepší byt než hnízdo
kočky jsou lepší jak psi
beta
delta
fero""".splitlines()


    rows = diff_bitexts(text1_src, text1_tgt, text2_src, text2_tgt)
    for (left, right) in rows:
        print(left, "\t", right)

if __name__ == "__main__":
    main()
