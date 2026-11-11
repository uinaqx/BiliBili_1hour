cpu 8086
bits 16
org 100h
mov si, 0200h
mov cx, 3
xor ax, ax
again: mov bl, [si]
xor bh, bh
add ax, bx
inc si
loop again

hlt

times 512 - ($ - $$ + 100h) db 0
db 3,5,7
