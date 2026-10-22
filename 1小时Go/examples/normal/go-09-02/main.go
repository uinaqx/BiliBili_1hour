package main

import "fmt"

type Student struct{ Score int }

func (s *Student) AddBonus(bonus int) {
	s.Score += bonus
}
func main() {
	student := Student{Score: 80}
	student.AddBonus(5)
	fmt.Println(student.Score)
}
