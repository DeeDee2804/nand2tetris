from typing import Iterator
from enum import Enum
from pathlib import PurePath
import sys

class VMCommandType(Enum):
    ARITHMETHIC_LOGICAL_CMD = 1
    MEMORY_ACCESS_CMD = 2
    BRANCHING_CMD = 3
    FUNCTION_CMD = 4

class VMCommand():
    
    def __init__(self, operation:str, *args):
        self.origin = " ".join([operation, *args])
        self.operation = operation
        if len(args) == 0:
            self.type = VMCommandType.ARITHMETHIC_LOGICAL_CMD
        else:
            self.type = VMCommandType.MEMORY_ACCESS_CMD
            self.mem_seg = args[0]
            self.position = int(args[1])     

class VMParser():
    
    def __init__(self, filepath: str):
        self.commands = self.read(filepath)

    # Create a generator which yields VMCommand
    def read(self, filepath) -> Iterator["VMCommand"]:
        with open(filepath, 'r') as VMFile:
            for line in VMFile.readlines():
                command = self.parse(line)
                #BUG_FIX: Check command is not None before yield
                if command is None:
                    continue
                else:
                    yield command

    # Parse the VM line of code into VMCommand object
    def parse(self, line:str) -> "VMCommand":
        line = line.strip().lower()
        if line.startswith("//") or line == "": 
            return None
        else:
            fields = line.split(" ")
            return VMCommand(*fields)
        
    # Try to read the next command
    def nextCommand(self) -> "VMCommand":
        try:
            #BUG_FIX: Run next of generator before return
            cmd = next(self.commands)
            return cmd
        except:
            return None

