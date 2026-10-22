package main

import "fmt"

type Student struct {
	Name  string
	Score int
}

func main() {
	first := Student{Name: "小林", Score: 80}
	second := first
	second.Score = 90
	fmt.Println(first.Score, second.Score)
}
