from enum import Enum
from pathlib import PurePath, Path
from collections import defaultdict
import sys

class VMCommandType(Enum):
    ARITHMETHIC_LOGICAL_CMD = 1
    MEMORY_ACCESS_CMD = 2
    LABEL_CMD = 3
    GOTO_CMD = 4
    IF_CMD = 5
    CALL_CMD = 6
    RETURN_CMD = 7
    FUNCTION_CMD = 8

class VMCommand():
    
    def __init__(self, operation:str, *args):
        self.origin = " ".join([operation, *args])
        self.operation = operation
        if len(args) == 0:
            if self.operation == "return":
                self.type = VMCommandType.RETURN_CMD
            else:
                self.type = VMCommandType.ARITHMETHIC_LOGICAL_CMD
        elif len(args) == 1:
            if operation == "label":
                self.type = VMCommandType.LABEL_CMD
            elif operation == "if-goto":
                self.type = VMCommandType.IF_CMD
            elif operation == "goto":
                self.type = VMCommandType.GOTO_CMD
            self.label = args[0]
        elif len(args) == 2:
            if operation == "function":
                self.type = VMCommandType.FUNCTION_CMD
                self.label = args[0]
                self.localnum = int(args[1])
                # print(self.localnum, self.label)
            elif operation == "call":
                self.type = VMCommandType.CALL_CMD
                self.label = args[0]
                self.argnum = int(args[1])
            else:
                self.type = VMCommandType.MEMORY_ACCESS_CMD
                self.mem_seg = args[0]
                self.position = int(args[1])     

