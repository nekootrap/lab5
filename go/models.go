package main

import "time"

// Address — адрес. Только экспортируемые строковые поля.
type Address struct {
	City   string
	Street string
	House  string
}

// Product — товар. Содержит вложенный Address (адрес склада).
type Product struct {
	Name      string
	Price     float64
	Warehouse Address // вложенный объект — ключевой случай для сериализации
}

// User — пользователь. Содержит вложенный Address и список Product.
type User struct {
	Name       string
	Email      string
	Address    Address
	Registered time.Time // ключевое поле для сериализации datetime
	Products   []Product
}
