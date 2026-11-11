bits 64
default rel
org 0x100000
sub rsp, 8
mov edi, 7
mov esi, 5
call add_two
add rsp, 8
ret
add_two: lea rax, [rdi+rsi]
ret
