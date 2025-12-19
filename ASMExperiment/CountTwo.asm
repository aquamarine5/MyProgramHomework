.386
.model flat, c
.code
; int CountTwo(const wchar_t* s, wchar_t c1, wchar_t c2);
CountTwo PROC
	PUSH EBP
	MOV EBP, ESP
	PUSH ESI
	PUSH EBX

	XOR EBX, EBX		

	MOV ESI, [EBP+8]
	MOV CX, [EBP+12]
	MOV DX, [EBP+16]

@Loop:
	LODSW
	OR AX, AX
	JZ @Done

	CMP AX, CX
	JE @Match

	CMP AX, DX
	JNE @Loop

@Match:
	INC EBX	
	JMP @Loop

@Done:
	MOV EAX, EBX

	POP EBX
	POP ESI
	POP EBP
	RET
	
CountTwo ENDP
END