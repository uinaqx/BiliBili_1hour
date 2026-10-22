package main

import "fmt"

func main() {
	var name string
	count, err := fmt.Scan(&name)
	if err != nil {
		fmt.Println("输入失败")
		return
	}
	fmt.Println(count, name)
}
