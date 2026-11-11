bits 64
default rel
org 0x100000
mov eax, [rdi]
add eax, 1
mov [rdi+4], eax
ret
