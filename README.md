# CLI-a-ner
Your command-line buddy for data cleaning.


## Installation
First, have the [OpusCleaner](https://github.com/hplt-project/OpusCleaner)
installed on your system.

Then, clone this repository and install the additional requirements (at this
point it's only `urwid` beyond what you already need to install to get a
working install of OpusCleaner)

## Usage

Set up the `DATA_PATH` (and perhaps the `SAMPLE_SIZE`) environment variables
(these are used by OpusCleaner as usual). Then, run the app with `./main.py`.

For example:

```bash
export DATA_PATH='/home/helcl/hplt/translation-models/en-cs/*.*.gz'
export SAMPLE_SIZE=100
cd path/to/clianer/
./main.py
```


## Controls

Most of the controls are listed in the bottom bar of the app frame. However,
there are some other controls depending the current application focus.
Move focus between filter view and dataset view using left and right arrow.

### Common controls

These work independently or whether focus is in the filter view or in the
dataset view.

- <kbd>F2</kbd> opens up a new dataset
- <kbd>F3</kbd> adds a new filter
- <kbd>F6</kbd> show clean version of the data in the dataset view
- <kbd>F7</kbd> assign categories to current dataset
- <kbd>F10</kbd>, <kbd>q</kbd> exit the application
- <kbd>Down</kbd>, <kbd>Up</kbd> move within the focused window
  (<kbd>PgUp</kbd> and <kbd>PgDn</kbd> also work)

### Filter view controls

- <kbd>F4</kbd> edit filter
- <kbd>F5</kbd> import filter pipeline from a different dataset (careful, this
  overwrites whatever is the current pipeline)
- <kbd>F8</kbd> remove filter
- <kbd>w</kbd>, <kbd>s</kbd> move selected filter up or down
- <kbd>d</kbd> mark filter for diffing
- <kbd>r</kbd> reset diffing

### Dataset view controls

- <kbd>F4</kbd> show diff (select which filter steps to diff in the filter
  view)
- <kbd>F5</kbd> show clean version of the data
