cpu 8086
bits 16
org 100h
xor ax, ax
mov cx, 3
again: add ax, 2
loop again

hlt
