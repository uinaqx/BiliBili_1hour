package main

import "fmt"

func addBonus(score, bonus int) int {
	return score + bonus
}
func main() {
	result := addBonus(80, 5)
	fmt.Println(result)
}
