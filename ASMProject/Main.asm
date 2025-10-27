.386
.model flat, c
.code

SumArray PROC
	; extern "C" void SumArray(int* arr, int size, int* result);
	; ESI for source array, EDI for destination address, ECX for counter
	PUSH EBP
	MOV EBP, ESP
	PUSH ESI
	PUSH EDI
	XOR EAX, EAX
	MOV ESI, [EBP+8]
	MOV ECX, [EBP+12]
	MOV EDI, [EBP+16]
	TEST ECX, ECX
	@Loop:
		ADD EAX, [ESI]
		ADD ESI, 4
		DEC ECX
		JNZ @Loop
	MOV [EDI], EAX
	MOV EAX, 1
	POP EDI
	POP ESI
	POP EBP
	RET
SumArray ENDP

Reverser PROC
	PUSH EBP ; PUSH/POP followed the stack order
	MOV EBP, ESP
	PUSH ESI
	PUSH EDI ; EBP->ESI->EDI, by stack

	XOR EAX,EAX ; clear the EAX to 0 

	; -or- MOV EAX,0
	; EBP+0: old EBP
	; EBP+4: return address
	MOV EDI, [EBP+8]  ; address of array y, reversed
	MOV ESI, [EBP+12] ; address of array x, original
	MOV ECX, [EBP+16] ; number of n (size)
	TEST ECX,ECX ; test if ECX == 0, which means no elements to copy
	
	LEA ESI, [ESI+ECX*4-4] ; Load Effective Address
	; calculate the address of the last element of array x without accessing the memory
	; ESI is the address of x[0]
	; ECX is the n (number of elements)
	; ESI = ESI + (n - 1) * 4  (4 bytes per int, DWORD)
	; 0    1    2    3    4    5     , ECX=6
	; ^ESI                     ^LEA
	; x[0]                     x[5]  , *not x[6], is invalid*


	PUSHFD ; push all CPU flags onto stack
	STD ; set direction flag to decrement (DF=0 -> DF=1)
	@@: LODSD ; Load String DWORD
		; controlled by DF, read a DWORD from [ESI] into EAX
		; ESI = ESI - 4 (because DF=1)

		; array y is EDI
		MOV [EDI], EAX ; [EDI] = EAX, [EDI] means the address and the EDI is not modified.
		ADD EDI, 4 ; array y moves forward
		DEC ECX ; ECX (size n) -= 1
		JNZ @B ; jump to the position of @@: if ECX != 0 after decrement
	
	POPFD ; restore all CPU flags from stack
	MOV EAX,1 ; set return value EAX to 1 (success)
	POP EDI ; EBP<-ESI<-EDI, by stack
	POP ESI
	POP EBP
	RET

Reverser ENDP
END