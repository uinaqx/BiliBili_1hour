cpu 8086
bits 16
org 100h
mov al, 20
mov bl, 15
mul bl
mov al, -5
mov bl, 3
imul bl

hlt
