_EXIT = 1
_WRITE = 4
_STDOUT = 1

.SECT .TEXT
start:
    MOV CX, de-hw
    PUSH CX
    PUSH hw
    PUSH _STDOUT
    PUSH _WRITE
    SYS
    ADD SP, 8
    SUB CX, AX
    PUSH CX
    PUSH _EXIT
    SYS
.SECT .DATA
hw: .ASCII "Hello world!\n"
de: .BYTE 0

.SECT .BSS
inprod: .SPACE 2