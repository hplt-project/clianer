import urwid

from clianer.widgets.dataset_view import DatasetView
from clianer.widgets.filter_list import FilterList
from clianer.widgets.add_filter import AddFilterDialog


PALETTE = [(None,  "black", "dark gray"),
           ("heading", "white", "dark gray"),
           ("line", "black", "light gray"),
           ("options", "light cyan", "black"),
           ("focus heading", "white", "dark red"),
           ("focus line", "black", "dark red"),
           ("focus options", "black", "light gray"),
           ("selected", "white", "dark blue")]

# FOCUS_MAP = {"heading": "focus heading",
#              "options": "focus options",
#              "line": "focus line"}


class ClianerFrame(urwid.WidgetWrap):
    def __init__(self, f1, f2):
        self.dialog_level = 0
        self.filterList = FilterList()
        self.datasetView = DatasetView(f1, f2)

        self.body = urwid.Columns([(40, self.filterList), self.datasetView])
        self.header = urwid.Text("File")

        self.footer = urwid.Columns([
            urwid.AttrMap(urwid.Text("F3: Add Filter"), "options"),
            urwid.AttrMap(urwid.Text("Q: Quit"), "options")
        ])

        self.top = urwid.Frame(
            self.body, header=self.header, footer=self.footer)

        super().__init__(self.top)

    def keypress(self, size, key):
        if key == "q" or key == "Q":
            if self.dialog_level == 0:
                raise urwid.ExitMainLoop()
            else:
                self.close_dialog()

        if key == "f3":
            self.open_dialog(AddFilterDialog(self), 30, 40)

        return super().keypress(size, key)


    def open_dialog(self, widget, height, width):
        self.dialog_level += 1
        self._w = urwid.Overlay(
            widget,
            self._w,
            align="center",
            width=width,
            valign="middle",
            height=height)
        urwid.connect_signal(self._w[1], "close", self.close_dialog)


    def close_dialog(self, widget=None, name=None):
        self.dialog_level -= 1
        urwid.disconnect_signal(self._w[1], "close", self.close_dialog)
        self._w = self._w[0]

        if widget is not None:
            assert name is not None
            flt = widget.available_filters[name]
            filter_params = {}
            if "parameters" in flt:
                for param in flt["parameters"]:
                    if "default" in flt["parameters"][param]:
                        filter_params[param] = str(
                            flt["parameters"][param]["default"])
                    else:
                        filter_params[param] = "None"

            self.filterList.add_filter(name, filter_params)
