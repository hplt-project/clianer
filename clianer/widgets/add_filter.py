import urwid

from clianer.filters import (get_global_filters, FilterParameter,
                             FilterParameterTuple, FilterParameterList)

class AddFilterDialog(urwid.WidgetWrap):
    """Dialog overlay that lets user choose which filter to add"""

    def __init__(self):
        self.available_filters = get_global_filters()

        self.buttons = []
        for name, filter_spec in self.available_filters.items():
            self.buttons.append(
                urwid.Button(filter_spec.name, on_press=self.add_filter,
                             user_data=filter_spec))

        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker(self.buttons))
        self.top = urwid.LineBox(self.listbox, title="New filter")

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(self.top)

    def add_filter(self, button, filter_obj):
        self._emit("close", filter_obj)

    def keypress(self, size, key):
        if key == "esc":
            self._emit("close", None)
        else:
            return super().keypress(size, key)


class EditFilterDialog(urwid.WidgetWrap):

    def __init__(self, filter_spec):
        self.filter_spec = filter_spec

        description = "No filter description provided"
        if filter_spec.description:
            description = filter_spec.description
        self.description_widget = urwid.Text(description)

        self.filter_args = {}
        self.parameter_widget_list = []
        if filter_spec.parameters:
            for name, param in filter_spec.parameters.items():
                self._add_parameter_widgets(name, param)

        if self.parameter_widget_list:
            self.parameters_widget = urwid.Pile(self.parameter_widget_list)
        else:
            self.parameters_widget = urwid.Text("No editable parameters")

        self.top = urwid.LineBox(
            urwid.ListBox([
                self.description_widget,
                urwid.Divider(),
                self.parameters_widget,
                urwid.Divider(),
                urwid.Columns([
                    urwid.Button("OK", on_press=self.save),
                    urwid.Button("Cancel", on_press=self.cancel)])]),
            title=self.filter_spec.name)

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(self.top)

    def _add_parameter_widgets(self, name: str, param: FilterParameter):
        self.parameter_widget_list.append(urwid.Text(name, align="left"))
        if param.help:
            self.parameter_widget_list.append(
                urwid.Text(param.help, align="left"))

        if isinstance(param, FilterParameterTuple):
            for subparam in param.parameters:
                self._add_parameter_widgets(subparam)

        if isinstance(param, FilterParameterList):
            # TODO add button to add new items to list
            for subparam in param.parameters:
                self._add_parameter_widgets(subparam)

        # TODO handle different types of parameters
        editor = urwid.Edit("", str(param.default), align="right")
        self.filter_args[name] = editor

        self.parameter_widget_list.append(editor)
        self.parameter_widget_list.append(urwid.Divider())

    def keypress(self, size, key):
        if key == "esc":
            self.cancel(None)
        if key == "enter":
            self.save(None)
        else:
            return super().keypress(size, key)

    def save(self, button):
        self._emit("close", self.filter_spec,
                   {k: v.get_edit_text() for k, v in self.filter_args.items()})

    def cancel(self, button):
        self._emit("close", self.filter_spec, None)
