cpu 8086
bits 16
org 100h
mov ax, 1234h
add ax, 1
mov bx, ax

hlt
