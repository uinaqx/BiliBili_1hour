.text
mov x2, #0
mov x3, #0
cbz x1, done
next: ldr w4, [x0], #4
add x2, x2, x4
cmp x4, x3
csel x3, x4, x3, hi
subs x1, x1, #1
b.ne next
done: mov x0, x2
mov x1, x3
ret
