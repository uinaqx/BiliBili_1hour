package main

import "fmt"

func main() {
	total := 0
	for n := 1; n <= 4; n++ {
		if n == 3 {
			continue
		}
		total += n
	}
	fmt.Println(total)
}
