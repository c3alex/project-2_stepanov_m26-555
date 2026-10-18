"""Вспомогательные функции для работы с файлами базы данных."""

import json
import os
from typing import Any

DATA_DIR = "data"


def load_metadata(filepath: str) -> dict[str, Any]:
    """Загружает метаданные базы данных из JSON-файла.

    Args:
        filepath: Путь к JSON-файлу с метаданными.

    Returns:
        Словарь с метаданными. Если файл не найден, возвращается
        пустой словарь ``{}``.

    Raises:
        json.JSONDecodeError: Если файл существует, но содержит
            некорректный JSON.
    """
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict[str, Any]) -> None:
    """Сохраняет метаданные базы данных в JSON-файл.

    Args:
        filepath: Путь к JSON-файлу с метаданными.
        data: Словарь с метаданными для сохранения.

    Side effects:
        Создаёт или полностью перезаписывает файл ``filepath``.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def _table_data_path(table_name: str) -> str:
    """Возвращает путь к JSON-файлу с данными таблицы.

    Args:
        table_name: Имя таблицы.

    Returns:
        Путь вида ``data/<table_name>.json``.
    """
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name: str) -> list[dict[str, Any]]:
    """Загружает записи таблицы из файла ``data/<table_name>.json``.

    Args:
        table_name: Имя таблицы.

    Returns:
        Список записей (словарей ``{столбец: значение}``). Если файл
        не найден, возвращается пустой список ``[]``.

    Raises:
        json.JSONDecodeError: Если файл существует, но содержит
            некорректный JSON.
    """
    try:
        with open(_table_data_path(table_name), encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict[str, Any]]) -> None:
    """Сохраняет записи таблицы в файл ``data/<table_name>.json``.

    Args:
        table_name: Имя таблицы.
        data: Список записей для сохранения.

    Side effects:
        Создаёт директорию ``data/`` при необходимости и полностью
        перезаписывает файл с данными таблицы.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_table_data_path(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name: str) -> None:
    """Удаляет файл с данными таблицы, если он существует.

    Args:
        table_name: Имя таблицы.

    Side effects:
        Удаляет файл ``data/<table_name>.json``.
    """
    try:
        os.remove(_table_data_path(table_name))
    except FileNotFoundError:
        pass
