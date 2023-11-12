import gzip
import urwid

class DatasetView(urwid.WidgetWrap):

    def __init__(self, file1, file2):
        a = []
        b = []

        with gzip.open(file1, "rt") as f_src, gzip.open(file2, "rt") as f_tgt:
            for i, (src, tgt) in enumerate(zip(f_src, f_tgt)):
                a.append(src.rstrip("\r\n"))
                b.append(tgt.rstrip("\r\n"))

                if i == 50:
                    break


        list_content = []

        for src, tgt in zip(a, b):
            list_content.append(urwid.Columns([urwid.Text(src), urwid.Text(tgt)], dividechars=1))
            list_content.append(urwid.Divider("─"))  # this is the line character

        listbox = urwid.ListBox(list_content)
        linebox = urwid.LineBox(listbox, title="/placeholder/path.en-ga.gz", title_attr="heading")

        super().__init__(linebox)
