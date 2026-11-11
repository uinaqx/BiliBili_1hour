cpu 8086
bits 16
org 100h
xor ax, ax
mov cx, 0
jcxz done
again: add ax, 2
loop again
done: nop

hlt
