package main

import "fmt"
import "strings"

func main() {
	text := " Go基础 "
	clean := strings.TrimSpace(text)
	fmt.Println(clean)
	fmt.Println(strings.Contains(clean, "Go"))
	parts := strings.Split("小林,85", ",")
	fmt.Println(parts[0], parts[1])
}
