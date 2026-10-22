package main

import "fmt"

func main() {
	scores := []int{80, 90, 70}
	for index, score := range scores {
		fmt.Println(index, score)
	}
}
