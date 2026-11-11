cpu 8086
bits 16
org 100h
mov dx, 0200h
mov ah, 09h
int 21h

hlt

times 512 - ($ - $$ + 100h) db 0
db 72,73,36
