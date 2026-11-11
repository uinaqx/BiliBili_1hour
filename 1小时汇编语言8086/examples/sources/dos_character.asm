cpu 8086
bits 16
org 100h
mov dl, 'A'
mov ah, 02h
int 21h

hlt
