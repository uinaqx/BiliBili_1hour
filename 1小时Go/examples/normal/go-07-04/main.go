package main

import "fmt"

func sum(values ...int) int {
	total := 0
	for _, value := range values {
		total += value
	}
	return total
}
func main() {
	scores := []int{80, 90}
	fmt.Println(sum(1, 2, 3))
	fmt.Println(sum(scores...))
}
