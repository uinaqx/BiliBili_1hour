cpu 8086
bits 16
org 100h
mov ax, 4
mov bx, 99
call add_three
jmp done
add_three: push bx
mov bx, 3
add ax, bx
pop bx
ret
done: nop

hlt
