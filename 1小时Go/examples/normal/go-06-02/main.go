package main

import "fmt"

func main() {
	scores := map[string]int{"小林": 0}
	score, ok := scores["小林"]
	fmt.Println(score, ok)
	delete(scores, "小林")
	score, ok = scores["小林"]
	fmt.Println(score, ok)
}
