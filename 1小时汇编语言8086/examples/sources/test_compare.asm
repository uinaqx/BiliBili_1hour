cpu 8086
bits 16
org 100h
mov al, 81h
test al, 1
cmp al, 81h

hlt
