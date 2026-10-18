"""Разбор значений и условий ``where``/``set`` из пользовательских команд.

Строковые значения всегда должны быть в кавычках (``"..."`` или ``'...'``),
логические записываются как ``true``/``false``, целые числа без кавычек.
"""

import re
from typing import Any

QUOTES = ("'", '"')
INT_RE = re.compile(r"[+-]?\d+")


def _quote_mask(text: str) -> list[bool]:
    """Отмечает для каждого символа, находится ли он внутри кавычек.

    Raises:
        ValueError: Если в строке есть незакрытая кавычка.
    """
    mask = []
    quote = None
    for char in text:
        if quote is None and char in QUOTES:
            quote = char
            mask.append(True)
        elif char == quote:
            quote = None
            mask.append(True)
        else:
            mask.append(quote is not None)
    if quote is not None:
        raise ValueError(f"незакрытая кавычка в {text!r}")
    return mask


def split_outside_quotes(text: str, sep: str) -> list[str]:
    """Делит строку по разделителю, игнорируя разделители внутри кавычек.

    Args:
        text: Исходная строка.
        sep: Разделитель-регулярное выражение (например, ``","``).

    Returns:
        Список частей без пробелов по краям.

    Raises:
        ValueError: Если в строке есть незакрытая кавычка.
    """
    mask = _quote_mask(text)
    parts = []
    start = 0
    for match in re.finditer(sep, text, flags=re.IGNORECASE):
        if not mask[match.start()]:
            parts.append(text[start : match.start()].strip())
            start = match.end()
    parts.append(text[start:].strip())
    return parts


def find_keyword(text: str, keyword: str) -> int:
    """Ищет ключевое слово (целым словом, без учёта регистра) вне кавычек.

    Args:
        text: Строка для поиска.
        keyword: Ключевое слово, например ``"where"``.

    Returns:
        Позиция начала ключевого слова или ``-1``, если оно не найдено.

    Raises:
        ValueError: Если в строке есть незакрытая кавычка.
    """
    mask = _quote_mask(text)
    for match in re.finditer(rf"\b{keyword}\b", text, flags=re.IGNORECASE):
        if not mask[match.start()]:
            return match.start()
    return -1


def parse_value(raw: str) -> Any:
    """Преобразует текстовое значение в объект Python.

    Args:
        raw: Значение, например ``'"Sergei"'``, ``"28"`` или ``"true"``.

    Returns:
        ``str`` для значения в кавычках, ``bool`` для ``true``/``false``,
        ``int`` для целого числа.

    Raises:
        ValueError: Если значение не удалось распознать.
    """
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] in QUOTES and raw[-1] == raw[0]:
        return raw[1:-1]
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    if INT_RE.fullmatch(raw):
        return int(raw)
    raise ValueError(f"не удалось распознать значение {raw!r}")


def parse_values(text: str) -> list[Any]:
    """Разбирает список значений вида ``("Sergei", 28, true)``.

    Raises:
        ValueError: Если нет скобок или значение не распознано.
    """
    text = text.strip()
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError("значения должны быть в скобках")
    inner = text[1:-1].strip()
    if not inner:
        return []
    return [parse_value(part) for part in split_outside_quotes(inner, ",")]


def _parse_assignments(parts: list[str]) -> dict[str, Any]:
    """Превращает список строк ``столбец = значение`` в словарь."""
    clause: dict[str, Any] = {}
    for part in parts:
        column, sep, value = part.partition("=")
        column = column.strip()
        if not sep or not column.isidentifier():
            raise ValueError(f"ожидалось 'столбец = значение', получено {part!r}")
        clause[column] = parse_value(value)
    return clause


def parse_where(text: str) -> dict[str, Any]:
    """Разбирает условие ``where``: ``age = 28`` -> ``{'age': 28}``.

    Несколько условий можно объединить через ``and``.

    Raises:
        ValueError: Если условие записано некорректно.
    """
    return _parse_assignments(split_outside_quotes(text, r"\band\b"))


def parse_set(text: str) -> dict[str, Any]:
    """Разбирает выражение ``set``: ``age = 29, name = "Ivan"`` в словарь.

    Raises:
        ValueError: Если выражение записано некорректно.
    """
    return _parse_assignments(split_outside_quotes(text, ","))
