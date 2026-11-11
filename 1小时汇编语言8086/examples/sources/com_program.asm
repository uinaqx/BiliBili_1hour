cpu 8086
bits 16
org 100h
push cs
pop ds
mov dx, msg
mov ah, 09h
int 21h
mov ax, 4C00h
int 21h
msg: db 'OK$'
