_PRINTF = 127
_GETCHAR = 117
_EXIT = 1

.SECT .TEXT
main:	
    
    !input n
    PUSH _GETCHAR
    SYS
    SUBB AL, 0x30
    MOVB (n), AL

    !FINE INPUT


    PUSH v1
    PUSH v2
    PUSH v2 - v1
    CALL fun

    PUSH v2
    PUSH v2 - v1
    CALL print


    PUSH 0
    PUSH _EXIT
    SYS		

fun:
    PUSH BP
    MOV BP, SP
    
    MOV BX, 0
    MOV DI, 8(BP) !v1
    MOV SI, 6(BP) !v2
    MOV CX, 4(BP) !size

    ciclo:
        ! v_1[i] > n
        XOR AX, AX
        MOVB AL, (BX)(DI)
        MOVB AH, (n)

        CMPB AL, AH
        JLE elseif

        XOR AX, AX
        XOR DX, DX

        MOVB AL, (n)
        MOVB DL, 5
        DIVB DL

        MOVB AL, AH
        MOVB AH, 0

        MULB (BX)(DI)

        MOVB (BX)(SI), AL

        JMP end


        elseif:

        ! v_1[i] + v_2[i] > dim + n
        XOR AX, AX
        MOVB AL, (BX)(DI)
        ADDB AL, (BX)(SI)

        MOVB AH, 4(BP)
        ADDB AH, (n)

        CMPB AL, AH
        JLE else

        XOR AX, AX
        XOR DX, DX

        MOVB AL, (n)
        MOVB DL, 2

        DIVB DL

        XOR DX, DX

        MOVB DL, AH

        XOR AX, AX
        MOVB AL, (BX)(SI)
        ADDB AL, (BX)(DI)
        SUBB AL, DL

        MOVB (BX)(SI), AL

        JMP end


        else:

        XOR AX, AX
        MOVB AL, (BX)(SI)
        MULB (n)

        XOR DX, DX
        MOVB DL, 3
        DIVB DL

        MOVB (BX)(SI), AH

        JMP end

    end:
        INC BX
        LOOP ciclo

    MOV SP, BP
    POP BP
    RET

print:
    PUSH BP
    MOV BP, SP
    
    MOV BX, 0   
    MOV SI, 6(BP) !v2
    MOV CX, 4(BP) !size

    ciclo_stampa:
    XOR AX, AX
    MOVB AL, (BX)(SI)
    ADDB AL, (n)
    ADDB AL, 4

    PUSH AX
    PUSH s
    PUSH _PRINTF
    SYS


    INC BX
    LOOP ciclo_stampa

    MOV SP, BP
    POP BP
    RET



.SECT .DATA
    v1: .BYTE 2,7,5,6,4,9
    v2: .BYTE 8,9,5,4,6,1
    s: .ASCII "%d \0"


.SECT .BSS
    n: .SPACE 1


    

