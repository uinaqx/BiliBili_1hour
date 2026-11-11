bits 64
default rel
org 0x100000
xor eax, eax
test rsi, rsi
jz done
next: mov ecx, [rdi]
add rax, rcx
add rdi, 4
dec rsi
jnz next
done: ret
