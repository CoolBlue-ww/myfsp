package main

import "fmt"

func main() {
	var names = []string{"张三", "李四", "王二麻子"}
	fmt.Println("中奖名单：", names)

	args := make([]string, 2, 3)
	fmt.Println("args:", args, "len:", len(args), "cap:", cap(args))
}