class VMParser():
    
    def __init__(self, filepath: str):
        self.commands = self.read(filepath)
        self.current_index = 0

    # Read all commands and store them in a list
    def read(self, filepath: Path) -> list[tuple[str, "VMCommand"]]:
        commands = []
        if filepath.is_dir():
            for vmpath in filter(lambda x: x.suffix == ".vm", filepath.iterdir()):
                with open(vmpath, 'r') as VMFile:
                    for line in VMFile:  # More memory efficient than readlines()
                        command = self.parse(line)
                        if command is not None:
                            commands.append((vmpath.stem, command))
        else:
            with open(filepath, 'r') as VMFile:
                for line in VMFile:  # More memory efficient than readlines()
                    command = self.parse(line)
                    if command is not None:
                        commands.append((filepath.stem, command))
        return commands

    # Parse the VM line of code into VMCommand object
    def parse(self, line: str) -> "VMCommand":
        comment_idx = line.find("//")
        line = line[:comment_idx]
        line = line.strip().lower()
        if line == "": 
            return None
        else:
            fields = line.split(" ")
            return VMCommand(*fields)
        
    # Get the next command from the list
    def nextCommand(self) -> tuple[str, "VMCommand"]:
        if self.current_index < len(self.commands):
            cmd = self.commands[self.current_index]
            self.current_index += 1
            return cmd
        else:
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
    def __init__(self, filepath: str, init=False):
        self.filepath = filepath
        self.module =  PurePath(self.filepath).stem
        self.command = None
        self.code = []
        self.count_compare = 0
        self.currrent_func = ""
        self.call_count = defaultdict(lambda: 0)
        if init:
            self.writeInit()

    def write(self, module: str, command: "VMCommand") -> str:
        self.command = command
        self.module = module
        self.addComment(command.origin)
        if command.type == VMCommandType.ARITHMETHIC_LOGICAL_CMD:
            self.writeArithmethicLogical()
        elif command.type == VMCommandType.MEMORY_ACCESS_CMD:
            self.writeMemoryAccess(command.operation)
        elif command.type == VMCommandType.LABEL_CMD:
            self.writeLabel(command.label)
        elif command.type == VMCommandType.GOTO_CMD:
            self.writeGoto(command.label)
        elif command.type == VMCommandType.IF_CMD:
            self.writeIf(command.label)
        elif command.type == VMCommandType.FUNCTION_CMD:
            self.writeFunction(command.label, command.localnum)
        elif command.type == VMCommandType.CALL_CMD:
            self.writeCall(command.label, command.argnum)
        elif command.type == VMCommandType.RETURN_CMD:
            self.writeReturn()
        
    def dump(self):
        if self.count_compare > 0:
            self.writeHelperFunction()
        with open(self.filepath, 'w') as ASMFile:
            ASMFile.writelines(self.code)
            self.code.clear()
            self.count_compare = 0
            self.currrent_func = ""
            self.call_count = {}

    def addCode(self, code):
        self.code += code + "\n"

    def addComment(self, comment: str):
        self.code += f"// {comment} \n"

    def writeInit(self):
        # Set SP = 256
        self.addComment("Bootstrap init")
        self.addCode("@256")
        self.addCode("D=A")
        self.addCode("@SP")
        self.addCode("M=D")
        # Call Sys.init()
        self.addComment("Call Sys.init")
        self.writeCall("sys.init", 0)
        
    def writeLabel(self, label: str):
        if self.currrent_func:
            self.code += f"({self.currrent_func}${label})\n"
        else:
            self.code += f"({label})\n"

    def writeGoto(self, label: str):
        if self.currrent_func:
            self.addCode(f"@{self.currrent_func}${label}")
        else:
            self.addCode(f"@{label}")
        self.addCode(f"0; JMP")

    def writeIf(self, label: str):
        self.addCode("@SP")
        self.addCode("AM=M-1")
        self.addCode("D=M")
        if self.currrent_func:
            self.addCode(f"@{self.currrent_func}${label}")
        else:
            self.addCode(f"@{label}")
        self.addCode("D; JNE")

    def writeFunction(self, label: str, localnum: int):
        self.addCode(f"({label})")
        self.currrent_func = label
        if localnum > 0:
            self.addCode(f"@SP")
            self.addCode("A=M")
            # Initialize all the local to 0 and increase the stack pointer
            for _ in range(localnum):
                self.addCode("M=0")
                self.addCode(f"@SP")
                self.addCode("AM=M+1")

    def writeCall(self, label: str, argnum:int):
        self.addCode(f"@{label}$ret.{self.call_count[label]}")
        self.addCode("D=A")
        self.addCode("@SP")
        self.addCode("A=M")
        self.addCode("M=D")
        # Save caller LCL
        self.addCode("@LCL")
        self.addCode("D=M")
        self.addCode("@SP")
        self.addCode("AM=M+1")
        self.addCode("M=D")
        # Save caller ARG
        self.addCode("@ARG")
        self.addCode("D=M")
        self.addCode("@SP")
        self.addCode("AM=M+1")
        self.addCode("M=D")
        # Save caller THIS
        self.addCode("@THIS")
        self.addCode("D=M")
        self.addCode("@SP")
        self.addCode("AM=M+1")
        self.addCode("M=D")
        # Save caller THAT
        self.addCode("@THAT")
        self.addCode("D=M")
        self.addCode("@SP")
        self.addCode("AM=M+1")
        self.addCode("M=D")
        # Reposition ARG
        self.addCode(f"@{4+argnum}")
        self.addCode("D=A")
        self.addCode("@SP")
        self.addCode("D=M-D")
        self.addCode("@ARG")
        self.addCode("M=D")
        # Reposition LCL
        self.addCode("@SP")
        #BUG: fix MD instead of DM
        self.addCode("MD=M+1")
        self.addCode("@LCL")
        self.addCode("M=D")
        # Goto function
        self.addCode(f"@{label}")
        self.addCode("0; JMP")
        # Add return label
        self.addCode(f"({label}$ret.{self.call_count[label]})")
        self.call_count[label] += 1
        

    def writeReturn(self):
        # BUG: always save LCL and return before other opearation
        # In case there are no argument, it wil override  return value by pop value
        # endFrame = LCL
        self.addCode("@LCL")
        self.addCode("D=M")
        self.addCode("@R13")
        self.addCode("M=D")
        # pop return = *(endFrame-5)  
        self.addCode("@5")
        self.addCode("A=D-A")
        self.addCode("D=M")
        self.addCode("@R14")
        self.addCode("M=D")
        # *ARG = pop()
        self.addCode("@SP")
        self.addCode("A=M-1")
        self.addCode("D=M")
        self.addCode("@ARG")
        self.addCode("A=M")
        self.addCode("M=D")
        # SP = ARG + 1
        self.addCode("@ARG")
        self.addCode("D=M")
        self.addCode("@SP")
        self.addCode("M=D+1")
        # pop THAT = *(endFrame-1)
        self.addCode("@R13") #Temporary endpointer
        self.addCode("AM=M-1")
        self.addCode("D=M")
        self.addCode("@THAT")
        self.addCode("M=D")
        # pop THIS = *(endFrame-2)
        self.addCode("@R13") #Temporary endpointer
        self.addCode("AM=M-1")
        self.addCode("D=M")
        self.addCode("@THIS")
        self.addCode("M=D")
        # pop ARG = *(endFrame-3)
        self.addCode("@R13") #Temporary endpointer
        self.addCode("AM=M-1")
        self.addCode("D=M")
        self.addCode("@ARG")
        self.addCode("M=D")
        # pop LCL = *(endFrame-4)
        self.addCode("@R13") #Temporary endpointer
        self.addCode("AM=M-1")
        self.addCode("D=M")
        self.addCode("@LCL")
        self.addCode("M=D")
        # return to caller
        self.addCode("@R14")
        self.addCode("A=M")
        self.addCode("0; JMP")

    def writeArithmethicLogical(self):
        ops = self.command.operation
        if ops in ASMWriter.unary_operator:
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
            # Assign true/false value based on compare result
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
            # Calculate the arithmethic between 2 top most values and decrement the stack pointer
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

    def writeMemoryAccess(self, operation):
        if operation == "push":
            if self.command.mem_seg == "constant":
                self.addCode(f"@{self.command.position}")
                self.addCode("D=A")
                self.addCode("@SP")
                self.addCode("AM=M+1")
                self.addCode("A=A-1")
                self.addCode("M=D")
            elif self.command.mem_seg == "temp":
                self.addCode(f"@{5+self.command.position}")
                self.addCode("D=M")
                self.addCode("@SP")
                self.addCode("AM=M+1")
                self.addCode("A=A-1")
                self.addCode("M=D")
            elif self.command.mem_seg == "static":
                self.addCode(f"@{self.module}.{self.command.position}")
                self.addCode("D=M")
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
                self.addCode("@SP")
                self.addCode("AM=M+1")
                self.addCode("A=A-1")
                self.addCode("M=D")
        elif operation == "pop":
            if self.command.mem_seg in self.simple_segment:
                self.addCode(f"@{self.command.position}")
                self.addCode("D=A")
                self.addCode(f"@{self.simple_segment[self.command.mem_seg]}")
                self.addCode("D=D+M")
                self.addCode("@SP")
                self.addCode("AM=M-1")
                self.addCode("D=D+M")
                self.addCode("A=D-M")
                self.addCode("M=D-A")
            elif self.command.mem_seg == "temp":
                self.addCode("@SP")
                self.addCode("AM=M-1")
                self.addCode("D=M")
                self.addCode(f"@{5+self.command.position}")
                self.addCode("M=D")
            elif self.command.mem_seg == "static":
                self.addCode("@SP")
                self.addCode("AM=M-1")
                self.addCode("D=M")
                self.addCode(f"@{self.module}.{self.command.position}")
                self.addCode("M=D")
            elif self.command.mem_seg == "pointer":
                self.addCode("@SP")
                self.addCode("AM=M-1")
                self.addCode("D=M")
                if self.command.position == 0:
                    self.addCode("@THIS")
                elif self.command.position == 1:
                    self.addCode("@THAT")
                self.addCode("M=D")

class VMTranslator():

    def __init__(self, filepath: Path) -> None:
        self.filepath_in = filepath
        if filepath.is_dir():
            self.filepath_out = filepath.joinpath(filepath.name).with_suffix('.asm')
            self.coder = ASMWriter(self.filepath_out, init=True)
        else:
            self.filepath_out = filepath.with_suffix('.asm')
            self.coder = ASMWriter(self.filepath_out, init=False)
        self.parser = VMParser(self.filepath_in)
    
    def convert(self) -> None:
        command = self.parser.nextCommand()
        while (command is not None):
            self.coder.write(command[0], command[1])
            command = self.parser.nextCommand()
        self.coder.dump()

if __name__ == "__main__":
    filepath = sys.argv[1] 
    translator = VMTranslator(Path(filepath))
    translator.convert()    


