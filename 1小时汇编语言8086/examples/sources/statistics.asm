cpu 8086
bits 16
org 100h
xor dx, dx
xor bx, bx
mov si, 0200h
mov cx, 3
next: mov al, [si]
xor ah, ah
add dx, ax
cmp al, bl
jbe keep
mov bl, al
keep: inc si
loop next

hlt

times 512 - ($ - $$ + 100h) db 0
db 3,5,7
