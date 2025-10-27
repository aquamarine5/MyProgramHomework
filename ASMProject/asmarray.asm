.386
.model flat
.data
	numbers DWORD 1000h,2000h,3000h,4000h
	intArray SDWORD 0,0,1,3,0,-34,-56,7,8
	STATUS_NOT_FOUND EQU -10000
.code
ASMArraySum PROC
	MOV EDI, OFFSET numbers
	MOV ECX, LENGTHOF numbers
	XOR EAX, EAX

	@@:
		ADD EAX, [EDI]
		ADD EDI, TYPE numbers
		LOOP @B
	RET
ASMArraySum ENDP

ASMArrayScan PROC
	MOV EAX, TYPE numbers
	MOV EBX, LENGTHOF numbers
	MOV ECX, SIZEOF numbers
	MOV EDX, OFFSET numbers
	RET
ASMArrayScan ENDP

ASMArrayFindFirstNonZeroElement PROC
	MOV EBX, OFFSET intArray
	MOV ECX, LENGTHOF intArray
	@@:
		CMP SDWORD PTR [EBX], 0
		JNE @FOUND
		ADD EBX, TYPE intArray
		LOOP @B
		JMP @NOTFOUND
	@FOUND:
		MOV EAX, [EBX]
		RET
	@NOTFOUND:
		MOV EAX, STATUS_NOT_FOUND
		RET
ASMArrayFindFirstNonZeroElement ENDP

ASMArrayFindLargestElement PROC
	MOV EBX, OFFSET intArray
	MOV ECX, LENGTHOF intArray
	MOV EAX, [EBX]
	ADD EBX, TYPE intArray
	DEC ECX
	JZ @RESULT
	@FOREACH:
		CMP EAX, SDWORD PTR [EBX]
		JGE @NOTSWAP
		MOV EAX, [EBX]
		@NOTSWAP:
			ADD EBX, TYPE intArray
			LOOP @FOREACH
	@RESULT:
		RET
ASMArrayFindLargestElement ENDP

ASMArrayCountNonZeroElement PROC
	MOV EBX, OFFSET intArray
	MOV ECX, LENGTHOF intArray
	XOR EAX, EAX
	@FOREACH:
		CMP SDWORD PTR [EBX],0
		JE @ISZERO
		INC EAX
		@ISZERO:
			ADD EBX, TYPE intArray
			LOOP @FOREACH
	RET
ASMArrayCountNonZeroElement ENDP

END ASMArrayFindFirstNonZeroElement