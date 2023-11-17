import gzip
import urwid

class DatasetView(urwid.WidgetWrap):

    def __init__(self, dataset):

        list_content = []
        for src, tgt in dataset:
            cols =  urwid.Columns([urwid.Text(src), urwid.Text(tgt)],
                                  dividechars=1)
            cols._selectable = True
            list_content.append(
                urwid.AttrMap(cols, attr_map="data", focus_map="focus data"))
            #list_content.append(urwid.Divider(" "))
            #list_content.append(urwid.Divider("─"))  # this is the line character

        listbox = urwid.ListBox(list_content)
        listbox = urwid.Padding(listbox, ("fixed left", 1), ("fixed right", 1))
        listbox = urwid.AttrMap(listbox, attr_map="data")
        linebox = urwid.LineBox(
            listbox, title=f"Dataset: {dataset.name}",
            title_align="left", title_attr="heading")

        #linebox.title_widget = urwid.AttrMap(linebox.title_widget,
        #                                     attr_map="heading", focus_map="focus heading")

        super().__init__(linebox)
