.text
mov x2, #0
cbz x1, done
next: ldr w3, [x0], #4
add x2, x2, x3
subs x1, x1, #1
b.ne next
done: mov x0, x2
ret
