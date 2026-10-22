package main

import "fmt"

type Student struct {
	Name  string
	Score int
}

func main() {
	student := Student{Name: "小林", Score: 80}
	fmt.Println(student.Name, student.Score)
}
