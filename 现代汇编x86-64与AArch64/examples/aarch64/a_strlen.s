.text
mov x2, #0
next: ldrb w3, [x0, x2]
cbz w3, done
add x2, x2, #1
b next
done: mov x0, x2
ret
