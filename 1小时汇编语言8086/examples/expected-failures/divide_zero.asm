cpu 8086
bits 16
org 100h
mov ax, 12
mov bl, 0
div bl

hlt
