from typing import List, Tuple, Optional
import diff_match_patch


Markup = List[Tuple[Optional[str],str]]
BitextMarkup = Tuple[Markup]
BitextDiff = List[BitextMarkup]

DIFF_MINUS_WHOLE = "diffminus whole"
DIFF_MINUS = "diffminus"
DIFF_PLUS_WHOLE = "diffplus whole"
DIFF_PLUS = "diffplus"

INSERTION = 1
DELETION = -1
KEEP = 0


def _resegment_bitext_diff(diff: List[Tuple[int, str]]) -> BitextDiff:
    """Recover tab-separated lines from the  output of the Google differ

    This function resegments the long list of markup to recover the lines and
    the tab characters (one per line).
    """
    current_markup: BitextMarkup = ([], [])
    current_side: int = 0
    result: BitextDiff = []

    for chunk_type, chunk in diff:
        # what if "\n", "\t" are in a + or - chunk?
        # first, just disallow this
        if "\n" in chunk and chunk_type != KEEP:
            import pudb; pu.db

        assert "\n" not in chunk or chunk_type == KEEP
        assert "\t" not in chunk or chunk_type == KEEP

        if chunk_type == INSERTION:
            current_markup[current_side].append((DIFF_PLUS, chunk))
            continue

        if chunk_type == DELETION:
            current_markup[current_side].append((DIFF_MINUS, chunk))
            continue

        assert chunk_type == KEEP

        lines = chunk.split("\n")
        for i, line in enumerate(lines):
            if i > 0:
                assert current_side == 1
                # flush out the current markup
                result.append(current_markup)

                current_side = 0
                current_markup = ([], [])

            sides = line.split("\t")
            assert len(sides) in [1, 2]

            for j, side in enumerate(sides):
                if j > 0:
                    current_side = 1

                if side:
                    current_markup[current_side].append((None, side))

    if current_markup[0] or current_markup[1]:
        result.append(current_markup)

    return result


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

    # import pudb;pu.db

    tabsep_rev1 = [f"{src}\t{tgt}" for src, tgt in zip(rev1_src, rev1_tgt)]
    tabsep_rev2 = [f"{src}\t{tgt}" for src, tgt in zip(rev2_src, rev2_tgt)]

    dmp = diff_match_patch.diff_match_patch()
    diff = dmp.diff_main("\n".join(tabsep_rev1), "\n".join(tabsep_rev2))

    return _resegment_bitext_diff(diff)
