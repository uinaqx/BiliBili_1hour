bits 64
default rel
org 0x100000
mov rax, -1
cmp rax, 1
seta cl
setl dl
ret
