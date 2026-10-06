"""Эмулятор командной оболочки UNIX-подобной ОС."""

import getpass
import socket
import sys


def get_prompt():
    """Возвращает приглашение вида user@host:~$ по данным ОС."""
    user = getpass.getuser()
    host = socket.gethostname().split(".")[0]
    return f"{user}@{host}:~$ "


def act(line):
    """Разбирает строку на команду и аргументы и выполняет её."""
    parts = line.split()
    if not parts:
        return ""
    cmd = parts[0]
    args = parts[1:]
    if cmd == "exit":
        sys.exit()
    elif cmd == "ls":
        return f"ls {args}"
    elif cmd == "cd":
        if len(args) > 1:
            raise ValueError("cd: слишком много аргументов")
        return f"cd {args}"
    else:
        raise ValueError(f"{cmd}: команда не найдена")


def repl():
    """Читает команды пользователя и печатает результат."""
    while True:
        try:
            line = input(get_prompt())
        except EOFError:
            break
        try:
            result = act(line)
        except ValueError as error:
            result = str(error)
        if result:
            print(result)


if __name__ == "__main__":
    repl()
