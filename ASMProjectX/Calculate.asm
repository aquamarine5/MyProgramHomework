.386
.model flat, c
.code

; int IntegerMultiplyDivide(int a, int b, int* product, int* quotient, int* remainder)
IntegerMultiplyDivide PROC
	PUSH EBP
	MOV EBP, ESP
	PUSH ESI
	PUSH EBX

	MOV EBX, [EBP+8]  ; int a
	MOV ECX, [EBP+12] ; int b
	CMP ECX, 0
	JE @InvalidDivisor

	; product = a * b
	MOV EAX, EBX
	IMUL ECX ; EAX = EAX * ECX
	MOV ESI, [EBP+16] ; int* product
	MOV [ESI], EAX

	; quotient = a / b, remainder = a % b
	MOV EAX, EBX
	CDQ
	IDIV ECX ; EAX ... EDX = EAX / ECX
	MOV ESI, [EBP+20] ; int* quotient
	MOV [ESI], EAX
	MOV ESI, [EBP+24] ; int* remainder
	MOV [ESI], EDX

	MOV EAX, 1
	JMP @Done

@InvalidDivisor:
	MOV EAX, 0

@Done:
	POP EBX
	POP ESI
	POP EBP
	RET
IntegerMultiplyDivide ENDP
END