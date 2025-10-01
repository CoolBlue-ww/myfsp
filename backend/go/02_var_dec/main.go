package main

import "fmt"

func main() {
	num := 100
	fmt.Println("寻找100-1000以内的水仙花数...")
	for ; num < 1000; num++ {
		hundreds := num / 100
		tens := (num % 100) / 10
		uints := num % 10
		sum := hundreds*hundreds*hundreds + tens*tens*tens + uints*uints*uints
		if sum == num {
			fmt.Printf("%d是水仙花数\n", num)
		}
	}
}
