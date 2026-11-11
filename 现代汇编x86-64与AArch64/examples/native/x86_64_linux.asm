bits 64
default rel
section .text
global add_two
add_two:
    lea rax, [rdi+rsi]
    ret
section .note.GNU-stack noalloc noexec nowrite progbits
