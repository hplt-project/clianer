from typing import List, Tuple, Optional, Iterable
import diff_match_patch


Markup = List[Tuple[Optional[str],str]]
BitextMarkup = Tuple[Markup]
BitextDiff = List[BitextMarkup]
Chunk = Tuple[int, str]

DIFF_MINUS_WHOLE = "diffminus whole"
DIFF_MINUS = "diffminus"
DIFF_PLUS_WHOLE = "diffplus whole"
DIFF_PLUS = "diffplus"

INSERT = 1
DELETE = -1
KEEP = 0




def _chunks_to_lines(diff: List[Chunk]) -> Iterable[List[Chunk]]:

    # if I find a newline inside a minus or plus chunk, I must find another
    # one there.

    # that's not entirely true. If I just skip one whole line, then:
    # original data:
    # a TAB b | c TAB d | a TAB b |
    # new data:
    # a TAB b | a TAB b |
    # then I have for example:
    # (0, a TAB B |), (-1, c TAB d |), (0, a TAB b |)

    # after splitting into lines it would be
    # (0, a TAB b), (0, ""), (-1, c TAB d), (-1, ""), (0, a tab b), (0, "")
    # but it could also be the other way around and the first newline would be
    # minus and the second zero

    # either way, if I find a newline inside a minus, the line to the left or
    # right must be entirely in the minus - I can assert that. analogously for
    # pluses.


    # so there are two strategies for handling the newlines

    # if there is a newline encountered in a minus/plus, check whether it is
    # the first minus character or not. also check whether the minus chunk
    # began right after a newline or not.


    lines = []
    current_line = []

    last_type = None
    for chunk_type, chunk in diff:

        if last_type is not None:
            # We assume that neighboring chunks have different types
            assert chunk_type != last_type
            last_type = chunk_type

        if "\n" not in chunk:
            # if there is no newline in the chunk, just append it to the
            # current line as is
            current_line.append((chunk_type, chunk))

        else:
            subchunks = chunk.split("\n")

            # Was the previous chunk ins/del, AND did it contain newlines?
            #  - If the last thing was a newline, it is acceptable - we can
            #    tell by looking at current_line, which should be empty.
            #  - If not, the first subchunk here should be empty.
            # maybe bad:            assert last_type == KEEP or (not current_line or not subchunks[0])

            # if there is a newline character in the chunk, we proceed
            # according to the chunk type
            if chunk_type == KEEP:
                # If the type is KEEP, we just split chunk into lines and
                # append those lines. We do not append empty chunks if created
                # by newlines on the end. Also do not finalize the last chunk.

                for subchunk in subchunks[:-1]:
                    if subchunk:
                        current_line.append((chunk_type, subchunk))
                    lines.append(current_line)
                    current_line = []

                if subchunks[-1]:
                    current_line.append((chunk_type, subchunk[-1]))

            else:  # Contains \n and is either INSERT or DELETE


                # Can the chunk contain the \n inside? (i.e. NOT begin or end with it?)
                # Yes, ONLY if the next chunk starts with \n, OR if the previous chunk ended with \n.

                # We know that either the first subchunk is empty or that the
                # current line is empty.

                for subchunk in subchunks[:-1]:

                    pass





                if current_line and subchunks[0]:
                    # We are adding an insert/delete chunk to the end of a line
                    # that is acceptable.
                    pass

                if current_line and not subchunks[0]:
                    # we finalize the current line and start at the next chunk.
                    # this is also acceptable. The next chunk needs to end within this line. -> next chunk must start with a newline.
                    pass

                if not current_line:
                    # this is acceptable, we are creating a new line.
                    pass


                # now, everything needs to be homogeneous except the last subchunk

            before, after = chunk.split("\n", maxsplit=2)

            if len(before) > 0:
                # if this is the first chunk, this is acceptable and the whole
                # line is homogeneous

                # if this is not the first chunk, the whole following line
                # *has* to be homogeneous i.e. it has to be constituted of a
                # single chunk.
                pass
            else:
                pass







def _resegment_bitext_diff(diff: List[Chunk]) -> BitextDiff:
    """Recover tab-separated lines from the  output of the Google differ

    This function resegments the long list of markup to recover the lines and
    the tab characters (one per line).
    """
    current_markup: BitextMarkup = ([], [])
    current_side: int = 0
    result: BitextDiff = []

    for chunk_type, chunk in diff:

        lines = chunk.split("\n")
        # before first split - that belongs to current markup
        # between first and last split - these are complete markups
        # after last split - leave that markup open






        # what if "\n", "\t" are in a + or - chunk?
        # first, just disallow this
        if "\n" in chunk and chunk_type != KEEP:
            import pudb; pu.db

        assert "\n" not in chunk or chunk_type == KEEP
        assert "\t" not in chunk or chunk_type == KEEP

        if chunk_type == INSERT:
            current_markup[current_side].append((DIFF_PLUS, chunk))
            continue

        if chunk_type == DELETE:
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
    dmp.Diff_Timeout = 30

    # diff = []

    # longersize = max(len(tabsep_rev1), len(tabsep_rev2))
    # batch_size = 50
    # for batch in range(longersize // batch_size + 1):
        # rev1_batch = tabsep_rev1[batch * batch_size: (batch + 1) * batch_size]
        # rev2_batch = tabsep_rev2[batch * batch_size: (batch + 1) * batch_size]

        # diff.extend(
    diff = dmp.diff_main("\n".join(tabsep_rev1), "\n".join(tabsep_rev2))

    return _resegment_bitext_diff(diff)
