import urwid

from clianer.widgets.dataset_view import DatasetView
from clianer.widgets.filter_list import FilterList
from clianer.widgets.add_filter import AddFilterDialog, EditFilterDialog
from clianer.widgets.select_dataset import SelectDatasetDialog
from clianer.data import ParallelDataset


class ClianerFrame(urwid.WidgetWrap):
    def __init__(self):
        self.dialog = None
        self.filterList = FilterList()
        self.datasetView = DatasetView()
        self.langs = ["en", "ga"]

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

        if key == "f2":
            if self.dialog is None:
               self.openSelectDatasetDialog()

            # from opuscleaner.server import get_sample
            # from opuscleaner.datasets import list_datasets

            # filters = list(self.filterList.get_filters())
            # name = "ELRC-3456-EC_EUROPA_covid-v1.en-ga"
            # s = get_sample(name, filters)

            # async def get_():
            #     return [output async for output in s]

            # import asyncio
            # ss = asyncio.run(get_())


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
            self.filterList.add_filter(filter_spec, filter_args, lang)

    def selectDatasetDialogClosed(self, widget, dataset_cfg):
        # datasets: Dict[str, List[Tuple[str, Path]]]
        # {name -> [(lang, path)]}

        if dataset_cfg is not None:
            # TODO handle also monolingual datasets (and more than 2 langs)
            assert len(dataset_cfg[1]) == 2

            (p_src, p_tgt) = dataset_cfg[1][0][1], dataset_cfg[1][1][1]

            self.datasetView.set_dataset(ParallelDataset(p_src, p_tgt, dataset_cfg[0]))
            self.langs = [dataset_cfg[1][0][0], dataset_cfg[1][1][0]]
