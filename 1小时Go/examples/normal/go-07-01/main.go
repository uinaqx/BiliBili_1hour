package main

import "fmt"

func greet(name string) {
	fmt.Println("你好，" + name)
}
func main() {
	greet("小林")
	greet("小陈")
}
