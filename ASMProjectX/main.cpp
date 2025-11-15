/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 * lovely lonely, but be a quokka.
 */
#include <iostream>
#include <stdlib.h>

// y is output array, x is input array, n is number of elements
extern "C" void Reverser(int* y, const int* x, int n);

extern "C" void SumArray(int* arr, int size, int* result);

extern "C" int IntegerMultiplyDivide(int a, int b, int* product, int* quotient, int* remainder);

int main() {
	int a = 22, b = 5;
	int product, quotient, remainder;
	IntegerMultiplyDivide(a, b, &product, &quotient, &remainder);
	printf("a=%d, b=%d, a*b=%d, a/b=%d...%d", a, b, product, quotient, remainder);
}

int mainx() {
	const int n = 10;
	int x[n], y[n], result;
	for (int i = 0; i < n; i++)
		x[i] = i;
	Reverser(y, x, n);
	SumArray(x, n, &result);
	printf("\n----------------Array Reverser-----------\n");
	for (int i = 0; i < n; i++)
		printf(" x: %5d\ty: %5d\n", x[i], y[i]);
	printf("\n----------------Sum Array-----------\n");
	printf(" Sum: %d\n", result);
	return 0;
}