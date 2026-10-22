package main

import "fmt"

func main() {
	scores := []int{80, 90}
	for i := range scores {
		scores[i] += 5
	}
	backup := make([]int, len(scores))
	count := copy(backup, scores)
	backup[0] = 99
	fmt.Println(scores, backup, count)
}
