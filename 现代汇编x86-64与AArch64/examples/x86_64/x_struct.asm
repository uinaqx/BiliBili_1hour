bits 64
default rel
org 0x100000
mov eax, [rdi]
movzx edx, byte [rdi+4]
ret
