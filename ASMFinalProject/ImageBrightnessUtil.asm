.686
.XMM
.model flat, c
.code

; void MmxIncreaseBrightness(unsigned char* data, int n, unsigned char amount);
MmxIncreaseBrightness PROC C USES esi edi ebx, \
    pData:PTR BYTE, \
    n:DWORD, \
    amount:BYTE

    mov esi, pData      ; ESI = &data[0]
    mov ecx, n          ; ECX = n
    
    test ecx, ecx
    jle mmx_done        ; if n <= 0, nothing to do

    ; Build MMX register mm0 with 8 copies of 'amount'
    movzx eax, amount   ; EAX = amount (0..255)
    
    ; ====== 构建亮度掩码 ======
    ; 将amount值复制到8个字节中
    mov  ah, al          ; ax = amount amount
    mov  bx, ax          ; bx = amount amount
    shl  eax, 16         ; eax高16位 = amount amount
    mov  ax, bx          ; eax = amount amount amount amount
    
    ; 使用栈代替全局变量
    push eax             ; 压入高32位
    push eax             ; 压入低32位
    movq mm7, QWORD PTR [esp] ; 从栈加载8个字节到mm7
    add esp, 8           ; 恢复栈平衡

mmx_loop:
    cmp ecx, 8
    jl mmx_tail        ; if less than 8 pixels left, go to tail

    ; Load 8 pixels into mm1
    movq mm1, QWORD PTR [esi]

    ; Perform saturated add: pixels += amount
    paddusb mm1, mm7

    ; Store back
    movq QWORD PTR [esi], mm1

    add esi, 8          ; advance pointer to next 8 pixels
    sub ecx, 8          ; processed 8 pixels
    jmp mmx_loop

mmx_tail:
    test ecx, ecx
    jz mmx_done
    
    mov dl, amount      ; Load amount into DL for scalar loop

tail_loop_start:
    mov al, [esi]       ; Load byte
    add al, dl          ; Add amount
    jnc store_val       ; If no carry, value is correct (<= 255)
    mov al, 255         ; If carry, saturate to 255
store_val:
    mov [esi], al       ; Store back
    inc esi
    dec ecx
    jnz tail_loop_start

mmx_done:
    emms                    ; clear MMX state
    ret

MmxIncreaseBrightness ENDP
END
