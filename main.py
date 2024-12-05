# main.py

import shlex
import threading
import re
import os
import logging
import subprocess

# Try importing readline for history navigation; use pyreadline on Windows
try:
    import readline
except ImportError:
    import pyreadline as readline

from constants import RED, GREEN, YELLOW, RESET, aliases
from utils import get_prompt, setup_autocomplete, load_configuration
from commands import (
    change_directory,
    list_files,
    make_directory,
    remove_item,
    copy_item,
    move_item,
    print_working_directory,
    display_help,
    display_command_help,
    set_alias,
    remove_alias,
    set_environment_variable,
    execute_command,
    execute_script,
)
from autocomplete import autocomplete_commands
from jobs import add_job, list_jobs, bring_job_to_foreground

# Configure logging
logging.basicConfig(filename='shell.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s: %(message)s')

def substitute_commands(command_input):
    """Substitute commands enclosed in backticks or $()."""
    pattern = r'`([^`]+)`|\$\(([^)]+)\)'
    while True:
        match = re.search(pattern, command_input)
        if not match:
            break
        cmd = match.group(1) or match.group(2)
        try:
            # Use shell=True to allow shell features in command substitution
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
            command_input = command_input[:match.start()] + output + command_input[match.end():]
        except subprocess.CalledProcessError as e:
            error_output = e.output.decode().strip() if e.output else str(e)
            logging.error(f"Error in command substitution: {error_output}", exc_info=True)
            print(f"{RED}Error in command substitution: {error_output}{RESET}")
            # Remove the failed substitution
            command_input = command_input[:match.start()] + command_input[match.end():]
        except Exception as e:
            logging.error(f"Error in command substitution: {e}", exc_info=True)
            print(f"{RED}Error in command substitution: {e}{RESET}")
            # Remove the failed substitution
            command_input = command_input[:match.start()] + command_input[match.end():]
    return command_input

def process_command(command_input):
    """Process a single command input."""
    # Handle command substitution
    command_input = substitute_commands(command_input)

    if not command_input:
        return

    # Command History
    readline.add_history(command_input)

    # Handle background execution
    background = False
    if command_input.endswith('&'):
        background = True
        command_input = command_input[:-1].strip()

    tokens = shlex.split(command_input)
    if not tokens:
        return
    command = tokens[0]
    args = tokens[1:]

    # Handle variable assignment
    if '=' in command and command[0] != '=':
        name, value = command_input.split('=', 1)
        set_environment_variable(name.strip(), value.strip())
        return

    # Check for aliases
    if command in aliases:
        aliased_command = aliases[command]
        command_input = aliased_command + ' ' + ' '.join(args)
        tokens = shlex.split(command_input)
        command = tokens[0]
        args = tokens[1:]

    # Handle built-in commands
    if command == 'exit':
        print(f"{GREEN}Exiting Custom Shell. Goodbye!{RESET}")
        exit(0)
    elif command == 'cd':
        path = args[0] if args else '~'
        change_directory(path)
    elif command == 'ls':
        detailed = False
        all_files = False
        for arg in args:
            if arg == '-l':
                detailed = True
            elif arg == '-a':
                all_files = True
        list_files(detailed, all_files)
    elif command == 'mkdir':
        if args:
            make_directory(args[0])
        else:
            print(f"{RED}mkdir: missing operand{RESET}")
    elif command == 'rm':
        recursive = False
        force = False
        patterns = []
        for arg in args:
            if arg == '-r':
                recursive = True
            elif arg == '-f':
                force = True
            else:
                patterns.append(arg)
        if patterns:
            remove_item(patterns, recursive=recursive, force=force)
        else:
            print(f"{RED}rm: missing operand{RESET}")
    elif command == 'cp':
        if len(args) >= 2:
            copy_item(args[0], args[1])
        else:
            print(f"{RED}cp: missing file operand{RESET}")
    elif command == 'mv':
        if len(args) >= 2:
            move_item(args[0], args[1])
        else:
            print(f"{RED}mv: missing file operand{RESET}")
    elif command == 'pwd':
        print_working_directory()
    elif command == 'alias':
        if args:
            for arg in args:
                if '=' in arg:
                    name, cmd = arg.split('=', 1)
                    set_alias(name, cmd)
                else:
                    print(f"{YELLOW}{arg}='{aliases.get(arg, '')}'{RESET}")
        else:
            for name, cmd in aliases.items():
                print(f"{YELLOW}{name}='{cmd}'{RESET}")
    elif command == 'unalias':
        if args:
            remove_alias(args[0])
        else:
            print(f"{RED}unalias: missing operand{RESET}")
    elif command == 'export':
        if args and '=' in args[0]:
            name, value = args[0].split('=', 1)
            set_environment_variable(name, value)
        else:
            print(f"{RED}export: invalid format. Use 'export NAME=value'{RESET}")
    elif command == 'echo':
        output = ' '.join(args)
        # Expand environment variables
        output = os.path.expandvars(output)
        print(output)
    elif command == 'jobs':
        list_jobs()
    elif command == 'fg':
        if args:
            try:
                job_id = int(args[0])
                bring_job_to_foreground(job_id)
            except ValueError:
                print(f"{RED}fg: argument must be a job ID{RESET}")
        else:
            print(f"{RED}fg: job ID missing{RESET}")
    elif command == 'help':
        if args:
            display_command_help(args[0])
        else:
            display_help()
    elif command == 'source':
        if args:
            execute_script(args[0], process_command)
        else:
            print(f"{RED}source: filename argument required{RESET}")
    else:
        # Execute external command
        if background:
            thread = threading.Thread(target=execute_command, args=(command_input,))
            thread.start()
            add_job(thread, command_input)
        else:
            execute_command(command_input)

def main():
    print(f"{GREEN}Welcome to Enhanced Custom Shell! Type 'help' to see available commands. Type 'exit' to quit.{RESET}")
    setup_autocomplete(autocomplete_commands)
    load_configuration(process_command)

    while True:
        try:
            prompt = get_prompt()
            command_input = input(prompt).strip()
            if command_input:
                process_command(command_input)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Interrupted. Type 'exit' to quit.{RESET}")
        except EOFError:
            print(f"\n{GREEN}Exiting Custom Shell. Goodbye!{RESET}")
            break
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)
            print(f"{RED}An error occurred: {e}{RESET}")

if __name__ == "__main__":
    main()
