import urwid


class CustomButton(urwid.Button):
    """ Same as urwid button but looks like a Midnight Commander button """

    def __init__(self, label, on_press=None, user_data=None, **kwargs):
        self.button_left = urwid.Text('[')
        self.button_right = urwid.Text(']')

        super().__init__(label, on_press, user_data, **kwargs)
        #import pudb;pu.db
        self._w = urwid.Columns([
            ('fixed', 1, self.button_left),
            self._label,
            ('fixed', 1, self.button_right)])

        self._w = urwid.AttrMap(self._w, 'button normal', 'button select')
