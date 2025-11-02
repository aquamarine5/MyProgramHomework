.386
.model flat
.data
numbers DD 10,20,30,40,50
sum DD ?

.code
array_code PROC
	MOV EAX, [numbers]
	MOV EBX, [numbers+4]
	MOV ECX, [numbers+8]
	
	; Q: Why is the offset +4 and +8 instead of +1 and +2?
	; A: Each DWORD (DD, 32-bit integer) occupies 4 bytes in memory.
	RET
array_code ENDP

array_code_by_esi PROC
	MOV ESI, 0
	MOV EAX, [numbers + ESI]
	ADD ESI, 4
	MOV EBX, [numbers + ESI]
	ADD ESI, 4
	MOV ECX, [numbers + ESI]

	; Q: What happens if you replace ADD ESI, 4 with ADD ESI, 12?
	; A: It will skip two elements and read the fourth element directly.

	; Q: Explain what data will be loaded and why?
	; A: EAX will load 10 (numbers[0]), EBX will load 20 (numbers[1]), 
	;    and ECX will load 30 (numbers[2]).
	RET
array_code_by_esi ENDP

array_sum PROC
	MOV ESI, 0
	XOR EAX, EAX
	@Loop:
		ADD EAX, [numbers + ESI]
		ADD ESI, 4
		CMP ESI, 20
		JL @Loop
	MOV [sum], EAX

	; Q: What addressing mode is used here?
	; A: Base plus index addressing mode.

	; Q: Why do we multiply index by 4 in 32-bit arrays?
	; A: Because each element is 4 bytes (32 bits) in size.
	RET
array_sum ENDP
END array_sum