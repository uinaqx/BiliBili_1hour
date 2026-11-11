cpu 8086
bits 16
org 100h
mov al, 5
add al, '0'
mov bl, al
sub bl, '0'

hlt
