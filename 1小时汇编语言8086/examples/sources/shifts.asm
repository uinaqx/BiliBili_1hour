cpu 8086
bits 16
org 100h
mov al, 80h
shr al, 1
mov bl, 80h
sar bl, 1

hlt
