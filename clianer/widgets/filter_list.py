from typing import List
import urwid

from opuscleaner.filters import FilterStep, FilterType


COLLAPSED_ICON = "[+]"
EXPANDED_ICON = "[-]"
EMPTY_ICON = "[ ]"


class FilterItem(urwid.WidgetWrap):
    def __init__(self, filter_spec, filter_args, filter_lang=None):
        self.caption = filter_spec.name
        self.body = FilterItemBody(filter_args, filter_lang)

        icon = COLLAPSED_ICON if not self.body.empty else EMPTY_ICON

        self.header = urwid.SelectableIcon(
            icon + " " + self.caption, cursor_position=1)

        styled_header = urwid.AttrMap(self.header, None, "selected")

        self.expanded = False
        self.collapsed_top = styled_header
        self.expanded_top = urwid.Pile([styled_header, self.body])

        super().__init__(self.collapsed_top)

    def toggle_body(self):
        self.expanded = not self.expanded

        icon = EXPANDED_ICON if self.expanded else COLLAPSED_ICON
        icon = icon if not self.body.empty else EMPTY_ICON

        self.header.set_text(icon + " " + self.caption)
        self._w = self.expanded_top if self.expanded else self.collapsed_top

    def keypress(self, size, key):
        if key == "tab" or key == "enter" or key == " ":
            self.toggle_body()

        return super().keypress(size, key)


class FilterItemBody(urwid.WidgetWrap):
    def __init__(self, filter_params, mono_lang=None):

        cols = []
        self.empty = True
        if mono_lang is not None:
            cols.append(urwid.Text("Language: " + mono_lang, align="left"))
            cols.append(urwid.Divider())
            self.empty = False

        for opt, val in filter_params.items():
            cols.append(urwid.Pile([urwid.Text(opt, align="left"),
                                    urwid.Text(str(val), align="right")]))
            self.empty = False

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

    def update_filter(self, filter_index, filter_spec, filter_args,
                      filter_lang):
        self.filters[filter_index] = (filter_spec, filter_args, filter_lang)
        self.listWalker[filter_index] = FilterItem(
            filter_spec, filter_args, filter_lang)

    def remove_filter(self, filter_index):
        self.filters.remove(filter_item)
        self.listWalker.remove(filter_index)

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

    def get_focused_filter_index(self):
        return self.listWalker.get_focus()[1]

    def keypress(self, size, key):
        if key == "f8":
            #self.listWalker[self.listWalker.focus_position]
            pass

        return super().keypress(size, key)
