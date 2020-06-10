#!/usr/bin/env python
# 

import os
import re
import subprocess
import sys

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    HSplit,
    VerticalAlign,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit import ANSI
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import to_formatted_text, fragment_list_to_text
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.processors import Processor, Transformation
from prompt_toolkit.widgets import Frame


HISTORY_HEIGHT = 5 # Odds only


TITLE = HTML(
    """ <u>VSplit VerticalAlign</u> example.
 Press <b>'q'</b> to quit."""
)

FOOTER="""[j] [k]: Move        [enter]: Set to next command        [q]: quit"""


class HistoryLogContainer():
    def __init__(self):
        self.raw_logs = ''
        self.logs = []
        home_dir = os.environ.get('HOME')
        histfile = os.path.expanduser('{}/.zsh_history'.format(home_dir))

        with open(histfile, 'r', errors='replace') as f:
            parsed_lines = f.readlines()
            one_line = ''.join(parsed_lines)
            replaced_logs = one_line.replace('\\\n', '\\  ')
            replaced_logs = re.sub(': ([\d]+):([\d]+);', '', replaced_logs)

            self.logs = replaced_logs.split('\n')
            self.logs.pop()
        self.curr = len(self.logs) - 1

    def curr_up(self):
        if self.curr > 0:
            self.curr = self.curr - 1
    
    def curr_down(self):
        if self.curr < len(self.logs) - 1:
            self.curr = self.curr + 1

    def get_curr(self):
        return self.curr

    def get_logs(self):
        return self.logs
    
    def filter(self, word):
        filtered_logs = []
        for line in self.logs:
            if word in line:
                filtered_logs.append(line)
        self.logs = filtered_logs
        self.curr = len(self.logs) - 1


class FormatText(Processor):
    def apply_transformation(self, transformation_input):
        fragments = to_formatted_text(ANSI(fragment_list_to_text(transformation_input.fragments)))
        return Transformation(fragments)


def print_logs(logs, curr):
    printed_logs = list(logs)
    printed_logs[curr] = '\x1b[41;37m{}\x1b[0m'.format(printed_logs[curr])
    padding = int(HISTORY_HEIGHT / 2)

    log_length = len(printed_logs)
    for i in range(HISTORY_HEIGHT):
        printed_logs.append('')

    if curr < padding:
        pivot = padding
    else:
        pivot = curr

    result = ''
    for i in range(HISTORY_HEIGHT):
        log = printed_logs[pivot - (HISTORY_HEIGHT - 1 - i)]
        result = result + '{}\n'.format(log)
    result = result + '{}'.format(printed_logs[pivot+1])
    
    return result


# layout
log_container = HistoryLogContainer()

buff = Buffer()
contents = Window(
    BufferControl(
        buffer=buff,
        input_processors=[FormatText()],
        include_default_input_processors=True)
)
buff.text = print_logs(log_container.get_logs(), log_container.get_curr())

body = HSplit(
    [
        VSplit(
            [
                Window(
                    FormattedTextControl(HTML("Recall History")),
                    height=4,
                    ignore_content_width=True,
                    style="bg:#e4ec55 #000000 bold",
                    align=WindowAlign.CENTER,
                ),
            ],
            height=1,
            padding=1,
            padding_style="bg:#e4ec55",
        ),
        VSplit(
            [
                # Top alignment.
                HSplit(
                    [
                        contents
                    ],
                    padding=1,
                    height=HISTORY_HEIGHT + 1,
                    padding_style="bg:#fff #ffffff",
                    align=VerticalAlign.TOP,
                    padding_char="~",
                ),
                # Center alignment.
            ],
            padding=1,
            padding_style="bg:#fff #ffffff",
            padding_char="|",
        ),
        Frame(
            Window(FormattedTextControl(HTML(FOOTER)), height=1), style="bg:#9ac2f4 #000000"
        ),
    ]
)


# Key bindings
kb = KeyBindings()

@kb.add('j')
def _(event):
    log_container.curr_down()
    buff.text = print_logs(log_container.get_logs(), log_container.get_curr())


@kb.add('k')
def _(event):
    log_container.curr_up()
    buff.text = print_logs(log_container.get_logs(), log_container.get_curr())


@kb.add('c-m')
def _(event):
    ' Set next history '
    target_cmd = log_container.get_logs()[log_container.get_curr()] + '\n'
    home_dir = os.environ.get('HOME')
    with open('{}/.zsh_next_cmd'.format(home_dir), 'w') as f:
        f.write(target_cmd)
    event.app.exit()


@kb.add('c-c')
@kb.add('q')
def _(event):
    ' Quit application. '
    event.app.exit()


# Application
application = Application(
    layout=Layout(body),
    key_bindings=kb,
    full_screen=False)


def run():
    application.output.show_cursor = lambda:None # Hide cursor
    application.run()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = ' '.join(sys.argv[1:])
        log_container.filter(args)
        buff.text = print_logs(log_container.get_logs(), log_container.get_curr())
    run()
