cpu 8086
bits 16
org 100h
mov ax, 5
cmp ax, 5
je same
mov bx, 0
jmp done
same: mov bx, 1
done: nop

hlt
