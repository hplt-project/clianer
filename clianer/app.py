#!/usr/bin/env python3

import urwid
import gzip
import os
import sys

from clianer.widgets.main_frame import ClianerFrame
from opuscleaner.filters import set_global_filters, list_filters


PALETTE = [(None,  "light gray", "dark blue"),
           ("heading", "white", "dark blue"),
           ("line", "light gray", "dark blue"),
           ("options", "black", "dark cyan"),
           ("options key", "light gray", "dark blue"),
           ("focus heading", "white", "dark red"),
           ("focus line", "white", "dark blue"),
           ("focus options", "black", "light gray"),
           ("filter", "light gray", "dark blue"),
           ("filter selected", "black", "dark cyan"),
           ("filter diff", "light green,bold", "dark blue"),
           ("filter diff selected", "light green,bold", "dark cyan"),
           ("shadow", "white", "black"),
           ("dialog shadow corner", "", ""),
           ("dialog heading", "yellow", "dark cyan"),
           ("dialog body", "white", "dark cyan"),
           ("dialog edit", "white", "dark blue"),
           ("dialog edit caption", "white", "dark cyan"),
           ("dialog edit focus", "yellow", "black"),
           ("button select", "yellow", "black"),
           ("button normal", "white", "dark cyan"),
           ("edit", "black", "dark cyan"),
           ("data", "black", "light gray"),
           ("focus data", "black", "dark cyan"),
           ("diffminus", "black", "light red"),
           ("diffplus", "black", "light green"),
           ("diffminus whole", "black", "light red"),
           ("diffplus whole", "black ", "light green"),
           ]



DATA_LOCATION = "/home/helcl/hplt/OpusCleaner/data/train-parts"

FILTERS_ROOT = "/home/helcl/hplt/OpusCleaner/opuscleaner"
FILTER_PATHS = os.pathsep.join([
    os.path.join(FILTERS_ROOT, "filters/**/*.json"),
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
        self.main_frame = ClianerFrame()

        set_global_filters(list_filters(FILTER_PATHS))

    def run(self):
        urwid.MainLoop(self.main_frame, PALETTE).run()
