from decimal import Decimal
from typing import Any, Dict

import urwid
import urwid.numedit

from clianer.widgets.button import CustomButton
from clianer.widgets.dialog import Dialog
from opuscleaner.filters import (
    get_global_filters, FilterParameter, FilterParameterTuple,
    FilterParameterList, FilterType, FilterParameterFloat, FilterParameterInt,
    FilterParameterBool, FilterParameterStr)


class AddFilterDialog(Dialog):
    """Dialog overlay that lets user choose which filter to add"""

    def __init__(self):
        self.available_filters = get_global_filters()

        self.buttons = []
        for name, filter_spec in sorted(
                self.available_filters.items(), key=lambda x: x[0]):
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

    def __init__(self, filter_spec, default_args=None, default_lang_src=None):
        self.filter_spec = filter_spec
        self.default_args = default_args
        self.default_lang_src = default_lang_src

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
            rsrc = urwid.RadioButton(self.mono_lang_selector, "Source")
            rtgt = urwid.RadioButton(self.mono_lang_selector, "Target")

            if self.default_lang_src is not None:
                if self.default_lang_src:
                    rsrc.set_state(True)
                else:
                    rtgt.set_state(True)

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
        #self.parameter_widget_list.append(urwid.Text(name, align="left"))

        if isinstance(param, FilterParameterTuple):
            for subparam in param.parameters:
                self._add_parameter_widgets(subparam)

        if isinstance(param, FilterParameterList):
            # TODO add button to add new items to list
            for subparam in param.parameters:
                self._add_parameter_widgets(subparam)

        if isinstance(param, FilterParameterFloat):
            # if param.default is not None:
            #     editor = urwid.numedit.FloatEdit(
            #         ("dialog edit caption", name + " "),
            #         Decimal(param.default))
            # else:
            #     editor = urwid.numedit.FloatEdit(
            #         ("dialog edit caption", name + " "))
            # getter = lambda e=editor: float(e.value())

            if self.default_args is not None:
                editor = urwid.Edit(("dialog edit caption", name + ": "),
                                    str(self.default_args[name]))
            elif param.default is not None:
                editor = urwid.Edit(("dialog edit caption", name + ": "),
                                    str(param.default))
            else:
                editor = urwid.Edit(("dialog edit caption", name + ": "))

            getter = editor.get_edit_text
            editor = urwid.AttrMap(editor, "dialog edit", "dialog edit focus")

        if isinstance(param, FilterParameterInt):
            if self.default_args is not None:
                editor = urwid.IntEdit(("dialog edit caption", name + " "),
                                       self.default_args[name])
            else:
                editor = urwid.IntEdit(("dialog edit caption", name + " "),
                                       param.default)
            getter = editor.value
            editor = urwid.AttrMap(editor, "dialog edit", "dialog edit focus")

        if isinstance(param, FilterParameterBool):
            if self.default_args is not None:
                editor = urwid.CheckBox(name, bool(self.default_args[name]))
            elif param.default is not None:
                editor = urwid.CheckBox(name, param.default)
            else:
                editor = urwid.CheckBox(name)
            getter = editor.get_state
            editor = urwid.AttrMap(editor, "dialog body", "dialog edit focus")

        if isinstance(param, FilterParameterStr):
            if self.default_args is not None:
                editor = urwid.Edit(("dialog edit caption", name + ": "),
                                    self.default_args[name])
            elif param.default is not None:
                editor = urwid.Edit(("dialog edit caption", name + ": "),
                                    param.default)
            else:
                editor = urwid.Edit(("dialog edit caption", name + ": "))
            getter = editor.get_edit_text
            editor = urwid.AttrMap(editor, "dialog edit", "dialog edit focus")

        if param.help:
           self.parameter_widget_list.append(
               urwid.Text(param.help, align="left"))

        self.filter_args[name] = getter

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
                   {k: v() for k, v in self.filter_args.items()},
                   self.mono_lang_selector[0].state if self.mono_lang_selector else None)

    def cancel(self, button):
        self._emit("close", self.filter_spec, None)
