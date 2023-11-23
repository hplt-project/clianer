from typing import List
import urwid

from opuscleaner.filters import FilterStep, FilterType


class FilterItem(urwid.WidgetWrap):
    def __init__(self, filter_spec, filter_args, filter_lang=None):
        self.caption = filter_spec.name
        self.header = FilterItemHeader(filter_spec.name, self.toggle_body)
        self.body = FilterItemBody(filter_args, filter_lang)

        self.expanded = False
        self.collapsed_top = self.header
        self.expanded_top = urwid.Pile([self.header, self.body])

        super().__init__(self.collapsed_top)


    def toggle_body(self):
        self.expanded = not self.expanded
        self.header.set_expanded(self.expanded)

        if self.expanded:
            self._w = self.expanded_top
        else:
            self._w = self.collapsed_top


class FilterItemHeader(urwid.Button):
    def __init__(self, caption, callback=None):
        super().__init__("")
        self.callback = callback

        self.caption = caption
        self.icon = urwid.SelectableIcon(" ", 1)
        self.set_expanded(False)

        self._w = urwid.AttrMap(self.icon, None, "selected")
        urwid.connect_signal(self, "click", self.on_toggle_click)

    def on_toggle_click(self, *args):
        if self.callback:
            self.callback()

    def set_expanded(self, expanded):
        if expanded:
            self.icon.set_text("[-] " + self.caption)
        else:
            self.icon.set_text("[+] " + self.caption)


class FilterItemBody(urwid.WidgetWrap):
    def __init__(self, filter_params, mono_lang=None):

        cols = []
        if mono_lang is not None:
            cols.append(urwid.Text("Language: " + mono_lang, align="left"))
            cols.append(urwid.Divider())

        for opt, val in filter_params.items():
            cols.append(urwid.Pile([urwid.Text(opt, align="left"),
                                    urwid.Text(str(val), align="right")]))

        self.top = urwid.Pile(cols)
        super().__init__(self.top)


class FilterList(urwid.WidgetWrap):
    def __init__(self, filters=None):
        self.listWalker = urwid.SimpleListWalker([])
        self.top = urwid.LineBox(
            urwid.ListBox(self.listWalker),
            title="Filters", title_attr="heading", title_align="left")

        self.filters = []
        if filters is not None:
            for filter_step in filters:
                self.add_filter(filter_step)

        super().__init__(self.top)

    def add_filter(self, filter_spec, filter_args, filter_lang):
        self.filters.append((filter_spec, filter_args, filter_lang))
        self.listWalker.append(
            FilterItem(filter_spec, filter_args, filter_lang))

    def get_filters(self):
        for (filter_spec, filter_args, filter_lang) in self.filters:
            if filter_spec.type == FilterType.MONOLINGUAL:
                yield FilterStep(filter=filter_spec.name,
                                 parameters=filter_args, language=filter_lang)
            else:
                yield FilterStep(filter=filter_spec.name,
                                 parameters=filter_args)

    def clear_filters(self):
        self.filters = []
        self.listWalker.clear()
