_EXIT = 1
_WRITE = 4
_STDOUT = 1
_PRINTF = 127

.SECT .TEXT
start:
    MOV CX, de-hw
    PUSH CX
    PUSH hw
    PUSH _STDOUT
    PUSH _WRITE
    SYS
    MOV AX, 0x8
    OR AX, 0x4
    PUSH AX
    PUSH format
    PUSH _PRINTF
    SYS
    PUSH 69
    PUSH _EXIT
    SYS
.SECT .DATA
hw: .ASCII "Hello world!\n"
de: .BYTE 0
format: .ASCII "val %d"
b: .BYTE 0b101
h: .BYTE 0xDDAAFF, 0xAABBFF, 0xFFFFCC
o: .BYTE 07
d: .BYTE 257

.SECT .BSS
inprod: .SPACE 2