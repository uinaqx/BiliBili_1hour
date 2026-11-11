cpu 8086
bits 16
org 100h
mov ax, 7
mov bx, 12
cmp ax, bx
jae done
mov ax, bx
done: nop

hlt
