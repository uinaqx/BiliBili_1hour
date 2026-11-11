bits 64
default rel
org 0x100000
mov eax, 0x80000000
shr eax, 1
mov edx, 0x80000000
sar edx, 1
ret
