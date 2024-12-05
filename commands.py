# commands.py

import os
import stat
import time
import shutil
import glob
import subprocess
import logging
import shlex
from constants import RED, GREEN, YELLOW, BLUE, CYAN, RESET, aliases
from utils import confirm
from jobs import jobs_list, Job

def change_directory(path):
    """Change the current working directory."""
    path = os.path.expanduser(os.path.expandvars(path))
    try:
        os.chdir(path)
    except FileNotFoundError:
        print(f"{RED}cd: No such directory: {path}{RESET}")
    except NotADirectoryError:
        print(f"{RED}cd: Not a directory: {path}{RESET}")
    except Exception as e:
        logging.error(f"cd: Error: {e}", exc_info=True)
        print(f"{RED}cd: Error: {e}{RESET}")

def list_files(detailed=False, all_files=False):
    """List files in the current directory, with optional details and hidden files."""
    try:
        if all_files:
            items = os.listdir('.')
        else:
            items = [item for item in os.listdir('.') if not item.startswith('.')]
        for item in sorted(items):
            if detailed:
                stats = os.stat(item)
                permissions = stat.filemode(stats.st_mode)
                size = stats.st_size
                mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(stats.st_mtime))
                if os.path.isdir(item):
                    item_type = BLUE + item + RESET
                else:
                    item_type = item
                print(f"{permissions} {size:>8} {mtime} {item_type}")
            else:
                if os.path.isdir(item):
                    print(f"{BLUE}{item}{RESET}")
                else:
                    print(item)
    except Exception as e:
        logging.error(f"ls: Error: {e}", exc_info=True)
        print(f"{RED}ls: Error: {e}{RESET}")

def make_directory(directory_name):
    """Create a new directory."""
    directory_name = os.path.expanduser(os.path.expandvars(directory_name))
    try:
        os.makedirs(directory_name, exist_ok=False)
    except FileExistsError:
        print(f"{RED}mkdir: Directory '{directory_name}' already exists.{RESET}")
    except Exception as e:
        logging.error(f"mkdir: Error: {e}", exc_info=True)
        print(f"{RED}mkdir: Error: {e}{RESET}")

def remove_item(patterns, recursive=False, force=False):
    """Remove files or directories matching the given patterns."""
    for pattern in patterns:
        items = glob.glob(os.path.expanduser(os.path.expandvars(pattern)))
        if not items and not force:
            print(f"{RED}rm: No such file or directory: {pattern}{RESET}")
            continue
        for item_name in items:
            try:
                if os.path.isdir(item_name) and not os.path.islink(item_name):
                    if recursive:
                        if force or confirm(f"rm: remove directory '{item_name}' and its contents?"):
                            shutil.rmtree(item_name)
                    else:
                        print(f"{RED}rm: cannot remove '{item_name}': Is a directory{RESET}")
                else:
                    if force or confirm(f"rm: remove file '{item_name}'?"):
                        os.remove(item_name)
            except Exception as e:
                logging.error(f"rm: Error: {e}", exc_info=True)
                print(f"{RED}rm: Error: {e}{RESET}")

def copy_item(source, destination):
    """Copy a file or directory."""
    source = os.path.expanduser(os.path.expandvars(source))
    destination = os.path.expanduser(os.path.expandvars(destination))
    try:
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    except Exception as e:
        logging.error(f"cp: Error: {e}", exc_info=True)
        print(f"{RED}cp: Error: {e}{RESET}")

def move_item(source, destination):
    """Move or rename a file or directory."""
    source = os.path.expanduser(os.path.expandvars(source))
    destination = os.path.expanduser(os.path.expandvars(destination))
    try:
        shutil.move(source, destination)
    except Exception as e:
        logging.error(f"mv: Error: {e}", exc_info=True)
        print(f"{RED}mv: Error: {e}{RESET}")

def print_working_directory():
    """Print the current working directory."""
    print(os.getcwd())

