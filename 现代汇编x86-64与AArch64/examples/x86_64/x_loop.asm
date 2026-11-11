bits 64
default rel
org 0x100000
xor eax, eax
mov ecx, 3
next: add eax, 2
dec ecx
jnz next
ret
