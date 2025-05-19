import os
import subprocess
import readline
import shlex
import sys
import signal
import threading
import time
import json
import yaml
import hashlib
import shutil
import glob
from datetime import datetime

class MyShell:
    def __init__(self):
        self.history_file = os.path.expanduser("~/.myshell_history")
        self.load_history()
        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")
        self.aliases = {}
        self.jobs = {}
        self.next_job_id = 1
        self.load_aliases()
        self.shell_vars = {}
        self.config = self.load_config()

    def load_config(self):
        config_file = os.path.expanduser("~/.myshellrc")
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_config(self):
        config_file = os.path.expanduser("~/.myshellrc")
        with open(config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def load_history(self):
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass

    def save_history(self):
        readline.write_history_file(self.history_file)

    def load_aliases(self):
        alias_file = os.path.expanduser("~/.myshell_aliases")
        try:
            with open(alias_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            self.aliases[parts[0].strip()] = parts[1].strip()
        except FileNotFoundError:
            pass

    def save_aliases(self):
        alias_file = os.path.expanduser("~/.myshell_aliases")
        with open(alias_file, "w") as f:
            for alias, command in self.aliases.items():
                f.write(f"{alias}={command}\n")

    def completer(self, text, state):
        options = sorted(os.listdir('.') + list(self.aliases.keys()))
        matches = [x for x in options if x.startswith(text)]
        if state < len(matches):
            return matches[state]
        else:
            return None

    def print_help(self):
        print("""
MyShell Help:

  Built-in commands:
    cd [dir]                Change directory
    exit                    Exit the shell
    help                    Show this help message
    alias [name='command']  Define or show command aliases
    unalias [name]          Remove an alias
    history [-c]            Show or clear command history
    jobs                    List active jobs
    fg [job_id]             Bring a background job to the foreground
    bg [job_id]             Resume a suspended background job
    setenv [variable=value] Set an environment variable
    getenv [variable]       Get the value of an environment variable
    setvar [variable=value] Set a shell variable
    getvar [variable]       Get the value of a shell variable
    echo [args]             Display a line of text
    pwd                     Print the current working directory
    ls [-l -a ...] [path]   List directory contents (basic)
    mkdir [-p] <dir>        Create directories (basic)
    rm [-rf] <file/dir>     Remove files or directories (basic)
    cp [-r] <src> <dest>    Copy files or directories (basic)
    mv <src> <dest>        Move or rename files or directories (basic)
    cat <file>              Concatenate and display files
    head [-n <num>] <file>  Display the beginning of a file
    tail [-n <num>] <file>  Display the end of a file
    grep <pattern> <file>   Search for a pattern in a file (basic)
    find <path> -name <pattern> Find files (very basic)
    du [-h] [path]          Disk usage (very basic)
    df [-h]                 Disk free (very basic)
    sleep <seconds>         Delay for a specified time
    date                    Display the current date and time
    calc <expression>       Evaluate a simple math expression
    checksum <file> [md5|sha256] Calculate file checksum
    type <command>          Display information about a command
    watch [-n <sec>] <cmd>  Execute a command periodically (basic)
    man <command>           Display a manual page (placeholder)
    edit <file>             Open a file in a text editor (placeholder)
    tree [path]             Display directory tree (placeholder)
    sort <file>             Sort lines of a text file (placeholder)
    wc [-lwc] <file>        Word, line, character count (placeholder)
    patch <orig> <patch>    Apply a patch file (placeholder)
    tar -cvf <arch.tar> ... Archive files (placeholder)
    gzip <file>             Compress a file (placeholder)
    gunzip <file.gz>        Decompress a file (placeholder)
    mount <device> <dir>    Mount a filesystem (placeholder)
    umount <dir>            Unmount a filesystem (placeholder)
    top                     Display system processes (placeholder)
    kill <pid>              Terminate a process (placeholder)
    login <user>            Login as another user (placeholder)
    logout                  Logout (placeholder)
    whoami                  Print the current user ID (placeholder)
    historysearch <term>    Search history (placeholder)
    repeat <n> <command>    Repeat a command n times (placeholder)
    geturl <url> <file>     Download a file from a URL (placeholder)
    config get <key>        Get a shell configuration value (placeholder)
    config set <key> <value> Set a shell configuration value (placeholder)
    theme set <theme>       Set the shell theme (placeholder)
    keybind <key> <action>  Define a key binding (placeholder)
    notify <message>        Display a desktop notification (placeholder)
    progress <max>          Display a progress bar (placeholder)
    script <file>           Execute a shell script (placeholder)
    debug <command>         Run a command in debug mode (placeholder)
    timeit <command>        Measure the execution time of a command (placeholder)
    network info            Display basic network info (placeholder)
    ping <host>             Send ICMP echo requests (placeholder)
    dnslookup <host>        Perform DNS lookup (placeholder)
    portscan <host>         Scan ports on a host (placeholder)
    ssh <user>@<host>       Connect to a remote host (placeholder)
    ftp <host>              Connect to an FTP server (placeholder)
    mail [-s <subj>] <to>    Send an email (placeholder)
    weather <location>      Get weather information (placeholder)
    translate <text> <lang> Translate text (placeholder)
    news <topic>            Get news headlines (placeholder)
    stocks <symbol>         Get stock quotes (placeholder)
    currency <from> <to> <amt> Convert currencies (placeholder)
    reminder <time> <msg>   Set a reminder (placeholder)
    todo add <task>         Add a to-do item (placeholder)
    todo list               List to-do items (placeholder)
    calculator              Interactive calculator (placeholder)
    unitconv <val> <from> <to> Unit conversion (placeholder)
    colortest               Display terminal colors (placeholder)
    asciiart <text>         Generate ASCII art (placeholder)
    qrgen <text>            Generate a QR code (placeholder)
    barcode <data>          Generate a barcode (placeholder)
    encrypt <file>          Encrypt a file (placeholder)
    decrypt <file>          Decrypt a file (placeholder)
    audioplay <file>        Play an audio file (placeholder)
    videoplay <file>        Play a video file (placeholder)
    imageview <file>        View an image file (placeholder)
    pdfview <file>          View a PDF file (placeholder)
    systeminfo              Display detailed system information (placeholder)
    processmonitor          Interactive process monitor (placeholder)
    diskmanager             Disk partition management (placeholder)
    usermanager             User and group management (placeholder)
    servicemanager          Manage system services (placeholder)
    packagemanager <cmd>    Basic package management (placeholder)
    virtualenv <cmd>        Virtual environment management (placeholder)
    docker <cmd>            Basic Docker interaction (placeholder)
    git <cmd>               Basic Git interaction (placeholder)
    sqlite <db> <query>     Run SQLite query (placeholder)
    blockchain <cmd>        Basic blockchain interaction (placeholder)
    cloud <cmd>             Basic cloud service interaction (placeholder)

  Piping and Redirection:
    Use '|' to pipe the output of one command to another.
    Use '>' to redirect output to a file (overwrite).
    Use '>>' to append output to a file.
    Use '<' to redirect input from a file (not yet fully implemented).
    Use '2>' to redirect standard error.
    Use '&>' to redirect both standard output and error.

  Background Jobs:
    Append '&' to a command to run it in the background.
    Use 'Ctrl+Z' to suspend the current foreground job.
""")

    def execute_command(self, command):
        if not command:
            return

        parts = shlex.split(command)
        command_name = parts[0]
        args = parts[1:]

        if command_name in self.aliases:
            command = self.aliases[command_name] + " " + " ".join(args)
            parts = shlex.split(command)
            command_name = parts[0]
            args = parts[1:]

        # --- Built-in Commands ---
        if command_name == "cd":
            if not args:
                os.chdir(os.path.expanduser("~"))
            else:
                try:
                    os.chdir(args[0])
                except FileNotFoundError:
                    print(f"cd: no such file or directory: {args[0]}")
                except NotADirectoryError:
                    print(f"cd: not a directory: {args[0]}")
                except OSError as e:
                    print(f"cd error: {e}")
            return
        elif command_name == "exit":
            self.save_history()
            self.save_aliases()
            self.save_config()
            sys.exit(0)
        elif command_name == "help":
            self.print_help()
            return
        elif command_name == "alias":
            if not args:
                for alias, cmd in self.aliases.items():
                    print(f"{alias}='{cmd}'")
            elif "=" in args[0]:
                name, value = args[0].split("=", 1)
                self.aliases[name] = value
                self.save_aliases()
            else:
                print("Usage: alias [name='command'] or alias")
            return
        elif command_name == "unalias":
            if args and args[0] in self.aliases:
                del self.aliases[args[0]]
                self.save_aliases()
            else:
                print("Usage: unalias [name]")
            return
        elif command_name == "history":
            if args and args[0] == "-c":
                readline.clear_history()
                if os.path.exists(self.history_file):
                    os.remove(self.history_file)
                print("History cleared.")
            else:
                for i, cmd in enumerate(readline.get_history_list()):
                    print(f" {i+1}  {cmd}")
            return
        elif command_name == "jobs":
            for job_id, job_info in list(self.jobs.items()):
                status = "Running" if job_info["process"].poll() is None else "Done"
                print(f"[{job_id}] {status} {job_info['command']}")
                if status == "Done":
                    del self.jobs[job_id]
            return
        elif command_name == "fg":
            if args and args[0].isdigit():
                job_id = int(args[0])
                if job_id in self.jobs:
                    job_info = self.jobs.pop(job_id)
                    print(job_info["command"])
                    try:
                        job_info["process"].wait()
                    except KeyboardInterrupt:
                        print("^C")
                    return
                else:
                    print(f"fg: job not found: {job_id}")
                    return
            else:
                print("Usage: fg [job_id]")
                return
        elif command_name == "bg":
            if args and args[0].isdigit():
                job_id = int(args[0])
                if job_id in self.jobs and job_info["process"].poll() is not None and job_info["status"] == "suspended":
                    print(f"[{job_id}] {job_info['command']} &")
                    job_info["process"].send_signal(signal.SIGCONT)
                    job_info["status"] = "running"
                    return
                elif job_id in self.jobs:
                    print(f"bg: job {job_id} is already running or not suspended")
                    return
                else:
                    print(f"bg: job not found: {job_id}")
                    return
            else:
                print("Usage: bg [job_id]")
                return
        elif command_name == "setenv":
            if args and "=" in args[0]:
                name, value = args[0].split("=", 1)
                os.environ[name] = value
            else:
                print("Usage: setenv [VARIABLE=VALUE]")
            return
        elif command_name == "getenv":
            if args and args[0] in os.environ:
                print(os.environ[args[0]])
            elif args:
                print(f"{args[0]} not found in environment")
            else:
                print("Usage: getenv [VARIABLE]")
            return
        elif command_name == "setvar":
            if args and "=" in args[0]:
                name, value = args[0].split("=", 1)
                self.shell_vars[name] = value
            else:
                print("Usage: setvar [VARIABLE=VALUE]")
            return
        elif command_name == "getvar":
            if args and args[0] in self.shell_vars:
                print(self.shell_vars[args[0]])
            elif args:
                print(f"{args[0]} not found in shell variables")
            else:
                print("Usage: getvar [VARIABLE]")
            return
        elif command_name == "echo":
            print(" ".join(args))
            return
        elif command_name == "pwd":
            print(os.getcwd())
            return
        elif command_name == "ls":
            list_long = "-l" in args
            list_all = "-a" in args
            paths = [arg for arg in args if not arg.startswith("-")] or ["."]
            for path in paths:
                try:
                    items = os.listdir(path)
                    if not list_all:
                        items = [item for item in items if not item.startswith(".")]
                    for item in items:
                        if list_long:
                            stat_info = os.stat(os.path.join(path, item))
                            mode = self.format_permissions(stat_info.st_mode)
                            nlink = stat_info.st_nlink
                            owner = self.get_user_name(stat_info.st_uid)
                            group = self.get_group_name(stat_info.st_gid)
                            size = stat_info.st_size
                            mtime = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            print(f"{mode} {nlink:>3} {owner:<8} {group:<8} {size:>8} {mtime} {item}")
                        else:
                            print(item, end="  ")
                    print()
                except FileNotFoundError:
                    print(f"ls: cannot access '{path}': No such file or directory")
                except NotADirectoryError:
                    print(f"ls: cannot access '{path}': Not a directory")
            return
        elif command_name == "mkdir":
            parents = "-p" in args
            dirs_to_create = [arg for arg in args if not arg == "-p"]
            for dir_path in dirs_to_create:
                try:
                    os.makedirs(dir_path, exist_ok=True) if parents else os.mkdir(dir_path)
                except FileExistsError:
                    print(f"mkdir: cannot create directory '{dir_path}': File exists")
                except OSError as e:
                    print(f"mkdir: error creating directory '{dir_path}': {e}")
            return
        elif command_name == "rm":
            recursive = "-r" in args or "-rf" in args
            force = "-f" in args or "-rf" in args
            items_to_remove = [arg for arg in args if not arg.startswith("-")]
            for item_path in items_to_remove:
                try:
                    if os.path.isfile(item_path) or (not os.path.isdir(item_path) and not recursive):
                        os.remove(item_path)
                    elif os.path.isdir(item_path) and recursive:
                        shutil.rmtree(item_path, ignore_errors=force)
                    elif os.path.isdir(item_path) and not recursive:
                        print(f"rm: cannot remove '{item_path}': Is a directory")
                    elif not os.path.exists(item_path) and not force:
                        print(f"rm: cannot remove '{item_path}': No such file or directory")
                except OSError as e:
                    print(f"rm: error removing '{item_path}': {e}")
            return
        elif command_name == "cp":
            recursive = "-r" in args
            sources = [arg for arg in args if not arg.startswith("-")][:-1]
            destination = [arg for arg in args if not arg.startswith("-")][-1]
            if not sources:
                print("Usage: cp [-r] <source> ... <destination>")
                return
            for src in sources:
                try:
                    if os.path.isfile(src):
                        shutil.copy2(src, destination)
                    elif os.path.isdir(src) and recursive:
                        dest_path = os.path.join(destination, os.path.basename(src))
                        shutil.copytree(src, dest_path)
                    elif os.path.isdir(src) and not recursive:
                        print(f"cp: omitting directory '{src}'")
                    else:
                        print(f"cp: cannot stat '{src}': No such file or directory")
                except OSError as e:
                    print(f"cp: error copying '{src}' to '{destination}': {e}")
            return
        elif command_name == "mv":
            if len(args) < 2:
                print("Usage: mv <source> <destination>")
                return
            source = args[0]
            destination = args[1]
            try:
                shutil.move(source, destination)
            except FileNotFoundError:
                print(f"mv: cannot stat '{source}': No such file or directory")
            except OSError as e:
                print(f"mv: error moving '{source}' to '{destination}': {e}")
            return
        elif command_name == "cat":
            if not args:
                print("Usage: cat <file> [...]")
                return
            for file_path in args:
                try:
                    with open(file_path, "r") as f:
                        print(f.read(), end="")
                except FileNotFoundError:
                    print(f"cat: {file_path}: No such file or directory")
                except OSError as e:
                    print(f"cat: error reading '{file_path}': {e}")
            return
        elif command_name == "head":
            num_lines = 10
            file_paths = args
            if args and args[0].startswith("-n"):
                try:
                    num_lines = int(args[0][2:])
                    file_paths = args[1:]
                except ValueError:
                    print("head: invalid number of lines")
                    return
            if not file_paths:
                print("Usage: head [-n <num>] <file> [...]")
                return
            for file_path in file_paths:
                try:
                    with open(file_path, "r") as f:
                        for _ in range(num_lines):
                            line = f.readline()
                            if not line:
                                break
                            print(line, end="")
                except FileNotFoundError:
                    print(f"head: cannot open '{file_path}' for reading: No such file or directory")
                except OSError as e:
                    print(f"head: error reading '{file_path}': {e}")
            return
        elif command_name == "tail":
            num_lines = 10
            file_paths = args
            if args and args[0].startswith("-n"):
                try:
                    num_lines = int(args[0][2:])
                    file_paths = args[1:]
                except ValueError:
                    print("tail: invalid number of lines")
                    return
            if not file_paths:
                print("Usage: tail [-n <num>] <file> [...]")
                return
            for file_path in file_paths:
                try:
                    with open(file_path, "r") as f:
                        lines = f.readlines()
                        for line in lines[-num_lines:]:
                            print(line, end="")
                except FileNotFoundError:
                    print(f"tail: cannot open '{file_path}' for reading: No such file or directory")
                except OSError as e:
                    print(f"tail: error reading '{file_path}': {e}")
            return
        elif command_name == "grep":
            if len(args) < 2:
                print("Usage: grep <pattern> <file> [...]")
                return
            pattern = args[0]
            file_paths = args[1:]
            for file_path in file_paths:
                try:
                    with open(file_path, "r") as f:
                        for line in f:
                            if pattern in line:
                                print(f"{file_path}:{line}", end="")
                except FileNotFoundError:
                    print(f"grep: {file_path}: No such file or directory")
                except OSError as e:
                    print(f"grep: error reading '{file_path}': {e}")
            return
        elif command_name == "find":
            if len(args) < 3 or args[1] != "-name":
                print("Usage: find <path> -name <pattern>")
                return
            search_path = args[0]
            pattern = args[2]
            for root, _, files in os.walk(search_path):
                for name in files:
                    if glob.fnmatch.fnmatch(name, pattern):
                        print(os.path.join(root, name))
            return
        elif command_name == "du":
            human_readable = "-h" in args
            paths = [arg for arg in args if not arg == "-h"] or ["."]
            for path in paths:
                total_size = 0
                try:
                    if os.path.isfile(path):
                        total_size = os.path.getsize(path)
                    elif os.path.isdir(path):
                        for dirpath, _, filenames in os.walk(path):
                            for f in filenames:
                                fp = os.path.join(dirpath, f)
                                try:
                                    total_size += os.path.getsize(fp)
                                except OSError:
                                    pass
                    if human_readable:
                        print(f"{self.format_size(total_size)}\t{path}")
                    else:
                        print(f"{total_size}\t{path}")
                except FileNotFoundError:
                    print(f"du: cannot access '{path}': No such file or directory")
                except OSError as e:
                    print(f"du: error accessing '{path}': {e}")
            return
        elif command_name == "df":
            human_readable = "-h" in args
            try:
                output = subprocess.check_output(["df"], universal_newlines=True)
                lines = output.strip().split('\n')
                header = lines[0]
                print(header)
                for line in lines[1:]:
                    parts = line.split()
                    if human_readable:
                        print(f"{parts[0]:<20} {parts[1]:>10} {parts[2]:>10} {parts[3]:>10} {parts[4]:>5} {parts[5]}")
                    else:
                        print(line)
            except FileNotFoundError:
                print("df: command not found")
            except subprocess.CalledProcessError as e:
                print(f"df: error: {e}")
            return
        elif command_name == "sleep":
            if args and args[0].isdigit():
                try:
                    time.sleep(int(args[0]))
                except ValueError:
                    print("sleep: invalid time interval")
            else:
                print("Usage: sleep <seconds>")
            return
        elif command_name == "date":
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z%z"))
            return
        elif command_name == "calc":
            if args:
                try:
                    result = eval(" ".join(args))
                    print(result)
                except Exception as e:
                    print(f"calc: error evaluating expression: {e}")
            else:
                print("Usage: calc <expression>")
            return
        elif command_name == "checksum":
            if len(args) < 1:
                print("Usage: checksum <file> [md5|sha256]")
                return
            file_path = args[0]
            algorithm = args[1] if len(args) > 1 else "md5"
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                    if algorithm == "md5":
                        print(hashlib.md5(data).hexdigest())
                    elif algorithm == "sha256":
                        print(hashlib.sha256(data).hexdigest())
                    else:
                        print(f"checksum: unknown algorithm '{algorithm}'. Use 'md5' or 'sha256'.")
            except FileNotFoundError:
                print(f"checksum: {file_path}: No such file or directory")
            except OSError as e:
                print(f"checksum: error reading '{file_path}': {e}")
            return
        elif command_name == "type":
            if args:
                command_to_check = args[0]
                if command_to_check in self.aliases:
                    print(f"{command_to_check} is aliased to '{self.aliases[command_to_check]}'")
                elif command_to_check in ["cd", "exit", "help", "alias", "unalias", "history", "jobs", "fg", "bg", "setenv", "getenv", "setvar", "getvar", "echo", "pwd", "ls", "mkdir", "rm", "cp", "mv", "cat", "head", "tail", "grep", "find", "du", "df", "sleep", "date", "calc", "checksum", "type", "watch"]:
                    print(f"{command_to_check} is a built-in shell command")
                elif shutil.which(command_to_check):
                    print(f"{command_to_check} is in {shutil.which(command_to_check)}")
                else:
                    print(f"{command_to_check} not found")
            else:
                print("Usage: type <command>")
            return
        elif command_name == "watch":
            if not args:
                print("Usage: watch [-n <sec>] <command>")
                return
            delay = 2
            watch_command = args
            if args[0] == "-n" and len(args) > 1 and args[1].isdigit():
                delay = int(args[1])
                watch_command = args[2:]
            if not watch_command:
                print("Usage: watch [-n <sec>] <command>")
                return
            try:
                while True:
                    os.system("clear")
                    print(f"Every {delay}s: {' '.join(watch_command)}")
                    subprocess.run(watch_command, shell=False)
                    time.sleep(delay)
            except KeyboardInterrupt:
                print("\nWatch stopped.")
            return

        # --- Placeholder Built-in Commands ---
        elif command_name == "man":
            print(f"man: placeholder for '{' '.join(args)}'")
        elif command_name == "edit":
            print(f"edit: placeholder for '{' '.join(args)}'")
        elif command_name == "tree":
            print(f"tree: placeholder for '{' '.join(args)}'")
        elif command_name == "sort":
            print(f"sort: placeholder for '{' '.join(args)}'")
        elif command_name == "wc":
            print(f"wc: placeholder for '{' '.join(args)}'")
        elif command_name == "patch":
            print(f"patch: placeholder for '{' '.join(args)}'")
        elif command_name == "tar":
            print(f"tar: placeholder for '{' '.join(args)}'")
        elif command_name == "gzip":
            print(f"gzip: placeholder for '{' '.join(args)}'")
        elif command_name == "gunzip":
            print(f"gunzip: placeholder for '{' '.join(args)}'")
        elif command_name == "mount":
            print(f"mount: placeholder for '{' '.join(args)}'")
        elif command_name == "umount":
            print(f"umount: placeholder for '{' '.join(args)}'")
        elif command_name == "top":
            print("top: placeholder")
        elif command_name == "kill":
            print(f"kill: placeholder for '{' '.join(args)}'")
        elif command_name == "login":
            print(f"login: placeholder for '{' '.join(args)}'")
        elif command_name == "logout":
            print("logout: placeholder")
        elif command_name == "whoami":
            print("whoami: placeholder")
        elif command_name == "historysearch":
            print(f"historysearch: placeholder for '{' '.join(args)}'")
        elif command_name == "repeat":
            print(f"repeat: placeholder for '{' '.join(args)}'")
        elif command_name == "geturl":
            print(f"geturl: placeholder for '{' '.join(args)}'")
        elif command_name == "config":
            if args and args[0] == "get":
                print(f"config get: placeholder for '{' '.join(args[1:])}'")
            elif args and args[0] == "set":
                print(f"config set: placeholder for '{' '.join(args[1:])}'")
            else:
                print("config: placeholder")
        elif command_name == "theme":
            print(f"theme: placeholder for '{' '.join(args)}'")
        elif command_name == "keybind":
            print(f"keybind: placeholder for '{' '.join(args)}'")
        elif command_name == "notify":
            print(f"notify: placeholder for '{' '.join(args)}'")
        elif command_name == "progress":
            print(f"progress: placeholder for '{' '.join(args)}'")
        elif command_name == "script":
            print(f"script: placeholder for '{' '.join(args)}'")
        elif command_name == "debug":
            print(f"debug: placeholder for '{' '.join(args)}'")
        elif command_name == "timeit":
            print(f"timeit: placeholder for '{' '.join(args)}'")
        elif command_name == "network":
            if args and args[0] == "info":
                print("network info: placeholder")
            else:
                print("network: placeholder")
        elif command_name == "ping":
            print(f"ping: placeholder for '{' '.join(args)}'")
        elif command_name == "dnslookup":
            print(f"dnslookup: placeholder for '{' '.join(args)}'")
        elif command_name == "portscan":
            print(f"portscan: placeholder for '{' '.join(args)}'")
        elif command_name == "ssh":
            print(f"ssh: placeholder for '{' '.join(args)}'")
        elif command_name == "ftp":
            print(f"ftp: placeholder for '{' '.join(args)}'")
        elif command_name == "mail":
            print(f"mail: placeholder for '{' '.join(args)}'")
        elif command_name == "weather":
            print(f"weather: placeholder for '{' '.join(args)}'")
        elif command_name == "translate":
            print(f"translate: placeholder for '{' '.join(args)}'")
        elif command_name == "news":
            print(f"news: placeholder for '{' '.join(args)}'")
        elif command_name == "stocks":
            print(f"stocks: placeholder for '{' '.join(args)}'")
        elif command_name == "currency":
            print(f"currency: placeholder for '{' '.join(args)}'")
        elif command_name == "reminder":
            print(f"reminder: placeholder for '{' '.join(args)}'")
        elif command_name == "todo":
            print(f"todo: placeholder for '{' '.join(args)}'")
        elif command_name == "calculator":
            print("calculator: placeholder")
        elif command_name == "unitconv":
            print(f"unitconv: placeholder for '{' '.join(args)}'")
        elif command_name == "colortest":
            print("colortest: placeholder")
        elif command_name == "asciiart":
            print(f"asciiart: placeholder for '{' '.join(args)}'")
        elif command_name == "qrgen":
            print(f"qrgen: placeholder for '{' '.join(args)}'")
        elif command_name == "barcode":
            print(f"barcode: placeholder for '{' '.join(args)}'")
        elif command_name == "encrypt":
            print(f"encrypt: placeholder for '{' '.join(args)}'")
        elif command_name == "decrypt":
            print(f"decrypt: placeholder for '{' '.join(args)}'")
        elif command_name == "audioplay":
            print(f"audioplay: placeholder for '{' '.join(args)}'")
        elif command_name == "videoplay":
            print(f"videoplay: placeholder for '{' '.join(args)}'")
        elif command_name == "imageview":
            print(f"imageview: placeholder for '{' '.join(args)}'")
        elif command_name == "pdfview":
            print(f"pdfview: placeholder for '{' '.join(args)}'")
        elif command_name == "systeminfo":
            print("systeminfo: placeholder")
        elif command_name == "processmonitor":
            print("processmonitor: placeholder")
        elif command_name == "diskmanager":
            print("diskmanager: placeholder")
        elif command_name == "usermanager":
            print("usermanager: placeholder")
        elif command_name == "servicemanager":
            print("servicemanager: placeholder")
        elif command_name == "packagemanager":
            print(f"packagemanager: placeholder for '{' '.join(args)}'")
        elif command_name == "virtualenv":
            print(f"virtualenv: placeholder for '{' '.join(args)}'")
        elif command_name == "docker":
            print(f"docker: placeholder for '{' '.join(args)}'")
        elif command_name == "git":
            print(f"git: placeholder for '{' '.join(args)}'")
        elif command_name == "sqlite":
            print(f"sqlite: placeholder for '{' '.join(args)}'")
        elif command_name == "blockchain":
            print(f"blockchain: placeholder for '{' '.join(args)}'")
        elif command_name == "cloud":
            print(f"cloud: placeholder for '{' '.join(args)}'")

        # --- External Command Execution with Piping and Redirection ---
        else:
            process = None
            if '|' in command:
                pipes = [shlex.split(p) for p in command.split('|')]
                last_output = None
                for i, cmd_parts in enumerate(pipes):
                    stdout_pipe = subprocess.PIPE if i < len(pipes) - 1 else sys.stdout
                    process = subprocess.Popen(cmd_parts, stdin=last_output, stdout=stdout_pipe, stderr=sys.stderr)
                    if last_output is not None:
                        last_output.close()
                    last_output = process.stdout
                if process:
                    process.wait()
            else:
                stdout_redirect = None
                stderr_redirect = None
                mode = "w"
                command_parts = []

                for i, part in enumerate(parts):
                    if part == ">":
                        if i + 1 < len(parts):
                            stdout_redirect = open(parts[i + 1], "w")
                            break
                        else:
                            print("Error: No file specified for output redirection.")
                            return
                    elif part == ">>":
                        if i + 1 < len(parts):
                            stdout_redirect = open(parts[i + 1], "a")
                            break
                        else:
                            print("Error: No file specified for appending output.")
                            return
                    elif part == "2>":
                        if i + 1 < len(parts):
                            stderr_redirect = open(parts[i + 1], "w")
                            break
                        else:
                            print("Error: No file specified for stderr redirection.")
                            return
                    elif part == "&>":
                        if i + 1 < len(parts):
                            redirect_file = open(parts[i + 1], "w")
                            stdout_redirect = redirect_file
                            stderr_redirect = redirect_file
                            break
                        else:
                            print("Error: No file specified for stdout and stderr redirection.")
                            return
                    command_parts.append(part)

                try:
                    if command.endswith('&'):
                        bg_command = " ".join(command_parts[:-1]).strip()
                        bg_parts = shlex.split(bg_command)
                        if bg_parts:
                            process = subprocess.Popen(bg_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            job_id = self.next_job_id
                            self.jobs[job_id] = {"process": process, "command": bg_command, "status": "running"}
                            print(f"[{job_id}] {bg_command} &")
                            self.next_job_id += 1
                    else:
                        process = subprocess.run(command_parts, stdout=stdout_redirect, stderr=stderr_redirect, check=False)
                except FileNotFoundError:
                    print(f"{command_name}: command not found")
                except Exception as e:
                    print(f"Error executing command: {e}")
                finally:
                    if stdout_redirect:
                        stdout_redirect.close()
                    if stderr_redirect:
                        stderr_redirect.close()

    def handle_signal(self, signum, frame):
        if signum == signal.SIGTSTP:  # Ctrl+Z
            if hasattr(self, 'foreground_process') and self.foreground_process:
                print("\nSuspended")
                self.foreground_process.send_signal(signal.SIGTSTP)
                job_id = self.next_job_id
                self.jobs[job_id] = {"process": self.foreground_process, "command": self.foreground_command, "status": "suspended"}
                print(f"[{job_id}] Suspended {self.foreground_command}")
                self.next_job_id += 1
                self.foreground_process = None
                self.foreground_command = None

    def format_permissions(self, mode):
        perms = ""
        if os.path.isdir(f"."):
            perms += "d"
        elif os.path.islink(f"."):
            perms += "l"
        else:
            perms += "-"
        # User permissions
        perms += "r" if (mode & 0o400) else "-"
        perms += "w" if (mode & 0o200) else "-"
        perms += "x" if (mode & 0o100) else "-"
        # Group permissions
        perms += "r" if (mode & 0o040) else "-"
        perms += "w" if (mode & 0o020) else "-"
        perms += "x" if (mode & 0o010) else "-"
        # Others permissions
        perms += "r" if (mode & 0o004) else "-"
        perms += "w" if (mode & 0o002) else "-"
        perms += "x" if (mode & 0o001) else "-"
        return perms

    def get_user_name(self, uid):
        try:
            import pwd
            return pwd.getpwuid(uid).pw_name
        except ImportError:
            return str(uid)

    def get_group_name(self, gid):
        try:
            import grp
            return grp.getgrgid(gid).gr_name
        except ImportError:
            return str(gid)

    def format_size(self, size):
        for unit in ['B', 'K', 'M', 'G', 'T', 'P']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}E"

    def myshell(self):
        if hasattr(signal, 'SIGTSTP'):
            signal.signal(signal.SIGTSTP, self.handle_signal)
        while True:
            try:
                cmd = input(f"{os.getcwd()}$ ")
            except EOFError:
                print("\nExiting...")
                break
            except KeyboardInterrupt:
                print("\n")
                continue

            self.foreground_command = cmd.strip()
            if self.foreground_command:
                readline.add_history(self.foreground_command)
                self.execute_command(self.foreground_command)
                self.foreground_process = None
                self.foreground_command = None
if __name__ == "__main__":
    shell = MyShell()
    shell.myshell()