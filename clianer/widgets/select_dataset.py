import urwid

from clianer.widgets.dialog import Dialog
from clianer.widgets.button import CustomButton

from opuscleaner.config import DATA_PATH
from opuscleaner.datasets import list_datasets


class SelectDatasetDialog(Dialog):

    def __init__(self):
        # datasets: Dict[str, List[Tuple[str, Path]]]
        self.datasets = list_datasets(DATA_PATH)

        self.dataset_widgets = []
        for dataset_name in self.datasets:
            langs = ", ".join(
                sorted(lang for lang, _ in self.datasets[dataset_name]))

            button = CustomButton(
                f"{dataset_name} ({langs})",
                on_press=self.select_dataset,
                user_data=dataset_name)
            self.dataset_widgets.append(button)

        self.listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(self.dataset_widgets))

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(self.listbox, "Select dataset", width=60, height=30)

    def select_dataset(self, button, dataset):
        self._emit("close", dataset)