def display_help():
    """Display help information."""
    help_text = f"""
{GREEN}Available commands:{RESET}
  {CYAN}cd [path]{RESET}        Change the current directory to 'path'.
  {CYAN}ls [-l] [-a]{RESET}     List files in the current directory. Use '-l' for detailed listing.
  {CYAN}mkdir [name]{RESET}     Create a new directory named 'name'.
  {CYAN}rm [options] [pattern]{RESET}
                   Remove files or directories matching 'pattern'.
                   Options:
                     -r    Recursively remove directories and their contents.
                     -f    Force removal without prompt.
  {CYAN}cp [source] [dest]{RESET} Copy file or directory from 'source' to 'dest'.
  {CYAN}mv [source] [dest]{RESET} Move or rename 'source' to 'dest'.
  {CYAN}pwd{RESET}              Display the current working directory.
  {CYAN}alias [name='command']{RESET}  Create an alias for a command.
  {CYAN}unalias [name]{RESET}    Remove an alias.
  {CYAN}export NAME=value{RESET} Set an environment variable.
  {CYAN}echo [args]{RESET}       Display a line of text.
  {CYAN}jobs{RESET}              List background jobs.
  {CYAN}fg [job_id]{RESET}       Bring a background job to the foreground.
  {CYAN}source [file]{RESET}     Execute commands from a file.
  {CYAN}help [command]{RESET}    Display help information.
  {CYAN}exit{RESET}              Exit the shell.

You can also execute system commands and use pipelines and redirection.
"""
    print(help_text)

# Help texts for individual commands
command_help = {
    'cd': 'Usage: cd [path]\nChange the current directory to [path].',
    'ls': 'Usage: ls [-l] [-a]\nList directory contents.',
    'mkdir': 'Usage: mkdir [directory]\nCreate a new directory.',
    'rm': 'Usage: rm [options] [pattern]\nRemove files or directories.\nOptions:\n  -r  Recursively remove directories.\n  -f  Force removal without prompt.',
    'cp': 'Usage: cp [source] [destination]\nCopy files or directories.',
    'mv': 'Usage: mv [source] [destination]\nMove or rename files or directories.',
    'pwd': 'Usage: pwd\nPrint the current working directory.',
    'alias': 'Usage: alias [name=\'command\']\nCreate an alias for a command.',
    'unalias': 'Usage: unalias [name]\nRemove an alias.',
    'export': 'Usage: export NAME=value\nSet an environment variable.',
    'echo': 'Usage: echo [arguments]\nDisplay a line of text.',
    'jobs': 'Usage: jobs\nList background jobs.',
    'fg': 'Usage: fg [job_id]\nBring a background job to the foreground.',
    'source': 'Usage: source [file]\nExecute commands from a file.',
    'help': 'Usage: help [command]\nDisplay help information.',
    'exit': 'Usage: exit\nExit the shell.',
}

def display_command_help(command_name):
    """Display help for a specific command."""
    help_text = command_help.get(command_name, f"No help available for '{command_name}'.")
    print(help_text)

def set_alias(name, command):
    """Set an alias for a command."""
    aliases[name] = command

def remove_alias(name):
    """Remove an alias."""
    aliases.pop(name, None)

def set_environment_variable(name, value):
    """Set an environment variable."""
    os.environ[name] = value

def get_environment_variable(name):
    """Get an environment variable."""
    return os.environ.get(name, '')

def execute_command(command_input):
    """Execute a system command, supporting pipelines and redirection."""
    try:
        # Parse the command for pipelines
        commands = [shlex.split(cmd) for cmd in command_input.split('|')]
        num_commands = len(commands)
        processes = []
        for i in range(num_commands):
            stdin = processes[i - 1].stdout if i > 0 else None
            stdout = subprocess.PIPE if i < num_commands - 1 else None
            proc = subprocess.Popen(
                commands[i],
                stdin=stdin,
                stdout=stdout or subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append(proc)
        # Wait for the last process to complete
        output, errors = processes[-1].communicate()
        if output:
            print(output.decode())
        if errors:
            print(errors.decode())
        return processes[-1].returncode
    except FileNotFoundError:
        command_name = commands[0][0] if commands and commands[0] else command_input
        logging.error(f"Command not found: {command_name}", exc_info=True)
        print(f"{RED}Command not found: {command_name}{RESET}")
        return 127
    except Exception as e:
        logging.error(f"Error executing command: {e}", exc_info=True)
        print(f"{RED}Error executing command: {e}{RESET}")
        return 1

def execute_script(file_path, process_command):
    """Execute commands from a script file."""
    try:
        with open(file_path, 'r') as script_file:
            for line in script_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    process_command(line)
    except Exception as e:
        logging.error(f"Error executing script: {e}", exc_info=True)
        print(f"{RED}Error executing script: {e}{RESET}")
