package main

import "fmt"
import "strconv"

func main() {
	text := "85"
	score, err := strconv.Atoi(text)
	if err != nil {
		fmt.Println("请输入整数")
		return
	}
	fmt.Println(score + 5)
	fmt.Println(strconv.Itoa(score))
}
