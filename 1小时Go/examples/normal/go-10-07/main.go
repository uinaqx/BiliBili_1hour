package main

import "fmt"
import "strconv"

func main() {
	score, err := strconv.Atoi("hello")
	if err != nil {
		fmt.Println("请输入整数")
		return
	}
	if score < 0 || score > 100 {
		fmt.Println("成绩超出范围")
		return
	}
	fmt.Println("成绩：", score)
}
