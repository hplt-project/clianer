import asyncio
import urwid

from opuscleaner.server import get_sample
from opuscleaner.datasets import list_datasets
from opuscleaner.server import ParsedFilterOutput

from clianer.widgets.dataset_view import DatasetView
from clianer.widgets.filter_list import FilterList
from clianer.widgets.add_filter import AddFilterDialog, EditFilterDialog
from clianer.widgets.select_dataset import SelectDatasetDialog


class ClianerFrame(urwid.WidgetWrap):
    def __init__(self):
        self.dialog = None
        self.filter_list = FilterList()
        self.dataset = None
        self.datasetView = DatasetView()
        self.langs = ["en", "ga"]

        self.body = urwid.Columns([(40, self.filter_list), self.datasetView])
        self.header = urwid.AttrMap(urwid.Text("  File"), "options")

        self.footer = urwid.Columns([
            urwid.AttrMap(urwid.Text("F3: Add Filter"), "options"),
            urwid.AttrMap(urwid.Text("Q: Quit"), "options")
        ])

        self.top = urwid.Frame(
            self.body, header=self.header, footer=self.footer)

        super().__init__(self.top)

    def keypress(self, size, key):
        if key == "q" or key == "Q":
            if self.dialog is None:
                raise urwid.ExitMainLoop()

        if key == "f3":
            if self.dialog is None:
                self.openAddFilterDialog()

        if key == "f2":
            if self.dialog is None:
               self.openSelectDatasetDialog()

        if key == "f4":
            pass

        return super().keypress(size, key)

    def openDialog(self, widget, tag, callback, user_args=None):
        assert self.dialog is None
        self.dialog = tag
        self._w = widget.overlay(self._w)

        def callback_wrapper(widget, *args, **kwargs):
            assert widget is not None
            self.dialog = None
            urwid.disconnect_signal(
                self._w[1], "close", callback_wrapper)
            self._w = self._w[0]
            callback(widget, *args, **kwargs)

        urwid.connect_signal(
            self._w[1], "close", callback_wrapper)

    def openAddFilterDialog(self):
        widget = AddFilterDialog()
        self.openDialog(widget, "add_filter", self.addFilterDialogClosed)

    def openEditFilterDialog(self, filter_spec):
        widget = EditFilterDialog(filter_spec)
        self.openDialog(widget, "edit_filter", self.editFilterDialogClosed)

    def openSelectDatasetDialog(self):
        widget = SelectDatasetDialog()
        self.openDialog(widget, "sel_dataset", self.selectDatasetDialogClosed)

    def addFilterDialogClosed(self, widget, filter_spec):
        if filter_spec is not None:
            self.openEditFilterDialog(filter_spec)

    def editFilterDialogClosed(self, widget, filter_spec, filter_args,
                               filter_lang_is_src=None):
        if filter_args is not None:
            assert filter_spec is not None
            lang = None
            if filter_lang_is_src:
                lang = self.langs[0]
            if filter_lang_is_src is False:
                lang = self.langs[1]
            self.filter_list.add_filter(filter_spec, filter_args, lang)
            self.update_data()

    def selectDatasetDialogClosed(self, widget, dataset_name):
        if dataset_name is not None:
            # TODO ask to save filters
            # reset filters
            self.filter_list.clear_filters()
            self.open_dataset(dataset_name)

    def open_dataset(self, name):
        self.dataset = name
        self.update_data()

    def update_data(self):
        self.loaded_data = asyncio.run(self.load_data())
        self.datasetView.show(self.loaded_data[-1].stdout, title=self.dataset)

    async def load_data(self):
        filters = list(self.filter_list.get_filters())
        sample = get_sample(self.dataset, filters)
        return [ParsedFilterOutput(f) async for f in sample]
