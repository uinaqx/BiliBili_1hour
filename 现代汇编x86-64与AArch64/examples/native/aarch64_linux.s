.arch armv8-a
.text
.global add_two
.type add_two, %function
add_two:
    add x0, x0, x1
    ret
.size add_two, .-add_two
.section .note.GNU-stack,"",%progbits
