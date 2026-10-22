package main

import "fmt"

func main() {
	score := 85
	attended := true
	fmt.Println(score >= 60)
	fmt.Println(score >= 60 && attended)
	fmt.Println(score < 60 || !attended)
}
