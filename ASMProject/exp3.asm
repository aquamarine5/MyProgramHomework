INCLUDE io32.inc
INCLUDELIB io32.lib

.data
    string DB "ABCDEFGH"
    var_a DW 0BD61h, 0FF46h
    var_b DW 2 DUP(?)

.code
PrintAllCharacters PROC
    MOV AX, 'A'
    MOV CX, 26
    @Loop:
        CALL dispc
        INC AX
        DEC CX
        JNZ @Loop
    RET
PrintAllCharacters ENDP

DataStringToLowerCase PROC
    LEA ESI, string
    MOV ECX, LENGTHOF string
    LEA EDI, [string + ECX]
    XOR EBX, EBX
    @ConvertLoop:
        MOV AL, [ESI]
        ADD AL, 20h
        MOV [EDI], AL
        INC ESI
        INC EDI
        DEC ECX
        JNZ @ConvertLoop

    LEA EAX, string
    CALL dispmsg
    RET
DataStringToLowerCase ENDP

CalculateAbsNumber PROC
    MOV AX, [var_a]
    MOV BX, [var_a+2]
    TEST BX, 8000h
    JZ @IsPositive
    NEG BX
    NEG AX
    SBB BX, 0

@IsPositive:
    MOV [var_b], AX
    MOV [var_b+2], BX
    SHL EBX, 16
    MOV BX, AX
    MOV EAX, EBX
    CALL dispuid
    RET

CalculateAbsNumber ENDP

ExecuteTheCodeExp3 PROC
    MOV CL, 04
    SHL DX, CL
    MOV BL, AH
    SHL AX, CL
    SHR BL, CL
    OR DL, BL
    SHL EAX, 4
    RET
ExecuteTheCodeExp3 ENDP

END