import asyncio
import urwid

from opuscleaner.server import get_sample
from opuscleaner.datasets import list_datasets
from opuscleaner.server import ParsedFilterOutput

from clianer.widgets.dataset_view import DatasetView
from clianer.widgets.filter_list import FilterList
from clianer.widgets.add_filter import AddFilterDialog, EditFilterDialog
from clianer.widgets.select_dataset import SelectDatasetDialog
from clianer.widgets.dialog import ErrorDialog


class ClianerFrame(urwid.WidgetWrap):
    def __init__(self):
        self.dialog = None
        self.filter_list = FilterList()
        self.dataset = None
        self.dataset_view = DatasetView()
        self.langs = ["en", "ga"]

        self.body = urwid.Columns([(40, self.filter_list), self.dataset_view])
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
            if self.body.get_focus_column() == 1:
                self.show_diff(0, -1)
            elif self.body.get_focus_column() == 0:
                index = self.filter_list.get_focused_filter_index()
                filter_spec, filter_args, filter_lang = \
                    self.filter_list.filters[index]
                self.openEditFilterDialog(
                    index, filter_spec, filter_args,
                    filter_lang == self.langs[0])

        if key == "f5":
            self.show_orig()

        if key == "f6":
            self.show_clean()

        return super().keypress(size, key)

    def openDialog(self, widget, tag, callback=None, user_args=None):
        assert self.dialog is None
        self.dialog = tag
        self._w = widget.overlay(self._w)

        def callback_wrapper(widget, *args, **kwargs):
            assert widget is not None
            self.dialog = None
            urwid.disconnect_signal(
                self._w[1], "close", callback_wrapper)
            self._w = self._w[0]
            if callback is not None:
                callback(widget, *args, **kwargs)

        urwid.connect_signal(
            self._w[1], "close", callback_wrapper)

    def openAddFilterDialog(self):
        widget = AddFilterDialog()

        def add_filter_closed(widget, filter_spec):
            if filter_spec is not None:
                self.openEditFilterDialog(None, filter_spec)

        self.openDialog(widget, "add_filter", add_filter_closed)

    def openEditFilterDialog(
            self, index, filter_spec, filter_args=None, filter_lang=None):
        widget = EditFilterDialog(filter_spec, filter_args, filter_lang)

        def edit_filter_closed(widget, filter_spec, filter_args,
                               filter_lang_is_src=None):
            if filter_args is not None:
                assert filter_spec is not None
                lang = None
                if filter_lang_is_src:
                    lang = self.langs[0]
                if filter_lang_is_src is False:
                    lang = self.langs[1]

                if index is None:
                    self.filter_list.add_filter(filter_spec, filter_args, lang)
                else:
                    self.filter_list.update_filter(
                        index, filter_spec, filter_args, lang)

                self.update_data()

        self.openDialog(widget, "edit_filter", edit_filter_closed)

    def openSelectDatasetDialog(self):
        widget = SelectDatasetDialog()
        self.openDialog(widget, "sel_dataset", self.selectDatasetDialogClosed)

    def openErrorDialog(self, error_msg):
        widget = ErrorDialog(error_msg)
        self.openDialog(widget, "error")

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
        self.dataset_view.show(self.loaded_data[0].stdout, title=self.dataset)

    def show_clean(self):
        self.dataset_view.show(self.loaded_data[-1].stdout, title=self.dataset)

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

        self.dataset_view.show_diff(
            rev1_src, rev1_tgt, rev2_src, rev2_tgt, title=self.dataset)

    def update_data(self):
        self.loaded_data = asyncio.run(self.load_data())

        for i in range(len(self.loaded_data)):
            if self.loaded_data[i].returncode != 0:
                self.openErrorDialog(self.loaded_data[i].stderr)
                return

        self.show_clean()

    async def load_data(self):
        filters = list(self.filter_list.get_filters())
        sample = get_sample(self.dataset, filters)
        return [ParsedFilterOutput(f) async for f in sample]
