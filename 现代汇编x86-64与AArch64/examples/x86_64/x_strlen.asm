bits 64
default rel
org 0x100000
xor eax, eax
next: cmp byte [rdi+rax], 0
je done
inc rax
jmp next
done: ret
