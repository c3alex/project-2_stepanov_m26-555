import prompt


def welcome():
    """Показывает приветствие и доступные команды."""
    print(" project")
    print()

    while True:
        print(" ***")
        print(" <command> exit - выйти из программы")
        print(" <command> help - справочная информация")
        command = prompt.string(" Введите команду: ")

        if command == "exit":
            return
        if command == "help":
            continue

        print(" Неизвестная команда.")
