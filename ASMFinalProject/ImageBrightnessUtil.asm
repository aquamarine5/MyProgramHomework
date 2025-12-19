.686
.model flat, c
.mmx
.code

; void MmxIncreaseBrightness(unsigned char* img, int count, int brightness)
MmxIncreaseBrightness PROC
    push ebp
    mov ebp, esp
    push esi
    
    mov esi, [ebp + 8]      ; img pointer
    mov ecx, [ebp + 12]     ; count
    mov eax, [ebp + 16]     ; brightness value
    
    ; Prepare brightness mask in MM7
    movd mm7, eax           ; Load brightness into low 32 bits
    punpcklbw mm7, mm7      ; Interleave bytes: B3 B2 B1 B0 -> B3 B3 B2 B2 B1 B1 B0 B0
    punpcklwd mm7, mm7      ; Interleave words: W1 W1 W0 W0 -> B1 B1 B1 B1 B0 B0 B0 B0
    punpckldq mm7, mm7      ; Interleave dwords: D0 D0 -> B0...B0 (8 times)
    
    ; Calculate remainder and loop count
    mov edx, ecx            ; copy count to edx
    and edx, 7              ; edx = count % 8 (remainder)
    shr ecx, 3              ; ecx = count / 8
    
    cmp ecx, 0
    jle @CheckTail
    
@ProcessLoop:
    movq mm0, [esi]         ; Load 8 pixels
    paddusb mm0, mm7        ; Add brightness with saturation
    movq [esi], mm0         ; Store result
    
    add esi, 8              ; Move to next 8 pixels
    dec ecx
    jnz @ProcessLoop

@CheckTail:
    cmp edx, 0
    jle @Done
    
@TailLoop:
    mov al, [esi]           ; Load pixel
    add al, byte ptr [ebp + 16] ; Add brightness
    jnc @NoSat
    mov al, 255             ; Saturate
@NoSat:
    mov [esi], al           ; Store pixel
    inc esi
    dec edx
    jnz @TailLoop
    
@Done:
    emms                    ; Clear MMX state
    pop esi
    pop ebp
    ret
MmxIncreaseBrightness ENDP

END
