package main

import "fmt"

func main() {
	scores := map[string]int{"小林": 0}
	value, ok := scores["小王"]
	fmt.Println(value, ok)
	value, ok = scores["小林"]
	fmt.Println(value, ok)
}
