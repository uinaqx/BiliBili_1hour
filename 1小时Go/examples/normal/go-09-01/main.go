package main

import "fmt"

type Student struct{ Score int }

func (s Student) Passed() bool {
	return s.Score >= 60
}
func main() {
	student := Student{Score: 80}
	fmt.Println(student.Passed())
}
