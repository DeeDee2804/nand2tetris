// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@prev
M=0
@cur
M=0
@8192
D=A
@SCREEN
D=D+A
@endscreen
M=D
(MAIN)
@KBD
D=M
@PRESSED
D; JNE
@NOTPRESSED
D; JEQ
    (PRESSED)
    @cur
    M=-1
    @COMPARE
    0; JMP
    (NOTPRESSED)
    @cur
    M=0
    @COMPARE
    0; JMP
(COMPARE)
@cur
D=M
@prev
D=D-M
@CHANGE
D; JNE
@MAIN
D; JEQ
    (CHANGE)
    @SCREEN
    D=A
    @addr
    M=D
    @cur
    D=M
    @prev
    M=D
        (LOOP)
        @addr
        D=M
        @endscreen
        D=D-M
        @MAIN
        D; JEQ

        @cur
        D=M
        @addr
        A=M
        M=D
        @addr
        M=M+1
        @LOOP
        0; JMP


        


