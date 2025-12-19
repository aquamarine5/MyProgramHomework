.386
.model flat, c
.const
fibVals DWORD 0,1,1,2,3,5,8,13,21,34,55,89,144,233,377,610
numFibVals DWORD ($-fibVals)/TYPE fibVals
PUBLIC numFibVals

.code

; int memoryAddressing(
;	int i,
;	int* v1,
;	int* v2,
;	int* v3,
;	int* v4,
;	int* v5
; )
memoryAddressing PROC
	PUSH EBP
	MOV EBP, ESP
	PUSH EBX
	PUSH ESI
	PUSH EDI
	XOR EAX, EAX

	MOV ECX, [EBP+8] ; int i
	CMP ECX, 0
	JL @InvalidIndex 

	CMP ECX, numFibVals
	JGE @InvalidIndex

	; Example 1: Base Register Addressing
	MOV EBX, OFFSET fibVals
	MOV ESI, [EBP+8]
	SHL ESI, 2
	ADD EBX, ESI
	MOV EAX, [EBX]
	MOV EDI, [EBP+12] ; int* v1
	MOV [EDI], EAX

	; Example 2: Base + Displacement Addressing
	MOV ESI, [EBP+8]
	SHL ESI, 2
	MOV EAX, [ESI+fibVals]
	MOV EDI, [EBP+16] ; int* v2
	MOV [EDI], EAX

	; Example 3: Base + Index Addressing
	MOV EBX, OFFSET fibVals
	MOV ESI, [EBP+8]
	SHL ESI, 2
	MOV EAX, [EBX+ESI]
	MOV EDI, [EBP+20] ; int* v3
	MOV [EDI], EAX

	; Example 4: Base + Index * Scale Addressing
	MOV EBX, OFFSET fibVals
	MOV ESI, [EBP+8]
	MOV EAX, [EBX+ESI*4]
	MOV EDI, [EBP+24] ; int* v4
	MOV [EDI], EAX

	; Example 5: Base + Displacement Addressing with ECX
	MOV ECX, [EBP+8]
	SHL ECX, 2
	MOV EAX, [ECX+fibVals]
	MOV EDI, [EBP+28] ; int* v2
	MOV [EDI], EAX

	MOV EAX, 1
@InvalidIndex:
	POP EDI
	POP ESI
	POP EBX
	MOV ESP, EBP
	POP EBP
	RET
memoryAddressing ENDP
END