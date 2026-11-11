bits 64
default rel
org 0x100000
mov rax, rdi
cmp rdi, rsi
jge done
mov rax, rsi
done: ret
