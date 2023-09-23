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
// pop pointer 1 
@SP
AM=M-1
D=M
@THAT
M=D
// push constant 0 
@0
D=A
@SP
AM=M+1
A=A-1
M=D
// pop that 0 
@0
D=A
@THAT
D=D+M
@SP
AM=M-1
D=D+M
A=D-M
M=D-A
// push constant 1 
@1
D=A
@SP
AM=M+1
A=A-1
M=D
// pop that 1 
@1
D=A
@THAT
D=D+M
@SP
AM=M-1
D=D+M
A=D-M
M=D-A
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
// pop argument 0 
@0
D=A
@ARG
D=D+M
@SP
AM=M-1
D=D+M
A=D-M
M=D-A
// label main_loop_start 
(main_loop_start)
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
// if-goto compute_element 
@SP
AM=M-1
D=M
@compute_element
D; JNE
// goto end_program 
@end_program
0; JMP
// label compute_element 
(compute_element)
// push that 0 
@0
D=A
@THAT
A=D+M
D=M
@SP
AM=M+1
A=A-1
M=D
// push that 1 
@1
D=A
@THAT
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
// pop that 2 
@2
D=A
@THAT
D=D+M
@SP
AM=M-1
D=D+M
A=D-M
M=D-A
// push pointer 1 
@THAT
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
// add 
@SP
AM=M-1
D=M
A=A-1
M=D+M
// pop pointer 1 
@SP
AM=M-1
D=M
@THAT
M=D
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
// pop argument 0 
@0
D=A
@ARG
D=D+M
@SP
AM=M-1
D=D+M
A=D-M
M=D-A
// goto main_loop_start 
@main_loop_start
0; JMP
// label end_program 
(end_program)
