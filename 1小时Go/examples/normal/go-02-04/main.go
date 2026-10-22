package main

import "fmt"

func main() {
	const passScore = 60
	score := 85
	fmt.Println(score >= passScore)
	const message = "成绩已保存"
	fmt.Println(message)
}
