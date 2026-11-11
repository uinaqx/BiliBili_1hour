bits 64
default rel
org 0x100000
push rbx
mov ebx, 3
lea rax, [rdi+rbx]
pop rbx
ret
