import asyncio
import gzip
import urwid

from opuscleaner.server import get_sample
from opuscleaner.datasets import list_datasets
from opuscleaner.server import ParsedFilterOutput


class DatasetView(urwid.WidgetWrap):

    def __init__(self, filter_getter, dataset=None):
        self.filter_getter = filter_getter

        self.datacols = urwid.ListBox(urwid.SimpleFocusListWalker([]))
        if dataset is None:
            self.datacols.body.append(urwid.Text("Press F2 to load a dataset."))
        else:
            self.open_dataset(dataset)

        listbox = urwid.Padding(self.datacols, ("fixed left", 1), ("fixed right", 1))
        listbox = urwid.AttrMap(listbox, attr_map="data")

        name = dataset.name if dataset is not None else ""
        self.linebox = urwid.LineBox(
            listbox, title=f"Dataset: {name}",
            title_align="left", title_attr="heading")

        #self.linebox.title_widget = urwid.AttrMap(
        #    self.linebox.title_widget, attr_map="heading", focus_map="focus heading")

        super().__init__(self.linebox)

    def open_dataset(self, name):
        self.dataset = name
        self.datacols.body.clear()
        self.datacols.body.append(urwid.Text("Loading..."))
        parsed_sample = asyncio.run(self.load_data())
        self.datacols.body.clear()

        assert len(parsed_sample) == 1
        langs = parsed_sample[0].stdout[0].keys()
        assert len(langs) == 2
        src, tgt = langs

        for entry in parsed_sample[0].stdout:
            assert src in entry.keys() and tgt in entry.keys()
            cols = urwid.Columns(
                [urwid.Text(entry[src]), urwid.Text(entry[tgt])],
                dividechars=1)
            cols._selectable = True
            self.datacols.body.append(
                urwid.AttrMap(cols, attr_map="data", focus_map="focus data"))
            #list_content.append(urwid.Divider(" "))
            #list_content.append(urwid.Divider("─"))  # this is the line character


    async def load_data(self):
        filters = list(self.filter_getter())
        sample = get_sample(self.dataset, filters)
        return [ParsedFilterOutput(f) async for f in sample]
