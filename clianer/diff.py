#!/usr/bin/env python3
from difflib import Differ
import urwid
from typing import List, Tuple

def unhandled(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


palette = [
    ('body', 'black', 'light gray', 'standout'),
    ("diffminus", "black", "light red"),
    ("diffplus", "black", "light green"),
    ("diffminus whole", "light red", "black"),
    ("diffplus whole", "light green", "black")]


class Hunk:
    minus: str = None
    minusinfo: str = None
    plus: str = None
    plusinfo: str = None


def process_hunk(hunk: Hunk) -> List[Tuple[str, str]]:
    assert hunk.minus is not None and hunk.plus is not None

    if hunk.minusinfo is None and hunk.plusinfo is None:
        return [("diffminus whole", hunk.minus), ("diffplus whole", hunk.plus)]

    if hunk.minusinfo is None:
        hunk.minusinfo = ""

    if hunk.plusinfo is None:
        hunk.plusinfo = ""

    spans: List[Tuple[str, str]] = []

    plus_index: int = 0
    minus_index: int = 0

    hunk.plusinfo = hunk.plusinfo.ljust(len(hunk.plus), " ")  # this is a bug
    hunk.minusinfo = hunk.minusinfo.ljust(len(hunk.minus), " ") ## This is a bug

    assert len(hunk.plusinfo) == len(hunk.plus)
    assert len(hunk.minusinfo) == len(hunk.minus)

    assert hunk.plusinfo.count("^") == hunk.minusinfo.count("^")
    print(hunk.plusinfo.replace(" ", "X"),"|||", hunk.minusinfo.replace(" ", "Y"))
    assert hunk.plusinfo.count(" ") == hunk.minusinfo.count(" ")

    start_common = 0
    common_length = 0

    finished = False
    while not finished:

        if plus_index == len(hunk.plusinfo):
            assert minus_index < len(hunk.minusinfo)
            assert hunk.minusinfo[minus_index] == "-"
            plus_instr = "x"
        else:
            plus_instr = hunk.plusinfo[plus_index]

        if minus_index == len(hunk.minusinfo):
            assert plus_index < len(hunk.plusinfo)
            assert hunk.plusinfo[plus_index] == "+"
            minus_instr = "x"
        else:
            minus_instr = hunk.minusinfo[minus_index]

        assert not (plus_instr == "+" and minus_instr == "-")
        assert not (plus_instr == "^" and minus_instr == " ")
        assert not (plus_instr == " " and minus_instr == "^")

        if plus_instr == "+":
            if common_length > 0:
                spans.append((None, hunk.plus[start_common:plus_index]))
                common_length = 0

            start = plus_index
            while plus_index < len(hunk.plusinfo) and hunk.plusinfo[plus_index] == "+":
                plus_index += 1
            spans.append(("diffplus", hunk.plus[start:plus_index]))

        elif minus_instr == "-":
            if common_length > 0:
                spans.append((None, hunk.plus[start_common:plus_index]))
                common_length = 0

            start = minus_index
            while minus_index < len(hunk.minusinfo) and hunk.minusinfo[minus_index] == "-":
                minus_index += 1
            spans.append(("diffminus", hunk.minus[start:minus_index]))

        elif plus_instr == "^":  # implies minus_instr == "^"
            if common_length > 0:
                spans.append((None, hunk.plus[start_common:plus_index]))
                common_length = 0

            start_plus = plus_index
            start_minus = minus_index

            while plus_index < len(hunk.plusinfo) and hunk.plusinfo[plus_index] == "^":
                assert hunk.minusinfo[minus_index] == "^"
                assert minus_index < len(hunk.minusinfo)
                plus_index += 1
                minus_index += 1

            spans.append(("diffminus", hunk.minus[start_minus:minus_index]))
            spans.append(("diffplus", hunk.plus[start_plus:plus_index]))

        elif plus_instr == " " and minus_instr == " ":
            if common_length == 0:
                start_common = plus_index

            assert hunk.plus[plus_index] == hunk.minus[minus_index]
            plus_index += 1
            minus_index += 1
            common_length += 1

        else:
            raise Exception("unhandled case")

        finished = plus_index == len(hunk.plus) and minus_index == len(hunk.minus)

    if common_length > 0:
        spans.append((None, hunk.plus[start_common:plus_index]))

    return spans


def compute_diff(text1: List[str], text2: List[str]) -> List[urwid.Text]:

    rows: List[urwid.Text] = []
    op_state: int = 0  # zero (initial state), 1 (minus in hunk), 2 (plus in hunk)
    hunk: Hunk = None

    d = Differ()
    for line in d.compare(text1, text2):
        print(line.rstrip("\r\n"))
        #continue
        line = line.rstrip("\r\n")

        op = line[0]
        content = line[2:]

        if op == " ":
            if hunk is not None:
                rows.append(urwid.Text(process_hunk(hunk)))
            hunk = None
            rows.append(urwid.Text(content))
            op_state = 0

        if op == "-":
            if hunk is not None:
                if hunk.plus is None:
                    assert hunk.minusinfo is None and hunk.plusinfo is None
                    rows.append(urwid.Text(("diffminus whole", hunk.minus)))
                else:
                    rows.append(urwid.Text(process_hunk(hunk)))
            hunk = Hunk()
            hunk.minus = content
            op_state = 1

        if op == "?" and op_state == 1:
            assert hunk is not None
            hunk.minusinfo = content

        if op == "+":
            # assert op_state in [0, 1]

            if op_state == 0:
                assert hunk is None
                rows.append(urwid.Text(("diffplus whole", content)))

            elif op_state == 1:
                assert hunk is not None
                hunk.plus = content
                op_state = 2

            elif op_state == 2:
                assert hunk.plus is not None and hunk.minus is not None and hunk.plusinfo is None and hunk.minusinfo is None
                rows.append(urwid.Text(("diffminus whole", hunk.minus)))
                rows.append(urwid.Text(("diffplus whole", hunk.plus)))
                hunk = None
                rows.append(urwid.Text(("diffplus whole", content)))
                op_state = 0

        if op == "?" and op_state == 2:
            assert hunk is not None
            hunk.plusinfo = content
            rows.append(urwid.Text(process_hunk(hunk)))
            hunk = None
            op_state = 0

    if hunk is not None:
        rows.append(urwid.Text(process_hunk(hunk)))

    return rows


def main():

    text1 = '''1. Beautiful is better than ugly.
2. Explicit is better than implicit.
3. Simple is better than complex.
4. Complexy is better than complicated.
6. Cat is better than dog.
ahoj\tbet
bravo\tdelta
abeat\tfero
'''.splitlines(keepends=True)

    text2 = '''1. Beautiful is better than ugly.
3.   Simple is better than complex.
4. Complicatedf is better than complex.
5. Flat is better than nested.
6. Cat is better.
ahoj\tbeta
bravo\tdelta
beat\tfero
'''.splitlines(keepends=True)

    rows = compute_diff(text1, text2)
    urwid.MainLoop(urwid.ListBox(rows), unhandled_input=unhandled, palette=palette).run()


if __name__ == '__main__':
    main()
