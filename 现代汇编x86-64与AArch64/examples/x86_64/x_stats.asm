bits 64
default rel
org 0x100000
xor eax, eax
xor edx, edx
test rsi, rsi
jz done
next: mov ecx, [rdi]
add rax, rcx
cmp rcx, rdx
cmova rdx, rcx
add rdi, 4
dec rsi
jnz next
done: ret
