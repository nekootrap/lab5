package main

// Serializable — интерфейс для типов, умеющих превращать себя в словарь.
type Serializable interface {
	Serialize() map[string]any
}

func describe(x any) string {
	panic("not implemented: describe")
}

func safeToInt(x any) (int, bool) {
	panic("not implemented: safeToInt")
}

func serializeAny(x any) map[string]any {
	panic("not implemented: serializeAny")
}
