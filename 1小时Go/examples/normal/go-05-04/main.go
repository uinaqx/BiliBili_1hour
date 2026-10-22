package main

import "fmt"

func main() {
	scores := make([]int, 2, 4)
	scores[0], scores[1] = 80, 90
	scores = append(scores, 70)
	fmt.Println(scores)
	fmt.Println(len(scores), cap(scores))
}
