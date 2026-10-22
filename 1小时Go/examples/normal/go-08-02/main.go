package main

import "fmt"

func addLocal(score int)     { score += 5 }
func addOriginal(score *int) { *score += 5 }
func main() {
	score := 80
	addLocal(score)
	fmt.Println(score)
	addOriginal(&score)
	fmt.Println(score)
}
