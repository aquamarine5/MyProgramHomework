#include <iostream>
#include <stdlib.h>

// y is output array, x is input array, n is number of elements
extern "C" void Reverser(int* y, const int* x, int n);

extern "C" void SumArray(int* arr, int size, int* result);

int main() {
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