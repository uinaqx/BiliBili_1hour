package main

import "fmt"

func divide(total, count int) (int, bool) {
	if count == 0 {
		return 0, false
	}
	return total / count, true
}
func main() {
	result, ok := divide(10, 2)
	fmt.Println(result, ok)
}
