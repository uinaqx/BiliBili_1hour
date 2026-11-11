.text
mov x0, #0
mov x1, #3
next: add x0, x0, #2
subs x1, x1, #1
b.ne next
ret
