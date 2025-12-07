INCLUDE io32.inc
INCLUDELIB io32.lib

.data
	pattern DB "BUG"
	string DB "Fix a Bug, and birth more BxUxGs."
	success DB "Y",0
	failure DB "N",0
	result DB 100 DUP(?)
.code
FindStringContainPattern PROC
	XOR EAX, EAX
	XOR EBX, EBX
	MOV EDX, LENGTHOF string
	LEA ESI, string
	LEA EDI, pattern
@CheckingLoop:
	CMP EAX, EDX
	JAE @Failure
	CMP EBX, 3
	JAE @Success
	MOV EBP, EAX
	ADD EBP, EBX
	MOV CH, [ESI+EBP]
	MOV CL, [EDI+EBX]
	CMP CH, CL
	JNE @Mismatch
	INC EBX
	JMP @CheckingLoop
@Mismatch:
	INC EAX
	MOV EBX, 0
	JMP @CheckingLoop

@Success:
	LEA EAX, success
	CALL dispmsg
	JMP @Return
@Failure:
	LEA EAX, failure
	CALL dispmsg
@Return:
	RET
FindStringContainPattern ENDP

EraseAllWhitespace PROC
	XOR EAX, EAX
	XOR EBX, EBX
	MOV EDX, LENGTHOF string
	LEA ESI, string
@CheckingLoop:
	CMP EAX, EDX
	JAE @Return
	MOV CL, [ESI+EAX]
	INC EAX
	CMP CL, ' '
	JE @CheckingLoop
	LEA EDI, [result+EBX]
	MOV [EDI], CL
	INC EBX
	JMP @CheckingLoop

@Return:
	LEA EAX, result
	CALL dispmsg
	RET
EraseAllWhitespace ENDP

END 