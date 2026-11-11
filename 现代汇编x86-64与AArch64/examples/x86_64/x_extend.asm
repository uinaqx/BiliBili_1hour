bits 64
default rel
org 0x100000
movzx eax, byte [rdi]
movsx rdx, byte [rdi]
ret
