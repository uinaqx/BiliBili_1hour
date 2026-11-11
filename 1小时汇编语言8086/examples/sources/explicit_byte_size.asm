cpu 8086
bits 16
org 100h
mov byte [0200h], 1
mov ax, [0200h]

hlt

times 512 - ($ - $$ + 100h) db 0
db 205,171
