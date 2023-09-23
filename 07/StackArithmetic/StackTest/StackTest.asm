// push constant 17 
@17
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 17 
@17
D=A
@SP
AM=M+1
A=A-1
M=D
// eq 
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
D; JEQ
@PUSH_FALSE
D; JNE
(END_CMP_1)
// push constant 17 
@17
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 16 
@16
D=A
@SP
AM=M+1
A=A-1
M=D
// eq 
@END_CMP_2
D=A
@R14
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE
D; JEQ
@PUSH_FALSE
D; JNE
(END_CMP_2)
// push constant 16 
@16
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 17 
@17
D=A
@SP
AM=M+1
A=A-1
M=D
// eq 
@END_CMP_3
D=A
@R14
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE
D; JEQ
@PUSH_FALSE
D; JNE
(END_CMP_3)
// push constant 892 
@892
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 891 
@891
D=A
@SP
AM=M+1
A=A-1
M=D
// lt 
@END_CMP_4
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
(END_CMP_4)
// push constant 891 
@891
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 892 
@892
D=A
@SP
AM=M+1
A=A-1
M=D
// lt 
@END_CMP_5
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
(END_CMP_5)
// push constant 891 
@891
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 891 
@891
D=A
@SP
AM=M+1
A=A-1
M=D
// lt 
@END_CMP_6
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
(END_CMP_6)
// push constant 32767 
@32767
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 32766 
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
// gt 
@END_CMP_7
D=A
@R14
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE
D; JGT
@PUSH_FALSE
D; JLE
(END_CMP_7)
// push constant 32766 
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 32767 
@32767
D=A
@SP
AM=M+1
A=A-1
M=D
// gt 
@END_CMP_8
D=A
@R14
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE
D; JGT
@PUSH_FALSE
D; JLE
(END_CMP_8)
// push constant 32766 
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 32766 
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
// gt 
@END_CMP_9
D=A
@R14
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@PUSH_TRUE
D; JGT
@PUSH_FALSE
D; JLE
(END_CMP_9)
// push constant 57 
@57
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 31 
@31
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 53 
@53
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
// push constant 112 
@112
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
// neg 
@SP
A=M-1
M=-M
// and 
@SP
AM=M-1
D=M
A=A-1
M=D&M
// push constant 82 
@82
D=A
@SP
AM=M+1
A=A-1
M=D
// or 
@SP
AM=M-1
D=M
A=A-1
M=D|M
// not 
@SP
A=M-1
M=!M
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
