from typing import Any, Dict

import urwid

from clianer.widgets.button import CustomButton
from clianer.widgets.dialog import Dialog
from opuscleaner.filters import (get_global_filters, FilterParameter,
                                 FilterParameterTuple, FilterParameterList,
                                 FilterType)


class AddFilterDialog(Dialog):
    """Dialog overlay that lets user choose which filter to add"""

    def __init__(self):
        self.available_filters = get_global_filters()

        self.buttons = []
        for name, filter_spec in self.available_filters.items():
            self.buttons.append(
                CustomButton(filter_spec.name, on_press=self.add_filter,
                             user_data=filter_spec))

        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker(self.buttons))
        #self.top = urwid.LineBox(self.listbox, title="New filter")

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(self.listbox, "New filter", width=50, height=35)

    def add_filter(self, button, filter_obj):
        self._emit("close", filter_obj)


class EditFilterDialog(Dialog):

    def __init__(self, filter_spec):
        self.filter_spec = filter_spec

        description = "No filter description provided"
        if filter_spec.description:
            description = filter_spec.description
        self.description_widget = urwid.Text(description)

        self.filter_args: Dict[str, Any] = {}

        self.mono_lang_selector = []
        self.filter_type_widget_list = []
        if filter_spec.type == FilterType.MONOLINGUAL:
            self.filter_type_widget_list.append(urwid.Text("Language for monolingual filter:"))
            self.mono_lang_selector = []
            urwid.RadioButton(self.mono_lang_selector, "Source")
            urwid.RadioButton(self.mono_lang_selector, "Target")
            self.filter_type_widget_list.append(urwid.Columns(self.mono_lang_selector))
        if self.filter_type_widget_list:
            self.filter_type_widget = urwid.Pile(self.filter_type_widget_list)
        else:
            self.filter_type_widget = urwid.Text("Bilingual filter")

        self.parameter_widget_list = []
        if filter_spec.parameters:
            for name, param in filter_spec.parameters.items():
                self._add_parameter_widgets(name, param)

        if self.parameter_widget_list:
            self.parameters_widget = urwid.Pile(self.parameter_widget_list)
        else:
            self.parameters_widget = urwid.Text("No editable parameters")

        self.cancel_button = CustomButton("Cancel", on_press=self.cancel, align="center")
        self.ok_button = CustomButton("OK", on_press=self.save, align="center")
        self.buttons = urwid.Padding(
            urwid.Columns([self.ok_button, self.cancel_button], 4), "center")

        self.top = urwid.ListBox([
            self.description_widget,
            urwid.Divider(),
            self.filter_type_widget,
            urwid.Divider(),
            self.parameters_widget,
            urwid.Divider(),
            self.buttons])

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(self.top, self.filter_spec.name, width=60, height=40)

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
        editor = urwid.AttrMap(editor, "dialog edit")

        self.parameter_widget_list.append(editor)
        self.parameter_widget_list.append(urwid.Divider())

    def keypress(self, size, key):
        if key == "esc":
            self.cancel(None)
        if key == "enter":
            # unless focus is on a button, save
            focus = self.top.get_focus_widgets()[-1]
            if focus == self.cancel_button:
                self.cancel(None)
            else:
                self.save(None)
        else:
            return super().keypress(size, key)

    def save(self, button):
        self._emit("close", self.filter_spec,
                   {k: v.get_edit_text() for k, v in self.filter_args.items()},
                   self.mono_lang_selector[0].state if self.mono_lang_selector else None)

    def cancel(self, button):
        self._emit("close", self.filter_spec, None)
