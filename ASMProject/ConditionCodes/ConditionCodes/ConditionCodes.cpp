// ConditionCodes.cpp : This file contains the 'main' function. Program execution begins and ends there.
//


#include <iostream>

//using conditional jumps
extern "C" int SignedMinA(int a, int b, int c);
extern "C" int SignedMaxA(int a, int b, int c);

//conditional moves
extern "C" int SignedMinB(int a, int b, int c);
extern "C" int SignedMaxB(int a, int b, int c);


int main()
{
	int a, b, c;
	int max_a, min_a, max_b, min_b;

	a = 345;
	b = -783;
	c = 34;
	min_a = SignedMinA(a, b, c);
	max_a = SignedMaxA(a, b, c);

	min_b = SignedMinB(a, b, c);
	max_b = SignedMaxB(a, b, c);

	printf("SignedMinA(%4d, %4d, %4d) = %4d\n", a, b, c, min_a);
	printf("SignedMinB(%4d, %4d, %4d) = %4d\n", a, b, c, min_b);

	printf("SignedMaxA(%4d, %4d, %4d) = %4d\n", a, b, c, max_a);
	printf("SignedMaxB(%4d, %4d, %4d) = %4d\n", a, b, c, max_b);


	 return 0;



}

