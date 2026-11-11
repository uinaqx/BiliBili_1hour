cpu 8086
bits 16
org 100h
stc
mov al, 0FFh
inc al
mov ax, 0FFFFh
mov dx, 0
add ax, 1
adc dx, 0

hlt
