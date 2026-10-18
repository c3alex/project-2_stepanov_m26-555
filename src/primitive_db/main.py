#!/usr/bin/env python3

from primitive_db.engine import run


def main() -> None:
    """Точка входа: запускает интерактивную базу данных.

    Side effects:
        Передаёт управление основному циклу ``run()``.
    """
    run()


if __name__ == "__main__":
    main()
