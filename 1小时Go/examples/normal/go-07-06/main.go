package main

import "fmt"

func main() {
	score := 80
	defer fmt.Println(score)
	score = 90
	fmt.Println(score)
}
