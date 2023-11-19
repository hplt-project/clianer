import gzip
import urwid

class DatasetView(urwid.WidgetWrap):

    def __init__(self, dataset=None):
        if dataset is None:
            list_content = [urwid.Text("Press F2 to load a dataset.")]
        else:
            list_content = self._format_cols(dataset)
        self.datacols = urwid.ListBox(list_content)
        listbox = urwid.Padding(self.datacols, ("fixed left", 1), ("fixed right", 1))
        listbox = urwid.AttrMap(listbox, attr_map="data")

        name = dataset.name if dataset is not None else ""
        self.linebox = urwid.LineBox(
            listbox, title=f"Dataset: {name}",
            title_align="left", title_attr="heading")

        #self.linebox.title_widget = urwid.AttrMap(
        #    self.linebox.title_widget, attr_map="heading", focus_map="focus heading")

        super().__init__(self.linebox)

    def _format_cols(self, dataset):
        list_content = []
        for src, tgt in dataset:
            cols =  urwid.Columns([urwid.Text(src), urwid.Text(tgt)],
                                  dividechars=1)
            cols._selectable = True
            list_content.append(
                urwid.AttrMap(cols, attr_map="data", focus_map="focus data"))
            #list_content.append(urwid.Divider(" "))
            #list_content.append(urwid.Divider("─"))  # this is the line character

        return list_content

    def set_dataset(self, dataset):
        self.datacols.body.clear()
        self.datacols.body.extend(self._format_cols(dataset))
        self.linebox.set_title(f"Dataset: {dataset.name}")