class ASMWriter():
    unary_operator = ["neg", "not"]
    compare_operator = ["lt", "gt", "eq"]
    simple_segment = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
    }
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.module_name =  PurePath(self.filepath).stem
        self.command = None
        self.code = []
        self.count_compare = 0

    def write(self, command: "VMCommand") -> str:
        self.command = command
        self.addComment(command.origin)
        if command.type == VMCommandType.ARITHMETHIC_LOGICAL_CMD:
            self.writeArithmethicLogical()
        else:
            self.writeMemoryAccess()
        
    def dump(self):
        # Only write helper function when at least one compare is executed
        if self.count_compare > 0:
            self.writeHelperFunction()
        with open(self.filepath, 'w') as ASMFile:
            ASMFile.writelines(self.code)
            self.code.clear()
            self.count_compare = 0

    def addCode(self, code):
        self.code += code + "\n"

    def addComment(self, comment: str):
        self.code += f"// {comment} \n"

    def writeArithmethicLogical(self):
        ops = self.command.operation
        if ops in ASMWriter.unary_operator:
            # Take the top element on stack
            self.addCode("@SP")
            self.addCode("A=M-1")
            if ops == "neg":
                self.addCode("M=-M")
            elif ops == "not":
                self.addCode("M=!M")
        elif ops in self.compare_operator:
            self.count_compare += 1
            # Save the specific end label 
            self.addCode(f"@END_CMP_{self.count_compare}")
            self.addCode("D=A")
            self.addCode("@R14")
            self.addCode("M=D")
            # Calculate the difference between 2 top most values and decrement the stack pointer
            self.addCode("@SP")
            self.addCode("AM=M-1")
            self.addCode("D=M")
            self.addCode("A=A-1")
            self.addCode("D=M-D")
            if ops == "lt":
                self.addCode("@PUSH_TRUE")
                self.addCode("D; JLT")
                self.addCode("@PUSH_FALSE")
                self.addCode("D; JGE")
            elif ops == "gt":
                self.addCode("@PUSH_TRUE")
                self.addCode("D; JGT")
                self.addCode("@PUSH_FALSE")
                self.addCode("D; JLE")
            elif ops == "eq":
                self.addCode("@PUSH_TRUE")
                self.addCode("D; JEQ")
                self.addCode("@PUSH_FALSE")
                self.addCode("D; JNE")
            self.addCode(f"(END_CMP_{self.count_compare})")
        else:
            # Take the top element on stack
            self.addCode("@SP")
            self.addCode("AM=M-1")
            self.addCode("D=M")
            self.addCode("A=A-1")
            if ops == "add":
                self.addCode("M=D+M")
            elif ops == "sub":
                self.addCode("M=M-D")
            elif ops == "and":
                self.addCode("M=D&M")
            elif ops == "or":
                self.addCode("M=D|M")
                
    def writeHelperFunction(self):
        self.addCode("@END_PROG")
        self.addCode("0; JMP")
        self.addCode("(PUSH_FALSE)")
        self.addCode("@SP")
        self.addCode("A=M-1")
        self.addCode("M=0")
        self.addCode("@R14")
        self.addCode("A=M")
        self.addCode("0; JMP")
        self.addCode("(PUSH_TRUE)")
        self.addCode("@SP")
        self.addCode("A=M-1")
        self.addCode("M=-1")
        self.addCode("@R14")
        self.addCode("A=M")
        self.addCode("0; JMP")
        self.addCode("(END_PROG)")

    def writeMemoryAccess(self):
        if self.command.operation == "push":
            if self.command.mem_seg == "constant":
                self.addCode(f"@{self.command.position}")
                self.addCode("D=A")
                # Optimize: increase stack pointer and assign push value to it at the same time
                self.addCode("@SP")
                self.addCode("AM=M+1")
                self.addCode("A=A-1")
                self.addCode("M=D")
            elif self.command.mem_seg == "temp":
                self.addCode(f"@{5+self.command.position}")
                self.addCode("D=M")
                # Optimize: increase stack pointer and assign push value to it at the same time
                self.addCode("@SP")
                self.addCode("AM=M+1")
                self.addCode("A=A-1")
                self.addCode("M=D")
            elif self.command.mem_seg == "static":
                self.addCode(f"@{self.module_name}.{self.command.position}")
                self.addCode("D=M")
                # Optimize: increase stack pointer and assign push value to it at the same time
                self.addCode("@SP")
                self.addCode("AM=M+1")
                self.addCode("A=A-1")
                self.addCode("M=D") 
            elif self.command.mem_seg == "pointer":
                if self.command.position == 0:
                    self.addCode("@THIS")
                elif self.command.position == 1:
                    self.addCode("@THAT")
                self.addCode("D=M")
                # Optimize: increase stack pointer and assign push value to it at the same time
                self.addCode("@SP")
                self.addCode("AM=M+1")
                self.addCode("A=A-1")
                self.addCode("M=D")         
            elif self.command.mem_seg in self.simple_segment:
                self.addCode(f"@{self.command.position}")
                self.addCode("D=A")
                self.addCode(f"@{self.simple_segment[self.command.mem_seg]}")
                self.addCode("A=D+M")
                self.addCode("D=M")
                # Optimize: increase stack pointer and assign push value to it at the same time
                self.addCode("@SP")
                self.addCode("AM=M+1")
                self.addCode("A=A-1")
                self.addCode("M=D")
        elif self.command.operation == "pop":
            if self.command.mem_seg in self.simple_segment:
                self.addCode(f"@{self.command.position}")
                self.addCode("D=A")
                self.addCode(f"@{self.simple_segment[self.command.mem_seg]}")
                self.addCode("D=D+M")
                # self.addCode("@R13")
                # self.addCode("M=D")
                # Optimize: update the stack pointer and get the value of it at the same time
                # Reduce 2 lines of code
                self.addCode("@SP")
                self.addCode("AM=M-1")
                # self.addCode("@R13")
                # self.addCode("A=M")
                # Optimize: using swapping in place to avoid of using temporary memory to store pop memory
                # Reduce 3 lines of code
                self.addCode("D=D+M")
                self.addCode("A=D-M")
                self.addCode("M=D-A")
            elif self.command.mem_seg == "temp":
                # Optimize: update the stack pointer and get the value of it at the same time
                # Reduce 2 lines of code
                self.addCode("@SP")
                self.addCode("AM=M-1")
                self.addCode("D=M")
                self.addCode(f"@{5+self.command.position}")
                self.addCode("M=D")
            elif self.command.mem_seg == "static":
                # Optimize: update the stack pointer and get the value of it at the same time
                # Reduce 2 lines of code
                self.addCode("@SP")
                self.addCode("AM=M-1")
                self.addCode("D=M")
                self.addCode(f"@{self.module_name}.{self.command.position}")
                self.addCode("M=D")
            elif self.command.mem_seg == "pointer":
                # Optimize: update the stack pointer and get the value of it at the same time
                # Reduce 2 lines of code
                self.addCode("@SP")
                self.addCode("AM=M-1")
                self.addCode("D=M")
                if self.command.position == 0:
                    self.addCode("@THIS")
                elif self.command.position == 1:
                    self.addCode("@THAT")
                self.addCode("M=D")

class VMTranslator():

    def __init__(self, filepath: str) -> None:
        self.filepath_in = filepath
        self.filepath_out = filepath[:-3] + ".asm"
        self.parser = VMParser(self.filepath_in)
        self.coder = ASMWriter(self.filepath_out)
    
    def convert(self) -> None:
        command = self.parser.nextCommand()
        while (command is not None):
            self.coder.write(command)
            command = self.parser.nextCommand()
        self.coder.dump()

if __name__ == "__main__":
    filepath = sys.argv[1] 
    translator = VMTranslator(filepath)
    translator.convert()    


