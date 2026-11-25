package main

import (
	"fmt"
	"time"
)

func main() {
	u := User{
		Name:       "Анна",
		Email:      "anna@mail.ru",
		Address:    Address{City: "Ставрополь", Street: "Ленина", House: "1"},
		Registered: time.Date(2024, 1, 1, 12, 0, 0, 0, time.UTC),
	}
	fmt.Println("Модель Go инициализирована:", u.Name, u.Address.City)
}
