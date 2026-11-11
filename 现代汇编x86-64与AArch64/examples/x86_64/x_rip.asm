bits 64
default rel
org 0x100000
lea rax, [rel here]
here: nop
ret
