package main

import "fmt"

func main() {
	score := 80
	pointer := &score
	*pointer = 85
	fmt.Println(score)
	fmt.Println(*pointer)
}
