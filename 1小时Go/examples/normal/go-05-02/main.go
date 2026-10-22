package main

import "fmt"

func main() {
	scores := [3]int{80, 90, 70}
	backup := scores
	backup[0] = 99
	fmt.Println(scores)
	fmt.Println(backup)
}
