package main

import "fmt"

func main() {
	attempts := 1
	for attempts <= 3 {
		fmt.Println("第", attempts, "次尝试")
		attempts++
	}
}
