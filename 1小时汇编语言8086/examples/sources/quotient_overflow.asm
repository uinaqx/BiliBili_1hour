cpu 8086
bits 16
org 100h
mov ax, 256
mov bl, 1
div bl

hlt
