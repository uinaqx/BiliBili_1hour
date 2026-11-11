bits 64
default rel
org 0x100000
mov eax, 7
xor edx, edx
xor ecx, ecx
div rcx
ret
