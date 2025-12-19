.686
.model flat, c
.stack 4096

.data
    val_32    REAL8 32.0
    val_5     REAL8 5.0
    val_9     REAL8 9.0
    val_0     REAL8 0.0

.code

; void CalcStats(double* arr, int count, double* avg, double* min, double* max)
CalcStats PROC
    push ebp
    mov ebp, esp
    push esi
    push edi
    
    mov esi, [ebp + 8]      ; arr
    mov ecx, [ebp + 12]     ; count
    
    cmp ecx, 0
    jle @DoneStats

    ; Load first element
    fld qword ptr [esi]     ; ST(0) = arr[0]
    fld st(0)               ; ST(0) = arr[0] (Min), ST(1) = arr[0]
    fld st(0)               ; ST(0) = arr[0] (Max), ST(1) = Min, ST(2) = arr[0]
    
    ; Stack:
    ; ST(0): Max
    ; ST(1): Min
    ; ST(2): Sum (initially arr[0])
    
    ; Loop setup
    dec ecx                 ; count--
    jz @CalcAvg             ; if count was 1
    add esi, 8              ; next element

@StatsLoop:
    fld qword ptr [esi]     ; Load Val, Stack: Val, Max, Min, Sum
    
    ; Update Sum
    fadd st(3), st(0)       ; Sum += Val, Stack: Val, Max, Min, Sum
    
    ; Update Max
    fcomi st(0), st(1)      ; Compare Val vs Max
    jbe @CheckMin           ; Jump if Val <= Max
    fst st(1)               ; Max = Val
    jmp @NextVal

@CheckMin:
    fcomi st(0), st(2)      ; Compare Val vs Min
    jae @NextVal            ; Jump if Val >= Min
    fst st(2)               ; Min = Val

@NextVal:
    fstp st(0)              ; Pop Val Stack: Max, Min, Sum
    add esi, 8
    dec ecx
    jnz @StatsLoop

@CalcAvg:
    ; Store Max
    mov edi, [ebp + 24]
    fstp qword ptr [edi]    ; Pop Max. Stack: Min, Sum
    
    ; Store Min
    mov edi, [ebp + 20]
    fstp qword ptr [edi]    ; Pop Min. Stack: Sum
    
    ; Calculate Avg
    fild dword ptr [ebp + 12] ; Stack: Count, Sum
    fdivp st(1), st(0)      ; Sum / Count. Stack: Avg
    
    ; Store Avg
    mov edi, [ebp + 16]
    fstp qword ptr [edi]    ; Pop Avg. Stack empty.

@DoneStats:
    pop edi
    pop esi
    mov esp, ebp
    pop ebp
    ret
CalcStats ENDP

; double CelsiusToFahrenheit(double c)
CelsiusToFahrenheit PROC
    push ebp
    mov ebp, esp
    
    fld qword ptr [ebp + 8]
    fld val_9
    fmulp st(1), st(0)      ; C * 9
    fld val_5
    fdivp st(1), st(0)      ; (C * 9) / 5
    fld val_32
    faddp st(1), st(0)      ; + 32
    
    pop ebp
    ret
CelsiusToFahrenheit ENDP

; double FahrenheitToCelsius(double f)
FahrenheitToCelsius PROC
    push ebp
    mov ebp, esp

    fld REAL8 PTR [ebp+8]
    fld val_32
    fsubp st(1), st(0)      ; F - 32
    fld val_5
    fmulp st(1), st(0)      ; (F - 32) * 5
    fld val_9
    fdivp st(1), st(0)      ; ((F - 32) * 5) / 9
    
    pop ebp
    ret
FahrenheitToCelsius ENDP

; double CalculateStandardDeviation(double* arr, int count, double avg)
CalculateStandardDeviation PROC
    push ebp
    mov ebp, esp
    push esi
    
    mov esi, [ebp + 8]      ; arr
    mov ecx, [ebp + 12]     ; count
    
    fld val_0               ; SumSqDiff = 0. Stack: SumSqDiff
    
    cmp ecx, 0
    jle @Done
    
@Loop:
    fld qword ptr [esi]     ; Load Val. Stack: Val, SumSqDiff
    fld qword ptr [ebp + 16]; Load Avg, Stack: Avg, Val, SumSqDiff
    fsubp st(1), st(0)      ; Val - Avg, Stack: Diff, SumSqDiff
    fmul st(0), st(0)       ; Diff^2, Stack: SqDiff, SumSqDiff
    faddp st(1), st(0)      ; SumSqDiff += SqDiff, Stack: SumSqDiff
    
    add esi, 8
    dec ecx
    jnz @Loop
    
    ; Calculate Variance = SumSqDiff / Count
    fild dword ptr [ebp + 12] ; Load Count, Stack: Count, SumSqDiff
    fdivp st(1), st(0)      ; SumSqDiff / Count, Stack: Variance
    fsqrt                   ; Sqrt(Variance)

@Done:
    pop esi
    pop ebp
    ret
CalculateStandardDeviation ENDP

END
