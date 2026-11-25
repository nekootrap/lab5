"""Модели домена: Address, Product, User.

См. лекцию 5, слайды 13 и 26: модели используются во всех частях работы.
"""

import datetime
from dataclasses import dataclass, field


@dataclass
class Address:
    """Адрес. Только плоские строковые поля."""

    city: str
    street: str
    house: str


@dataclass
class Product:
    """Товар. Содержит вложенный объект Address (адрес склада)."""

    name: str
    price: float
    warehouse: Address  # вложенный объект — ключевой случай для сериализации


@dataclass
class User:
    """Пользователь. Содержит вложенный Address и список Products."""

    name: str
    email: str
    address: Address
    registered: datetime.datetime = field(
        default_factory=lambda: datetime.datetime(2024, 1, 1, 12, 0, 0)
    )
    products: list[Product] = field(default_factory=list)
