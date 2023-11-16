#!/usr/bin/env python3

import urwid
import gzip
import os
import sys

from clianer.widgets.main_frame import ClianerFrame
from opuscleaner.filters import set_global_filters, list_filters


PALETTE = [(None,  "light gray", "black"),
           ("heading", "white", "black"),
           ("line", "light gray", "black"),
           ("options", "light cyan", "black"),
           ("focus heading", "white", "dark red"),
           ("focus line", "white", "black"),
           ("focus options", "black", "light gray"),
           ("selected", "white", "dark blue")]

DATA_LOCATION = "/home/helcl/hplt/OpusCleaner/data/train-parts"

FILTERS_ROOT = "/home/helcl/hplt/OpusCleaner/opuscleaner"
FILTER_PATHS = os.pathsep.join([
    os.path.join(FILTERS_ROOT, "filters**/*.json"),
    os.path.join(os.path.dirname(__file__), "filters/**/*.json")
])


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

        set_global_filters(list_filters(FILTER_PATHS))

    def run(self):
        urwid.MainLoop(self.main_frame, PALETTE).run()
