import gzip
import urwid

class DatasetView(urwid.WidgetWrap):

    def __init__(self, dataset):

        list_content = []
        for src, tgt in dataset:
            list_content.append(urwid.Columns([urwid.Text(src), urwid.Text(tgt)], dividechars=1))
            list_content.append(urwid.Divider("─"))  # this is the line character

        listbox = urwid.ListBox(list_content)
        linebox = urwid.LineBox(
            listbox, title=f"Dataset: {dataset.name}",
            title_align="left")

        #linebox.title_widget = urwid.AttrMap(linebox.title_widget,
        #                                     attr_map="heading", focus_map="focus heading")

        super().__init__(linebox)
