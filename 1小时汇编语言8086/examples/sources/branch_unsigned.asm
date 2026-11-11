cpu 8086
bits 16
org 100h
mov al, 0FFh
cmp al, 1
ja above
mov bx, 0
jmp done
above: mov bx, 1
done: nop

hlt
