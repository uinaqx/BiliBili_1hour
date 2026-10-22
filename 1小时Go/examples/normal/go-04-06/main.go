package main

import "fmt"

func main() {
	for n := 1; n <= 5; n++ {
		if n == 2 {
			continue
		}
		if n == 4 {
			break
		}
		fmt.Println(n)
	}
}
