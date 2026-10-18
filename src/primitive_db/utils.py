"""Вспомогательные функции для работы с файлами базы данных."""

import json
from typing import Any


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
