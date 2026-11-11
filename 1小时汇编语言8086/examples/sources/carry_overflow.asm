cpu 8086
bits 16
org 100h
mov al, 0FFh
add al, 1
mov al, 7Fh
add al, 1

hlt
