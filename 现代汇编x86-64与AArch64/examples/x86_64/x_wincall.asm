bits 64
default rel
org 0x100000
sub rsp, 40
mov ecx, 7
mov edx, 5
call add_two
add rsp, 40
ret
add_two: lea rax, [rcx+rdx]
ret
