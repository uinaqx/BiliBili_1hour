package main

import "fmt"
import "os"

func main() {
	data := []byte("小林,85\n小陈,92")
	err := os.WriteFile("scores.txt", data, 0600)
	if err != nil {
		fmt.Println("写入失败")
		return
	}
	saved, err := os.ReadFile("scores.txt")
	if err != nil {
		fmt.Println("读取失败")
		return
	}
	fmt.Print(string(saved))
}
