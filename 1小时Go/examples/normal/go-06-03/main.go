package main

import "fmt"

func main() {
	var scores map[string]int
	fmt.Println(scores == nil)
	fmt.Println(scores["小林"])
	scores = make(map[string]int)
	scores["小林"] = 85
	fmt.Println(scores["小林"])
}
