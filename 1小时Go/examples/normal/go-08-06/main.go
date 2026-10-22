package main

import "fmt"

type Student struct{ Score int }

func main() {
	first := Student{Score: 80}
	second := first
	pointer := &first
	second.Score = 90
	pointer.Score = 85
	fmt.Println(first.Score, second.Score)
}
