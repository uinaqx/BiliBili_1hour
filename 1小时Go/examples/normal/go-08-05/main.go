package main

import "fmt"

type Student struct{ Score int }

func setScore(student *Student) {
	student.Score = 85
}
func main() {
	s := Student{Score: 80}
	setScore(&s)
	fmt.Println(s.Score)
}
