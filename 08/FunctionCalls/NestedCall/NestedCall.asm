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
// function sys.init 0 
(sys.init)
// push constant 4000 
@4000
D=A
@SP
AM=M+1
A=A-1
M=D
// pop pointer 0 
@SP
AM=M-1
D=M
@THIS
M=D
// push constant 5000 
@5000
D=A
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
// call sys.main 0 
@sys.main$ret.0
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
@sys.main
0; JMP
(sys.main$ret.0)
// pop temp 1 
@SP
AM=M-1
D=M
@6
M=D
// label loop 
(sys.init$loop)
// goto loop 
@sys.init$loop
0; JMP
// function sys.main 5 
(sys.main)
@SP
A=M
M=0
@SP
AM=M+1
M=0
@SP
AM=M+1
M=0
@SP
AM=M+1
M=0
@SP
AM=M+1
M=0
@SP
AM=M+1
// push constant 4001 
@4001
D=A
@SP
AM=M+1
A=A-1
M=D
// pop pointer 0 
@SP
AM=M-1
D=M
@THIS
M=D
// push constant 5001 
@5001
D=A
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
// push constant 200 
@200
D=A
@SP
AM=M+1
A=A-1
M=D
// pop local 1 
@1
D=A
@LCL
D=D+M
@SP
AM=M-1
D=D+M
A=D-M
M=D-A
// push constant 40 
@40
D=A
@SP
AM=M+1
A=A-1
M=D
// pop local 2 
@2
D=A
@LCL
D=D+M
@SP
AM=M-1
D=D+M
A=D-M
M=D-A
// push constant 6 
@6
D=A
@SP
AM=M+1
A=A-1
M=D
// pop local 3 
@3
D=A
@LCL
D=D+M
@SP
AM=M-1
D=D+M
A=D-M
M=D-A
// push constant 123 
@123
D=A
@SP
AM=M+1
A=A-1
M=D
// call sys.add12 1 
@sys.add12$ret.0
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
@sys.add12
0; JMP
(sys.add12$ret.0)
// pop temp 0 
@SP
AM=M-1
D=M
@5
M=D
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
// push local 2 
@2
D=A
@LCL
A=D+M
D=M
@SP
AM=M+1
A=A-1
M=D
// push local 3 
@3
D=A
@LCL
A=D+M
D=M
@SP
AM=M+1
A=A-1
M=D
// push local 4 
@4
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
// add 
@SP
AM=M-1
D=M
A=A-1
M=D+M
// add 
@SP
AM=M-1
D=M
A=A-1
M=D+M
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
// function sys.add12 0 
(sys.add12)
// push constant 4002 
@4002
D=A
@SP
AM=M+1
A=A-1
M=D
// pop pointer 0 
@SP
AM=M-1
D=M
@THIS
M=D
// push constant 5002 
@5002
D=A
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
// push constant 12 
@12
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
