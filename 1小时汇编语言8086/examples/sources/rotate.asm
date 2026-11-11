cpu 8086
bits 16
org 100h
mov al, 81h
ror al, 1

hlt
