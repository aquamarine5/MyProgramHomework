#include<iostream>

using namespace std;

extern "C" int memoryAddressing(
	int i,
	int* v1,
	int* v2,
	int* v3,
	int* v4,
	int* v5
);

extern "C" int numFibVals;

int main() {
	int v1, v2, v3, v4, v5;
	int ret;
	for (int i = 0; i < numFibVals; ++i) {
		ret = memoryAddressing(i, &v1, &v2, &v3, &v4, &v5);
		printf("i=%2d, ret=%d, v1=%5d, v2=%5d, v3=%5d, v4=%5d, v5=%5d\n",
			i, ret, v1, v2, v3, v4, v5);
	}
	return 0;
}