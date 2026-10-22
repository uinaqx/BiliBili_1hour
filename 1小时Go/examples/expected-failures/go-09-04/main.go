package main

import "fmt"

type Reporter interface{ Report() string }
type Student struct{ Name string }

func show(r Reporter) { fmt.Println(r.Report()) }
func main() {
	student := Student{Name: "小林"}
	show(student)
}
