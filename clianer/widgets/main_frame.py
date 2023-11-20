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

        self.footer = urwid.AttrMap(urwid.Columns([
            urwid.Text([("options key", "F2"), "Select Dataset"]),
            urwid.Text([("options key", "F3"), "Add Filter"]),
            urwid.Text([("options key", "F4"), "Diff"]),
            urwid.Text([("options key", "F5"), "Original"]),
            urwid.Text([("options key", "F6"), "Cleaned"]),
            urwid.Text([("options key", "F10"), "Quit"])
        ]), "options")

        self.top = urwid.Frame(
            self.body, header=self.header, footer=self.footer)

        super().__init__(self.top)

    def keypress(self, size, key):
        if key == "q" or key == "Q" or key == "f10":
            if self.dialog is None:
                raise urwid.ExitMainLoop()

        if key == "f3":
            if self.dialog is None:
                self.openAddFilterDialog()

        if key == "f2":
            if self.dialog is None:
               self.openSelectDatasetDialog()

        if key == "f4":
            self.show_diff(0, -1)

        if key == "f5":
            self.show_orig()

        if key == "f6":
            self.show_clean()

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

    def show_orig(self):
        self.datasetView.show(self.loaded_data[0].stdout, title=self.dataset)

    def show_clean(self):
        self.datasetView.show(self.loaded_data[-1].stdout, title=self.dataset)

    def show_diff(self, rev1, rev2):
        #assert rev1 < rev2
        #assert rev1 >= 0
        assert rev1 < len(self.loaded_data)
        assert rev2 < len(self.loaded_data)

        rev1_data = self.loaded_data[rev1].stdout
        rev2_data = self.loaded_data[rev2].stdout

        rev1_src = [item[self.langs[0]] for item in rev1_data]
        rev1_tgt = [item[self.langs[1]] for item in rev1_data]
        rev2_src = [item[self.langs[0]] for item in rev2_data]
        rev2_tgt = [item[self.langs[1]] for item in rev2_data]

        self.datasetView.show_diff(
            rev1_src, rev1_tgt, rev2_src, rev2_tgt, title=self.dataset)

    def update_data(self):
        self.loaded_data = asyncio.run(self.load_data())
        self.datasetView.show(self.loaded_data[-1].stdout, title=self.dataset)

    async def load_data(self):
        filters = list(self.filter_list.get_filters())
        sample = get_sample(self.dataset, filters)
        return [ParsedFilterOutput(f) async for f in sample]
