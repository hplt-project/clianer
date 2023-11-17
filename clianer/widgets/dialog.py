import urwid


class Dialog(urwid.WidgetWrap):
    """A base class for dialogs providing a unified look and feel."""

    def __init__(self, body, header, width=None, height=None):
        # inspired by urwid's dialog.py

        # TODO the widht and height attributes do not work as expected
        self.width = width
        if self.width is None:
            self.width = ("relative", 80)

        self.height = height
        if self.height is None:
            self.height = ("relative", 80)

        self.body = body

        # pad area inside linebox
        w = urwid.Padding(body, ("fixed left", 1), ("fixed right", 1))

        # linebox around body
        w = urwid.LineBox(w, title=header, title_align="center",
                          title_attr="dialog heading")

        # pad area around linebox
        w = urwid.Padding(w, ("fixed left", 2), ("fixed right", 2))
        w = urwid.Filler(w, ("fixed top", 1), ("fixed bottom", 1))
        w = urwid.AttrMap(w, "dialog body")

        # "shadow" effect
        w = urwid.Columns([w, ("fixed", 2, urwid.AttrMap(urwid.Filler(
            urwid.Text(("dialog shadow corner", "  ")), "top"), "shadow"))])
        w = urwid.Frame(w, footer=urwid.AttrMap(
            urwid.Text(("dialog shadow corner", "  ")), "shadow"))

        # outermost border area
        w = urwid.Padding(w, "center", self.width)
        w = urwid.Filler(w, "middle", self.height)
        w = urwid.AttrMap(w, "border")

        self.dialog_top = w

        super().__init__(self.dialog_top)

    def overlay(self, bottom_w):
        return urwid.Overlay(
            self, bottom_w, "center", self.width, "middle", self.height)
