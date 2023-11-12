import os
import json
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


class FilterItem(urwid.WidgetWrap):
    def __init__(self, caption):
        self.caption = caption
        self.header = FilterItemHeader(caption, self.toggle_body)
        self.body = FilterItemBody({"option": "value", "option2": "32"})

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
        self.icon.set_text("aaa")
        if self.callback:
            self.callback()

    def set_expanded(self, expanded):
        if expanded:
            self.icon.set_text("[-] " + self.caption)
        else:
            self.icon.set_text("[+] " + self.caption)


class FilterItemBody(urwid.WidgetWrap):
    def __init__(self, filterOptions):

        cols = []
        for opt, val in filterOptions.items():
            cols.append(urwid.Columns([urwid.Text(opt), urwid.Text(val)]))

        self.top = urwid.Pile(cols)
        super().__init__(self.top)


class FilterList(urwid.WidgetWrap):
    def __init__(self):

        filter_names = list(get_filters().keys())
        filters_content = []
        for filter_name in filter_names:
            filters_content.append(FilterItem(filter_name))

        top = urwid.ListBox(filters_content)
        super().__init__(top)
