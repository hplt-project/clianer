import json
import os
import urwid

FILTERS_LOCATION = "/home/helcl/hplt/OpusCleaner/opuscleaner/filters/"


def get_filters(location=FILTERS_LOCATION):
    """Returns a list of filters from the given location and its subdirectories"""
    filters = {}

    for root, _, paths in os.walk(location):

        for path in paths:
            filename = os.path.join(root, path)
            if path.endswith(".json"):
                name = filename[len(location):].replace("/", ".").replace(".json", "")

                # parse the json
                with open(os.path.join(root, path), "r") as f:
                    filter_cfg = json.load(f)
                    filters[name] = filter_cfg

    return filters


class AddFilterDialog(urwid.WidgetWrap):
    """Dialog overlay that lets user choose which filter to add"""

    def __init__(self, parent):
        self.available_filters = get_filters()

        self.buttons = []
        for filter_name in self.available_filters.keys():
            self.buttons.append(urwid.Button(
                filter_name, on_press=self.add_filter, user_data=filter_name))

        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker(self.buttons))

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(urwid.LineBox(self.listbox, title="New filter"))

    def add_filter(self, button, filter_name):
        # just close and return focus to parent
        self._emit("close", filter_name, self.available_filters[filter_name])

    def keypress(self, size, key):
        if key == "esc":
            self._emit("close", None, None)
        else:
            return super().keypress(size, key)


class EditFilterDialog(urwid.WidgetWrap):

    def __init__(self, parent, filter_name, filter_cfg):

        self.filter_name = filter_name
        description = "No filter description provided"
        if "description" in filter_cfg:
            description = filter_cfg["description"]
        self.description_widget = urwid.Text(description)

        self.filter_args = {}
        if "parameters" in filter_cfg:
            widget_list = []
            for param_name in filter_cfg["parameters"]:
                param = filter_cfg["parameters"][param_name]

                # type, default, required, help
                widget_list.append(urwid.Text(param_name, align="left"))

                if "help" in param:
                    widget_list.append(urwid.Text(param["help"], align="left"))

                editor = urwid.Edit("", str(param["default"]), align="right")
                self.filter_args[param_name] = editor

                widget_list.append(editor)
                widget_list.append(urwid.Divider())

            self.parameters_widget = urwid.Pile(widget_list)
        else:
            self.parameters_widget = urwid.Text("No editable parameters")

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(urwid.LineBox(urwid.ListBox([
            self.description_widget,
            urwid.Divider(),
            self.parameters_widget,
            urwid.Divider(),
            urwid.Columns([urwid.Button("OK", on_press=self.save),
                           urwid.Button("Cancel", on_press=self.cancel)])]), title=filter_name))

    def keypress(self, size, key):
        if key == "esc":
            self.cancel(None)
        if key == "enter":
            self.save(None)
        else:
            return super().keypress(size, key)

    def save(self, button):
        self._emit("close", self.filter_name,
                   {k: v.get_edit_text() for k, v in self.filter_args.items()})

    def cancel(self, button):
        self._emit("close", self.filter_name, None)
