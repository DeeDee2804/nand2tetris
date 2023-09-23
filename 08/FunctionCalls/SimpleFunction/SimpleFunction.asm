// function simplefunction.test 2 
(simplefunction.test)
@SP
A=M
M=0
@SP
AM=M+1
M=0
@SP
AM=M+1
// push local 0 
@0
D=A
@LCL
A=D+M
D=M
@SP
AM=M+1
A=A-1
M=D
// push local 1 
@1
D=A
@LCL
A=D+M
D=M
@SP
AM=M+1
A=A-1
M=D
// add 
@SP
AM=M-1
D=M
A=A-1
M=D+M
// not 
@SP
A=M-1
M=!M
// push argument 0 
@0
D=A
@ARG
A=D+M
D=M
@SP
AM=M+1
A=A-1
M=D
// add 
@SP
AM=M-1
D=M
A=A-1
M=D+M
// push argument 1 
@1
D=A
@ARG
A=D+M
D=M
@SP
AM=M+1
A=A-1
M=D
// sub 
@SP
AM=M-1
D=M
A=A-1
M=M-D
// return 
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D
@SP
A=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@R13
AM=M-1
D=M
@THAT
M=D
@R13
AM=M-1
D=M
@THIS
M=D
@R13
AM=M-1
D=M
@ARG
M=D
@R13
AM=M-1
D=M
@LCL
M=D
@R14
A=M
0; JMP
