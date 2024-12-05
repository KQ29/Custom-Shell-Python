# constants.py

import os

# ANSI color codes for colored output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

# Command options for autocompletion
command_options = {
    'ls': ['-l', '-a'],
    'rm': ['-r', '-f'],
    'help': [],
    'cd': [],
    'mkdir': [],
    'cp': [],
    'mv': [],
    'pwd': [],
    'exit': [],
    'alias': [],
    'unalias': [],
    'export': [],
    'echo': [],
    'jobs': [],
    'fg': [],
    'bg': [],
    'source': [],
}

# Aliases dictionary
aliases = {}

# Check OS type
IS_WINDOWS = os.name == 'nt'
IS_UNIX = os.name == 'posix'
