package main

import "fmt"

func main() {
	score := 88
	switch {
	case score >= 90:
		fmt.Println("优秀")
	case score >= 60:
		fmt.Println("及格")
	default:
		fmt.Println("未及格")
	}
}
