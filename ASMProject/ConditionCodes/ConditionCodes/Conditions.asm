
.model flat,c
.code


; Find min()

SignedMinA	proc
		   push ebp
		   mov  ebp,esp

		   mov eax,[ebp+8]		;eax='a'
		   mov ecx,[ebp+12]     ;ecx ='b'

		   cmp eax,ecx
		   jle @F               ; jump forward to nearest @@ if less than or equal to
		   mov eax, ecx    ; eax = min (a,b)

@@:		mov ecx,[ebp+16]
		cmp eax,ecx
		jle @F
		mov eax,ecx		; eax =min(a,b,c)


@@:		pop ebp
		ret
SignedMinA  endp


;Find max

SignedMaxA  proc
           push ebp
		   mov  ebp,esp

		   mov eax,[ebp+8]		;eax='a'
		   mov ecx,[ebp+12]     ;ecx ='b'

		   cmp eax,ecx
		   jge  @F              ; jump forward to nearest @@ label if greater than or equal to
		   mov eax, ecx				; eax = max(a,b)


@@:     mov ecx,[ebp+16]
	   cmp eax,ecx
	   jge @F
	   mov eax, ecx			;eax = max(a,b,c)


@@: 	pop ebp
	    ret
SignedMaxA		endp

;Find min()

SignedMinB   proc
		push ebp
		mov ebp,esp
		mov eax,[ebp+8]		; eax ='a'
		mov ecx,[ebp+12]    ; ecx ='b'

		cmp eax,ecx
		cmovg  eax,ecx			; eax = min(a,b) ,use cmova for unsigned integers
		mov ecx,[ebp+16]
		cmp eax,ecx
		cmovg eax,ecx			; eax = min(a,b,c)

		pop ebp
		ret
SignedMinB	endp

;Find max()

SignedMaxB	proc
		push ebp
		mov ebp,esp
		mov eax,[ebp+8]
		mov ecx,[ebp+12]

		cmp eax,ecx
		cmovl eax,ecx    ;      eax = max(a,b) unsigned version of cmovl = cmovb  
		mov ecx,[ebp+16]
		cmp eax, ecx
		cmovl eax, ecx		  ;eax = max(a,b,c)

	    pop ebp
		ret
SignedMaxB endp
	  	end



