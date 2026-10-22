package main

import "fmt"

func main() {
	scores := []int{80, 90, 70}
	part := scores[1:3]
	part[0] = 95
	fmt.Println(scores)
	fmt.Println(part)
}
