// Bootstrap init 
@256
D=A
@SP
M=D
// Call Sys.init 
@sys.init$ret.0
D=A
@SP
A=M
M=D
@LCL
D=M
@SP
AM=M+1
M=D
@ARG
D=M
@SP
AM=M+1
M=D
@THIS
D=M
@SP
AM=M+1
M=D
@THAT
D=M
@SP
AM=M+1
M=D
@4
D=A
@SP
D=M-D
@ARG
M=D
@SP
MD=M+1
@LCL
M=D
@sys.init
0; JMP
(sys.init$ret.0)
// function main.fibonacci 0 
(main.fibonacci)
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
// push constant 2 
@2
D=A
@SP
AM=M+1
A=A-1
M=D
// lt 
@END_CMP_1
D=A
@R14
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE
D; JLT
@PUSH_FALSE
D; JGE
(END_CMP_1)
// if-goto if_true 
@SP
AM=M-1
D=M
@main.fibonacci$if_true
D; JNE
// goto if_false 
@main.fibonacci$if_false
0; JMP
// label if_true 
(main.fibonacci$if_true)
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
// label if_false 
(main.fibonacci$if_false)
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
// push constant 2 
@2
D=A
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
// call main.fibonacci 1 
@main.fibonacci$ret.0
D=A
@SP
A=M
M=D
@LCL
D=M
@SP
AM=M+1
M=D
@ARG
D=M
@SP
AM=M+1
M=D
@THIS
D=M
@SP
AM=M+1
M=D
@THAT
D=M
@SP
AM=M+1
M=D
@5
D=A
@SP
D=M-D
@ARG
M=D
@SP
MD=M+1
@LCL
M=D
@main.fibonacci
0; JMP
(main.fibonacci$ret.0)
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
// push constant 1 
@1
D=A
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
// call main.fibonacci 1 
@main.fibonacci$ret.1
D=A
@SP
A=M
M=D
@LCL
D=M
@SP
AM=M+1
M=D
@ARG
D=M
@SP
AM=M+1
M=D
@THIS
D=M
@SP
AM=M+1
M=D
@THAT
D=M
@SP
AM=M+1
M=D
@5
D=A
@SP
D=M-D
@ARG
M=D
@SP
MD=M+1
@LCL
M=D
@main.fibonacci
0; JMP
(main.fibonacci$ret.1)
// add 
@SP
AM=M-1
D=M
A=A-1
M=D+M
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
// function sys.init 0 
(sys.init)
// push constant 4 
@4
D=A
@SP
AM=M+1
A=A-1
M=D
// call main.fibonacci 1 
@main.fibonacci$ret.2
D=A
@SP
A=M
M=D
@LCL
D=M
@SP
AM=M+1
M=D
@ARG
D=M
@SP
AM=M+1
M=D
@THIS
D=M
@SP
AM=M+1
M=D
@THAT
D=M
@SP
AM=M+1
M=D
@5
D=A
@SP
D=M-D
@ARG
M=D
@SP
MD=M+1
@LCL
M=D
@main.fibonacci
0; JMP
(main.fibonacci$ret.2)
// label while 
(sys.init$while)
// goto while 
@sys.init$while
0; JMP
@END_PROG
0; JMP
(PUSH_FALSE)
@SP
A=M-1
M=0
@R14
A=M
0; JMP
(PUSH_TRUE)
@SP
A=M-1
M=-1
@R14
A=M
0; JMP
(END_PROG)
