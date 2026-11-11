cpu 8086
bits 16
org 100h
call print_u16
jmp done
print_u16:
push ax
push bx
push cx
push dx
xor cx, cx
mov bx, 10
.digits:
xor dx, dx
div bx
push dx
inc cx
test ax, ax
jnz .digits
.output:
pop dx
add dl, '0'
mov ah, 02h
int 21h
loop .output
pop dx
pop cx
pop bx
pop ax
ret
done: hlt
