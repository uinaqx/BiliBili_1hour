cpu 8086
bits 16
org 100h
mov ax, 1000
mov bl, 30
div bl

hlt
