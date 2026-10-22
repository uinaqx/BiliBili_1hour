package main

import "fmt"

func main() {
	var score int
	count, err := fmt.Scan(&score)
	if err != nil || count != 1 {
		fmt.Println("请输入整数")
		return
	}
	fmt.Println(score + 5)
}
