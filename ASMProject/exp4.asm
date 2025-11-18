INCLUDE io32.inc
INCLUDELIB io32.lib
.data
	buffer1 DWORD 1214
	buffer2 DWORD 1215
	buf DWORD 1214h, 1215h
	result DWORD ?
	string DB "How are # you ?",13,10,0
.code

Subtract PROC
	MOV EAX, buffer1
	SUB EAX, buffer2
	MOV EDX, 0
	SBB EDX, EDX
	RET
Subtract ENDP

LogicalLeftShift3Digits PROC
	MOV DX, 1214h
	MOV AX, 7777h
	SHL EAX, 16
	MOV AX, DX
	; SHL EAX, 3
	RET
LogicalLeftShift3Digits ENDP

ExecuteTheCode PROC
	MOV AX, 1Fh
	AND AX, AX
	OR AX, AX
	XOR AX, AX
	NOT AX
	TEST AX, 0Fh
	RET
ExecuteTheCode ENDP

StringReplacePoundToWhitespace PROC
	LEA EDI, string
	MOV EBX, LENGTHOF string
	MOV ECX, 0
@ScanLoop:
	CMP BYTE PTR [EDI], '#'
	JNE @ScanLoopItor
	MOV BYTE PTR [EDI], ' '
@ScanLoopItor:
	INC EDI
	INC ECX
	CMP ECX, EBX
	JB @ScanLoop

	MOV EAX, OFFSET string
	CALL dispmsg
	RET
StringReplacePoundToWhitespace ENDP

SumIfEqualSignAndSubtractOtherwise PROC
	MOV EAX, [buf]
	MOV EDX, [buf+4]
	XOR EDX, EAX
	JNS @IsEqual
	MOV EAX, [buf]
	ADD EAX, [buf+4]
	JMP @Result
@IsEqual:
	MOV EAX, [buf]
	SUB EAX, [buf+4]
@Result:
	MOV result, EAX
	RET
SumIfEqualSignAndSubtractOtherwise ENDP

END