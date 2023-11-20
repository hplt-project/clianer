import urwid

from clianer.util.diff import diff_bitexts


class DatasetView(urwid.WidgetWrap):

    def __init__(self, draw_lines=False):
        self.datacols = urwid.ListBox(urwid.SimpleFocusListWalker([
                urwid.Text("Press F2 to load a dataset.")]))
        self.draw_lines = draw_lines

        listbox = urwid.Padding(
            self.datacols, ("fixed left", 1), ("fixed right", 1))
        listbox = urwid.AttrMap(listbox, attr_map="data")

        self.linebox = urwid.LineBox(
            listbox, title=f"No dataset loaded",
            title_align="left", title_attr="heading")

        super().__init__(self.linebox)

    def show(self, data, title=None):
        self.datacols.body.clear()

        langs = data[0].keys()
        assert len(langs) == 2
        src, tgt = langs

        for entry in data:
            assert src in entry.keys() and tgt in entry.keys()
            cols = urwid.Columns(
                [urwid.Text(entry[src]), urwid.Text(entry[tgt])],
                dividechars=1)
            cols._selectable = True
            self.datacols.body.append(
                urwid.AttrMap(cols, attr_map="data", focus_map="focus data"))
            if self.draw_lines:
                self.datacols.body.append(urwid.Divider("─"))

        if title is not None:
            self.linebox.set_title(f"Dataset: {title}")


    def show_diff(self, rev1_src, rev1_tgt, rev2_src, rev2_tgt, title=None):

        bitext_diff = diff_bitexts(rev1_src, rev1_tgt, rev2_src, rev2_tgt)

        # note that left and right are already urwid texts.
        self.datacols.body.clear()
        for (left, right) in bitext_diff:
            cols = urwid.Columns(
                [urwid.Text(left), urwid.Text(right)], dividechars=1)
            cols._selectable = True
            self.datacols.body.append(
                urwid.AttrMap(cols, attr_map="data", focus_map="focus data"))
            if self.draw_lines:
                self.datacols.body.append(urwid.Divider("─"))
