cpu 8086
bits 16
org 100h
mov ax, 5
mov bx, 0
inc bx
cmp ax, 5
je equal
mov dx, 9
equal: nop

hlt
