#!/usr/bin/env python3

import argparse
import urwid
import gzip

from clianer.widgets.filter_list import FilterList

DATA_LOCATION = "/home/helcl/hplt/OpusCleaner/data/train-parts"


class App:

    def __init__(self, args):
        self.args = args
        a = []
        b = []

        with gzip.open(args.file1, "rt") as f_src, gzip.open(args.file2, "rt") as f_tgt:
            for i, (src, tgt) in enumerate(zip(f_src, f_tgt)):
                a.append(src.rstrip("\r\n"))
                b.append(tgt.rstrip("\r\n"))

                if i == 50:
                    break


        self.palette = [
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
        self.main_frame = urwid.Frame(app_body, urwid.Text("File"), urwid.Text("Status"))

    def run(self):
        urwid.MainLoop(self.main_frame, self.palette, unhandled_input=self.exit_on_q).run()


    def exit_on_q(self, key):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()
