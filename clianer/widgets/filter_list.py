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
            self.format_text(icon), cursor_position=1)

        self.styled_header = urwid.AttrMap(self.header, "filter", "filter selected")

        self.expanded = False
        self.diff = False
        self.collapsed_top = self.styled_header
        self.expanded_top = urwid.Pile([self.styled_header, self.body])

        super().__init__(self.collapsed_top)

    def toggle_body(self):
        self.expanded = not self.expanded

        icon = EXPANDED_ICON if self.expanded else COLLAPSED_ICON
        icon = icon if not self.body.empty else EMPTY_ICON

        self.header.set_text(self.format_text(icon))
        self._w = self.expanded_top if self.expanded else self.collapsed_top

    def toggle_diff(self):
        self.diff = not self.diff

        if self.diff:
            self.styled_header.set_attr_map({None: "filter diff"})
            self.styled_header.set_focus_map({None: "filter diff selected"})
        else:
            self.styled_header.set_attr_map({None: "filter"})
            self.styled_header.set_focus_map({None: "filter selected"})

    def format_text(self, icon):
        return icon + " " + self.caption

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

        self.diff_start = None
        self.diff_end = None

        self._enabled_signals = {"filter_update": True, "diff_update": True}

        urwid.register_signal(self.__class__, ["filter_update", "diff_update"])
        super().__init__(self.top)

    def set_signal_emit(self, signal, enable):
        self._enabled_signals[signal] = enable
        if enable:
            self._emit(signal)

    def _emit(self, signal):
        if self._enabled_signals[signal]:
            super()._emit(signal)

    def add_filter(self, filter_spec, filter_args, filter_lang):
        self.untoggle_all_diffs()
        self.filters.append((filter_spec, filter_args, filter_lang))
        self.listWalker.append(
            FilterItem(filter_spec, filter_args, filter_lang))

    def update_filter(self, filter_index, filter_spec, filter_args,
                      filter_lang):
        self.filters[filter_index] = (filter_spec, filter_args, filter_lang)
        self.listWalker[filter_index] = FilterItem(
            filter_spec, filter_args, filter_lang)
        self._emit("filter_update")

    def remove_filter(self, filter_index):
        self.untoggle_all_diffs()
        self.filters.pop(filter_index)
        self.listWalker.pop(filter_index)
        self._emit("filter_update")

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
        self.diff_start = None
        self.diff_end = None
        self._emit("filter_update")

    def get_focused_filter_index(self):
        return self.listWalker.get_focus()[1]

    def untoggle_all_diffs(self):
        if self.diff_start is None:
            return

        for i in range(self.diff_start, self.diff_end + 1):
            self.listWalker[i].toggle_diff()

        self.diff_start = None
        self.diff_end = None
        self._emit("diff_update")

    def toggle_filter_diffs(self, filter_index):
        if self.diff_start is None:
            self.diff_start = filter_index
            self.diff_end = filter_index
            self.listWalker[filter_index].toggle_diff()

        elif self.diff_start == filter_index and self.diff_end == filter_index:
            self.diff_start = None
            self.diff_end = None
            self.listWalker[filter_index].toggle_diff()

        elif self.diff_start == filter_index:
            self.diff_start += 1
            self.listWalker[filter_index].toggle_diff()

        elif self.diff_end == filter_index:
            self.diff_end -= 1
            self.listWalker[filter_index].toggle_diff()

        elif filter_index == self.diff_start - 1:
            self.diff_start -= 1
            self.listWalker[filter_index].toggle_diff()

        elif filter_index == self.diff_end + 1:
            self.diff_end += 1
            self.listWalker[filter_index].toggle_diff()

        else:
            # turn everything between start and end off
            for i in range(self.diff_start, self.diff_end + 1):
                self.listWalker[i].toggle_diff()

            self.diff_start = filter_index
            self.diff_end = filter_index
            self.listWalker[filter_index].toggle_diff()

        self._emit("diff_update")


    def keypress(self, size, key):

        if key == "d":
            index = self.get_focused_filter_index()
            self.toggle_filter_diffs(index)

        if key == "r":
            self.untoggle_all_diffs()

        if key == "w":
            # move focused filter up
            index = self.get_focused_filter_index()
            if index > 0:
                self.listWalker[index], self.listWalker[index - 1] = \
                    self.listWalker[index - 1], self.listWalker[index]
                self.filters[index], self.filters[index - 1] = \
                    self.filters[index - 1], self.filters[index]
                # move focus up
                self.listWalker.set_focus(index - 1)
                self._emit("filter_update")

        if key == "s":
            # move focused filter down
            index = self.get_focused_filter_index()
            if index < len(self.listWalker) - 1:
                self.listWalker[index], self.listWalker[index + 1] = \
                    self.listWalker[index + 1], self.listWalker[index]
                self.filters[index], self.filters[index + 1] = \
                    self.filters[index + 1], self.filters[index]
                # move focus down
                self.listWalker.set_focus(index + 1)
                self._emit("filter_update")

        return super().keypress(size, key)
