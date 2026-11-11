cpu 8086
bits 16
org 100h
mov ax, 1234h
mov [0200h], ax
mov bx, [0200h]

hlt
