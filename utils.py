# utils.py

import os
import getpass
import socket
import readline
import shlex
import glob
from constants import GREEN, BLUE, RESET, YELLOW, command_options

def confirm(prompt):
    """Prompt the user for confirmation."""
    answer = input(f"{YELLOW}{prompt} [y/N]: {RESET}")
    return answer.lower() == 'y'

def get_prompt():
    """Generate the command prompt."""
    username = getpass.getuser()
    hostname = socket.gethostname()
    current_dir = os.getcwd()
    return f"{GREEN}{username}@{hostname}{RESET}:{BLUE}{current_dir}{RESET}$ "

def setup_autocomplete(autocomplete_function):
    """Set up autocompletion using the readline module."""
    readline.parse_and_bind("tab: complete")
    readline.set_completer(autocomplete_function)

def load_configuration(process_command):
    """Load shell configuration from ~/.custom_shellrc."""
    config_file = os.path.expanduser('~/.custom_shellrc')
    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    process_command(line)
