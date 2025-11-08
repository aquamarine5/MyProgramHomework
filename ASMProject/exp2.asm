
.model flat
.data
vard DW 4000h
H8843 DW 8843h
varB DB 1,2,3,4,0
varW DB 5,6,7,8,90

.code
main PROC
mov si,1h
mov bx,vard
mov di,4h
mov dx,[bx]
mov dx,[bx+4h]
mov dx,vard[di]
mov dx,[bx+di]
mov dx,[bx+di+4h]
mov dx, vard[di+si]
mov dx, [bx+si*4]
mov cx, word ptr H8843
main ENDP
END main