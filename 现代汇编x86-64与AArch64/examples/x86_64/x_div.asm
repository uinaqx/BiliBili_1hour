bits 64
default rel
org 0x100000
mov rax, -17
cqo
mov ecx, 5
idiv rcx
ret
