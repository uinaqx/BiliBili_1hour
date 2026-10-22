package main

import "fmt"
import "errors"

func checkScore(score int) error {
	if score < 0 || score > 100 {
		return errors.New("成绩超出范围")
	}
	return nil
}
func main() {
	err := checkScore(120)
	if err != nil {
		fmt.Println(err)
	}
}
