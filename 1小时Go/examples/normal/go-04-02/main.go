package main

import "fmt"

func main() {
	if score := 88; score >= 90 {
		fmt.Println("优秀")
	} else if score >= 60 {
		fmt.Println("及格")
	} else {
		fmt.Println("未及格")
	}
}
