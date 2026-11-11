cpu 8086
bits 16
org 100h
mov si, 0200h
mov cx, 3
xor ax, ax
again: add ax, [si]
add si, 2
loop again

hlt

times 512 - ($ - $$ + 100h) db 0
db 100,0,200,0,44,1
