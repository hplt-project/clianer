#!/usr/bin/env python3

import argparse
import urwid
import gzip

from clianer.widgets.main_frame import ClianerFrame, PALETTE

DATA_LOCATION = "/home/helcl/hplt/OpusCleaner/data/train-parts"

def get_datasets(location):
    datasets = []

    for root, _, paths in os.walk(location):
        for path in paths:
            filename = os.path.join(root, path)
            name = filename[len(location):]

            datasets.append(filename)

    return datasets


class App:
    def __init__(self, args):
        self.args = args
        self.main_frame = ClianerFrame(args.file1, args.file2)

    def run(self):
        urwid.MainLoop(self.main_frame, PALETTE).run()
