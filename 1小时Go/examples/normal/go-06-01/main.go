package main

import "fmt"

func main() {
	scores := map[string]int{"小林": 85, "小陈": 92}
	fmt.Println(scores["小林"])
	fmt.Println(scores["小王"])
	fmt.Println(len(scores))
}
