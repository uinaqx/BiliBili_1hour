cpu 8086
bits 16
org 100h
cld
mov si, 0200h
mov di, 0300h
mov cx, 3
rep movsb

hlt

times 512 - ($ - $$ + 100h) db 0
db 65,66,67
