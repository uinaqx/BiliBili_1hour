cpu 8086
bits 16
org 100h
mov ax, 7
push ax
call add_one
add sp, 2
jmp done
add_one: push bp
mov bp, sp
mov ax, [bp+4]
inc ax
pop bp
ret
done: nop

hlt
