#!/usr/bin/env python3

import argparse
import urwid
import gzip
import json
import os


FILTERS_LOCATION = "/home/helcl/hplt/OpusCleaner/opuscleaner/filters/"
DATA_LOCATION = "/home/helcl/hplt/OpusCleaner/data/train-parts"

def get_filters(location=FILTERS_LOCATION):
    """Returns a list of filters from the given location and its subdirectories"""
    filters = {}

    for root, _, paths in os.walk(location):

        for path in paths:
            filename = os.path.join(root, path)
            if path.endswith(".json"):
                name = filename[len(location):].replace("/", ".").replace(".json", "")

                # parse the json
                with open(os.path.join(root, path), "r") as f:
                    filter_cfg = json.load(f)
                    filters[name] = filter_cfg

    return filters


class FilterItem(urwid.WidgetWrap):
    def __init__(self, caption):
        self.caption = caption
        self.header = FilterItemHeader(caption, self.toggle_body)
        self.body = FilterItemBody({"option": "value", "option2": "32"})

        self.expanded = False
        self.collapsed_top = self.header
        self.expanded_top = urwid.Pile([self.header, self.body])

        super().__init__(self.collapsed_top)


    def toggle_body(self):
        self.expanded = not self.expanded
        self.header.set_expanded(self.expanded)

        if self.expanded:
            self._w = self.expanded_top
        else:
            self._w = self.collapsed_top



class FilterItemHeader(urwid.Button):
    def __init__(self, caption, callback=None):
        super().__init__("")
        self.callback = callback

        self.caption = caption
        self.icon = urwid.SelectableIcon(" ", 1)
        self.set_expanded(False)

        self._w = urwid.AttrMap(self.icon, None, "selected")
        urwid.connect_signal(self, "click", self.on_toggle_click)

    def on_toggle_click(self, *args):
        self.icon.set_text("aaa")
        if self.callback:
            self.callback()

    def set_expanded(self, expanded):
        if expanded:
            self.icon.set_text("[-] " + self.caption)
        else:
            self.icon.set_text("[+] " + self.caption)


class FilterItemBody(urwid.WidgetWrap):
    def __init__(self, filterOptions):

        cols = []
        for opt, val in filterOptions.items():
            cols.append(urwid.Columns([urwid.Text(opt), urwid.Text(val)]))

        self.top = urwid.Pile(cols)
        super().__init__(self.top)


class FilterList(urwid.WidgetWrap):
    def __init__(self):

        filter_names = list(get_filters().keys())
        filters_content = []
        for filter_name in filter_names:
            filters_content.append(FilterItem(filter_name))

        top = urwid.ListBox(filters_content)
        super().__init__(top)

def exit_on_q(key):
    if key in ("q", "Q"):
        raise urwid.ExitMainLoop()


def main(args):
    a = []
    b = []

    with gzip.open(args.file1, "rt") as f_src, gzip.open(args.file2, "rt") as f_tgt:
        for i, (src, tgt) in enumerate(zip(f_src, f_tgt)):
            a.append(src.rstrip("\r\n"))
            b.append(tgt.rstrip("\r\n"))

            if i == 50:
                break

    # col_content = []
    # left_col = []
    # right_col = []
    # for src, tgt in zip(a, b):
    #     left_col.append(urwid.Text(src))
    #     right_col.append(urwid.Text(tgt))

    #     # listbox_content.append(urwid.Columns([urwid.Filler(urwid.Text(src), "top"), urwid.Filler(urwid.Text(tgt), valign="top")], box_columns=[0, 1]))

    # leftbox = urwid.ListBox(left_col)
    # rightbox = urwid.ListBox(right_col)
    # cols = urwid.Columns([leftbox, rightbox], dividechars=1)
    # loop = urwid.MainLoop(cols, unhandled_input=exit_on_q)

    palette = [
        (None,  'black', 'dark gray'),
        ('heading', 'white', 'dark gray'),
        ('line', 'black', 'light gray'),
        ('options', 'dark gray', 'black'),
        ('focus heading', 'white', 'dark red'),
        ('focus line', 'black', 'dark red'),
        ('focus options', 'black', 'light gray'),
        ('selected', 'white', 'dark blue')]
    focus_map = {
        'heading': 'focus heading',
        'options': 'focus options',
        'line': 'focus line'}

    list_content = []
    #list_content.append(urwid.Columns([urwid.Text("English"), urwid.Text("Irish")]))
    #list_content.append(urwid.Divider("="))
    for src, tgt in zip(a, b):
        list_content.append(urwid.Columns([urwid.Text(src), urwid.Text(tgt)], dividechars=1))
        list_content.append(urwid.Divider("-"))

    listbox = urwid.ListBox(list_content)

    # here's the line char: ─
    app_body = urwid.Columns([(40, urwid.LineBox(FilterList())), urwid.LineBox(listbox, title="/placeholder/path.en-ga.gz", title_attr="heading")])
    main_frame = urwid.Frame(app_body, urwid.Text("File"), urwid.Text("Status"))

    loop = urwid.MainLoop(main_frame, palette, unhandled_input=exit_on_q)
    loop.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file1")
    parser.add_argument("file2")
    args = parser.parse_args()
    main(args)
