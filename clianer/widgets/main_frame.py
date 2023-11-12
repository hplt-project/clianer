import urwid

from clianer.widgets.dataset_view import DatasetView
from clianer.widgets.filter_list import FilterList


PALETTE = [(None,  'black', 'dark gray'),
           ('heading', 'white', 'dark gray'),
           ('line', 'black', 'light gray'),
           ('options', 'light cyan', 'black'),
           ('focus heading', 'white', 'dark red'),
           ('focus line', 'black', 'dark red'),
           ('focus options', 'black', 'light gray'),
           ('selected', 'white', 'dark blue')]

# FOCUS_MAP = {'heading': 'focus heading',
#              'options': 'focus options',
#              'line': 'focus line'}


class ClianerFrame(urwid.WidgetWrap):
    def __init__(self, f1, f2):

        self.filterList = FilterList()
        self.datasetView = DatasetView(f1, f2)

        self.body = urwid.Columns([(40, self.filterList), self.datasetView])
        self.header = urwid.Text('File')


        self.footer = urwid.Columns([
            urwid.AttrMap(urwid.Text('F3: Add Filter'), 'options'),
            urwid.AttrMap(urwid.Text('Q: Quit'), 'options')
        ])

        self.frame = urwid.Frame(
            self.body, header=self.header, footer=self.footer)

        super().__init__(self.frame)

    def keypress(self, size, key):
        if key == 'q' or key == 'Q':
            raise urwid.ExitMainLoop()
        return super().keypress(size, key)
