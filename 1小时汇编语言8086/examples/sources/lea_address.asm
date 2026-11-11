cpu 8086
bits 16
org 100h
mov bx, 0200h
mov si, 4
lea dx, [bx+si+2]
mov ax, [bx+si+2]

hlt

times 518 - ($ - $$ + 100h) db 0
db 120,86
