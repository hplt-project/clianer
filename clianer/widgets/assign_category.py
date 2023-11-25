import urwid

from clianer.widgets.dialog import Dialog
from clianer.widgets.button import CustomButton

from opuscleaner.categories import get_mapping, update_categories, Category

class AssignCategoriesDialog(Dialog):

    def __init__(self, dataset):

        self.dataset = dataset

        self.cat_mapping = get_mapping()
        # mapping: categories(list of category objects with name)
        #          mapping(dict of category -> list of datasets)

        # create set of checkboxes for each category
        self.checkboxes = []
        for cat in self.cat_mapping.categories:
            state = (cat.name in self.cat_mapping.mapping
                     and self.dataset in self.cat_mapping.mapping[cat.name])
            self.checkboxes.append(urwid.CheckBox(cat.name, state=state))
        checkboxes_widget = urwid.Pile(self.checkboxes + [urwid.Divider()])

        # create Save and Cancel buttons
        self.save_button = CustomButton("Save", self.save)
        self.cancel_button = CustomButton("Cancel", self.close)
        self.buttons = urwid.Padding(
            urwid.Columns([self.save_button, self.cancel_button], 4), "center")

        self.listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker([checkboxes_widget, self.buttons]))

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(
            self.listbox, f"Assign categories: {dataset}", width=50, height=10)

    def save(self, button):
        # update categories
        cats = []
        for checkbox in self.checkboxes:
            if checkbox.state:
                cats.append(checkbox.label)

        for cat in self.cat_mapping.categories:
            after = cat.name in cats
            before = (cat.name in self.cat_mapping.mapping
                      and self.dataset in self.cat_mapping.mapping[cat.name])

            if before and not after:
                # remove
                self.cat_mapping.mapping[cat.name].remove(self.dataset)

                # if that was the last dataset
                if not self.cat_mapping.mapping[cat.name]:
                    del self.cat_mapping.mapping[cat.name]

            elif not before and after:
                # add category array if not there
                if cat.name not in self.cat_mapping.mapping:
                    self.cat_mapping.mapping[cat.name] = []

                # add dataset
                self.cat_mapping.mapping[cat.name].append(self.dataset)

        update_categories(self.cat_mapping)
        self._emit("close", None)

    def close(self, button):
        self._emit("close", None)
