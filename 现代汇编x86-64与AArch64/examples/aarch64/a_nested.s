.text
stp x29, x30, [sp, #-16]!
mov x29, sp
mov x0, #7
mov x1, #5
bl add_two
ldp x29, x30, [sp], #16
ret
add_two: add x0, x0, x1
ret
