cpu 8086
bits 16
org 100h
mov al, 0FFh
cmp al, 1
jl smaller
mov bx, 0
jmp done
smaller: mov bx, 1
done: nop

hlt
