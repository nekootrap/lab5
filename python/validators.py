"""Универсальный валидатор объектов по аннотациям типов.

См. лекцию 5: слайд 14 (рефлексия для валидации).
"""

from typing import Any


class ValidationError(Exception):
    """Исключение валидации.

    Атрибуты:
        field: имя поля, не прошедшего проверку (или "" для общей ошибки);
        message: человекочитаемое описание проблемы.
    """

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}" if field else message)


def validate(obj: Any) -> list[str]:
    """Проверяет атрибуты объекта obj на соответствие аннотациям типов.

    Алгоритм:
      - получить аннотации класса: typing.get_type_hints(type(obj));
      - для каждого поля проверить значение на соответствие типу:
          * примитивные типы (int, str, float, bool) — через isinstance;
          * None — ошибка для обычных типов (допускается не обрабатывать
            Optional — решение отразить в отчёте);
          * класс домена (Address, Product, User) — рекурсивный вызов validate;
          * list — проверка каждого элемента;
      - все найденные ошибки собираются в один список.

    Возвращает:
        список сообщений об ошибках; пустой список — объект валиден.
        Формат сообщения: "<ИмяКласса>.<поле>: ожидался <тип>, получен <тип>"
        (точный формат — на усмотрение студента, главное — информативность).
    """
    raise NotImplementedError("validate: требуется реализовать валидацию")


def validate_or_raise(obj: Any) -> None:
    """Выбрасывает ValidationError, если validate(obj) вернул непустой список."""
    raise NotImplementedError("validate_or_raise: требуется реализовать")
