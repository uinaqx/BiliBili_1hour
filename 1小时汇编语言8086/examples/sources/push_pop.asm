cpu 8086
bits 16
org 100h
mov sp, 0100h
mov ax, 1234h
mov bx, 0ABCDh
push ax
push bx
pop dx
pop cx

hlt
