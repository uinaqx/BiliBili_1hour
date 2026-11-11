cpu 8086
bits 16
org 100h
mov ax, 4
call plus_one
mov bx, ax
jmp done
plus_one: inc ax
ret
done: nop

hlt
