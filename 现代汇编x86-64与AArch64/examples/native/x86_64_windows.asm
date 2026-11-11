bits 64
default rel
section .text
global add_two
add_two:
    lea rax, [rcx+rdx]
    ret
