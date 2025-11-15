INCLUDE io32.inc
INCLUDELIB io32.lib

.data
	vard WORD 4000h
	H8843 DWORD 8843h
	varB DB 1,2,3,4,0
	varW DB 5,6,7,8,90
	var_a DWORD 4321h
	var_b DWORD 0011h
	str_s DB 'abcdefg',13,10,0
.code
exp2_1 PROC
	MOV EAX, 2222h
	MOV EBX, EAX
	SUB EAX, EBX
	MOV EAX, var_a
	MOV EBX, var_b
	SUB EAX, EBX
	MOV var_a, EAX
	MOV EAX, 0
	MOV EAX, OFFSET str_s
	CALL dispmsg
	RET
exp2_1 ENDP

exp2_2 PROC
	mov esi,1h
	mov ebx,OFFSET vard
	mov edi,4h
	mov edx,[ebx]
	mov edx,[ebx+4h]
	MOVZX edx,vard[edi]
	mov edx,[ebx+edi]
	mov edx,[ebx+edi+4h]
	MOVZX edx, vard[edi+esi]
	mov edx, [ebx+esi*4]
	MOVZX ecx, WORD PTR H8843
	RET
exp2_2 ENDP
END