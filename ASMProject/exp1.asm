.386
.model flat
.data
	a DWORD 1212h
	b DWORD 0001h
.code
	exp1 PROC
		MOV EAX, 4321h
		MOV EBX, EAX
		ADD EAX, EBX
		MOV a, EAX
		MOV ECX, b
		ADD ECX, a
		MOV EAX, ECX
		MOV b, ECX
		RET
	exp1 ENDP
END 