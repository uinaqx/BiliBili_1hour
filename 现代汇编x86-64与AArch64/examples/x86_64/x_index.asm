bits 64
default rel
org 0x100000
lea rax, [rdi+rsi*4+8]
mov ecx, [rax]
ret
