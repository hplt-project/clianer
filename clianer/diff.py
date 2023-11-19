#!/usr/bin/env python3
from difflib import Differ
import urwid
from typing import List, Tuple
import pudb

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

    hunk.plusinfo = hunk.plusinfo.ljust(len(hunk.plus), " ")
    hunk.minusinfo = hunk.minusinfo.ljust(len(hunk.minus), " ")

    assert len(hunk.plusinfo) == len(hunk.plus)
    assert len(hunk.minusinfo) == len(hunk.minus)

    assert hunk.plusinfo.count("^") == hunk.minusinfo.count("^")
    assert hunk.plusinfo.count(" ") == hunk.minusinfo.count(" ")

    start_common = 0
    common_length = 0

    finished = False
    while not finished:

        plus_instr = hunk.plusinfo[plus_index]
        minus_instr = hunk.minusinfo[minus_index]

        assert not (plus_instr == "+" and minus_instr == "-")
        assert not (plus_instr == "^" and minus_instr == " ")
        assert not (plus_instr == " " and minus_instr == "^")

        if plus_instr == "+":
            if common_length > 0:
                spans.append((None, hunk.plus[start_common:plus_index]))
                common_length = 0

            start = plus_index
            while hunk.plusinfo[plus_index] == "+":
                plus_index += 1
            spans.append(("diffplus", hunk.plus[start:plus_index]))

        elif minus_instr == "-":
            if common_length > 0:
                spans.append((None, hunk.plus[start_common:plus_index]))
                common_length = 0

            start = minus_index
            while hunk.minusinfo[minus_index] == "-":
                minus_index += 1
            spans.append(("diffminus", hunk.minus[start:minus_index]))

        elif plus_instr == "^":  # implies minus_instr == "^"
            if common_length > 0:
                spans.append((None, hunk.plus[start_common:plus_index]))
                common_length = 0

            start_plus = plus_index
            start_minus = minus_index

            while hunk.plusinfo[plus_index] == "^":
                assert hunk.minusinfo[minus_index] == "^"
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
            assert op_state == 0 or op_state == 1

            if op_state == 0:
                assert hunk is None
                rows.append(urwid.Text(("diffplus whole", content)))

            if op_state == 1:
                assert hunk is not None
                hunk.plus = content
                op_state = 2

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
'''.splitlines(keepends=True)

    text2 = '''1. Beautiful is better than ugly.
3.   Simple is better than complex.
4. Complicatedf is better than complex.
5. Flat is better than nested.
6. Cat is better.
'''.splitlines(keepends=True)


    rows = compute_diff(text1, text2)
    urwid.MainLoop(urwid.ListBox(rows), unhandled_input=unhandled, palette=palette).run()



def unused():

    text1 = '''1. Beautiful is better than ugly.
2. Explicit is better than implicit.
3. Simple is better than complex.
4. Complexy is better than complicated.
6. Cat is better than dog.
'''.splitlines(keepends=True)

    text2 = '''1. Beautiful is better than ugly.
3.   Simple is better than complex.
4. Complicatedf is better than complex.
5. Flat is better than nested.
6. Cat is better.
'''.splitlines(keepends=True)

    d = Differ()


    rows = []

    import itertools
    prev = None
    for line in itertools.chain(d.compare(text1, text2),  [" "]):
        line = line.rstrip("\r\n")

        if prev is None:
            prev = line
            continue

        if prev[0] == "?":
            prev = line
            continue



        # # if prev starts with "+", it belongs to the right
        # if prev[0] == "+":



        # if line starts with "?", we need to adapt the markup
        if line[0] == "?":
            assert prev[0] == "+" or prev[0] == "-"
            global_mode = "diffplus whole" if prev[0] == "+" else "diffminus whole"

            string = prev[2:].rstrip("\r\n")
            instructions = line[2:].rstrip("\r\n")

            texts = []

            start = 0
            mode = None
            for i, c in enumerate(instructions):
                if c == " ":
                    if mode == "-":
                        texts.append(("diffminus", string[start:i]))
                        start = i
                    if mode == "+":
                        texts.append(("diffplus", string[start:i]))
                        start = i
                    mode = None

                if c == "-":
                    if mode == "+":
                        texts.append(("diffplus", string[start:i]))
                        start = i
                    if mode is None:
                        texts.append((global_mode, string[start:i]))
                        start = i
                    mode = c

                if c == "+":
                    if mode == "-":
                        texts.append(("diffminus", string[start:i]))
                        start = i
                    if mode is None:
                        texts.append((global_mode, string[start:i]))
                        start = i
                    mode = c

                if c == "^":
                    assert mode is None
                    texts.append((global_mode, string[start:i]))
                    texts.append(("diffminus", string[i]))
                    start = i + 1

            if mode == "-":
                texts.append(("diffminus", string[start:i]))
            if mode == "+":
                texts.append(("diffplus", string[start:i]))
            if mode is None:
                texts.append((global_mode, string[start:i]))

            if len(string) > len(instructions):
                texts.append((global_mode, string[len(instructions):]))

            rows.append(urwid.Text(texts))
            prev = line
            continue

        if prev[0] == "+":
            rows.append(urwid.Text(("diffplus whole", prev[2:])))

        # if it starts with a "-", it belongs to the left
        if prev[0] == "-":
            rows.append(urwid.Text(("diffminus whole", prev[2:])))

        # if it starts with a " ", it belongs to both
        if prev[0] == " ":
            rows.append(urwid.Text(prev[2:]))
            #rows.append(urwid.Text(prev))

        prev = line



    urwid.MainLoop(urwid.ListBox(rows), unhandled_input=unhandled, palette=palette).run()



if __name__ == '__main__':
    main()
