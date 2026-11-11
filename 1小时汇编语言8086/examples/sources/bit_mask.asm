cpu 8086
bits 16
org 100h
mov al, 0ABh
and al, 0Fh
or al, 80h
xor al, 1

hlt
