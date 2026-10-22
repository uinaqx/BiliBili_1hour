package main

import "fmt"
import "unicode/utf8"

func main() {
	text := "Go语"
	fmt.Println(len(text), utf8.RuneCountInString(text))
	for position, ch := range text {
		fmt.Printf("%d %c\n", position, ch)
	}
}
