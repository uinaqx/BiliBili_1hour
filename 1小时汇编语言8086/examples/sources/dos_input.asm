cpu 8086
bits 16
org 100h
mov ah, 01h
int 21h
cmp al, '0'
jb bad
cmp al, '9'
ja bad
sub al, '0'
mov bl, al
jmp done
bad: mov bl, 0FFh
done: nop

hlt
