import urwid

from clianer.widgets.dataset_view import DatasetView
from clianer.widgets.filter_list import FilterList
from clianer.widgets.add_filter import AddFilterDialog, EditFilterDialog
from clianer.data import ParallelDataset


class ClianerFrame(urwid.WidgetWrap):
    def __init__(self, f1, f2):
        self.dialog = None
        self.filterList = FilterList()
        self.datasetView = DatasetView(ParallelDataset(f1, f2))

        self.body = urwid.Columns([(40, self.filterList), self.datasetView])
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

        # if key == "f2":
        #     if self.dialog is None:
        #         self.openSelectDatasetDialog()

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

    def addFilterDialogClosed(self, widget, filter_spec):
        if filter_spec is not None:
            self.openEditFilterDialog(filter_spec)

    def editFilterDialogClosed(self, widget, filter_spec, filter_args):
        if filter_args is not None:
            assert filter_spec is not None
            self.filterList.add_filter(filter_spec.name, filter_args)
