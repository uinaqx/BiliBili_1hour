package main

import "fmt"
import "errors"

func average(scores []int) (float64, error) {
	if len(scores) == 0 {
		return 0, errors.New("没有成绩")
	}
	total := 0
	for _, score := range scores {
		total += score
	}
	return float64(total) / float64(len(scores)), nil
}
func main() {
	value, err := average([]int{80, 90})
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Printf("平均分：%.1f\n", value)
}
