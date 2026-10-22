package main

import "fmt"

func main() {
	defer fmt.Println("先登记")
	defer fmt.Println("后登记")
	fmt.Println("处理中")
}
