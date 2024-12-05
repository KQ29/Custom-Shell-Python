# autocomplete.py

import os
import shlex
import glob
import readline
from constants import command_options, aliases

def autocomplete_commands(text, state):
    """Provide autocompletion for commands and files."""
    buffer = readline.get_line_buffer()
    tokens = shlex.split(buffer)
    # Determine the context
    if not tokens or buffer.endswith(' '):
        # Suggest command names, aliases, or file names
        options = list(command_options.keys()) + list(aliases.keys()) + os.listdir()
    elif len(tokens) == 1:
        options = [cmd for cmd in command_options if cmd.startswith(text)] + \
                  [alias for alias in aliases if alias.startswith(text)] + \
                  [f for f in os.listdir() if f.startswith(text)]
    else:
        # Suggest command options or file names
        cmd = tokens[0]
        if cmd in command_options:
            opts = command_options[cmd]
            options = [opt for opt in opts if opt.startswith(text)] + glob.glob(text + '*')
        else:
            options = glob.glob(text + '*')
    try:
        return options[state]
    except IndexError:
        return None
