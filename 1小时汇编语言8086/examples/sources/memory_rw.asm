cpu 8086
bits 16
org 100h
mov bx, 0200h
mov ax, [bx]
mov [0202h], ax

hlt

times 512 - ($ - $$ + 100h) db 0
db 52,18,0,0
