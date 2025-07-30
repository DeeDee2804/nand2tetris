from enum import Enum
from pathlib import Path

import sys
import re

class TokenType(Enum):
    KEYWORD = "keyword"
    IDENTIFIER = "identifier"
    INT_CONST = "integerConstant"
    STRING_CONST = "stringConstant"
    SYMBOL = "symbol"

class VariableKind(Enum):
    STATIC = "static"
    FIELD = "this"
    ARGUMENT = "argument"
    LOCAL = "local"
    NONE = None
        
class VMSegment(Enum):
    CONSTANT = "constant"
    ARGUMENT = "argument"
    LOCAL = "local"
    STATIC = "static"
    THIS = "this"
    THAT = "that"
    POINTER = "pointer"
    TEMP = "temp"
    
class VMCommand(Enum):
    ADD = "add"
    SUB = "sub"
    NEG = "neg"
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    AND = "and"
    OR = "or"
    NOT = "not"

class Token:
    """
    Represents a single token with its type and value.
    """
    
    def __init__(self, token_type: TokenType, value: str):
        """
        Initialize a token with its type and value.
        
        :param token_type: The type of the token (from TokenType enum)
        :param value: The string value of the token
        """
        self.token_type = token_type
        self.value = value

    def xml(self) -> str:
        """
        Returns the XML representation of the token.
        
        :return: A string in XML format representing the token.
        """
        if self.token_type == TokenType.SYMBOL:
            # Escape special characters in symbols
            escaped_value = self.value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return f"<{self.token_type.value}> {escaped_value} </{self.token_type.value}>"
        return f"<{self.token_type.value}> {self.value} </{self.token_type.value}>"

class SymbolTable:
    """
    A class to handle the symbol table of a file
    """
    
    def __init__(self):
        """
        Initializes the symbol table with empty dictionaries for class and subroutine symbols.
        """
        self.symbols: dict[str, tuple[str, VariableKind, int]] = {}
        self.kindCount = {}
    
    def define(self, name: str, varType: str, varKind: VariableKind):
        """
        Defines a new variable in the current scope.
        
        :param name: The name of the variable
        :param varType: The type of the variable (e.g., int, char, boolean, or identifier)
        :param varKind: The kind of the variable (from VariableKind enum)
        """
        self.symbols[name] = {"type": varType, "kind": varKind, "index": self.varCount(varKind)}
        self.kindCount[varKind] = self.varCount(varKind) + 1
            
    def varCount(self, varKind: VariableKind) -> int:
        """
        Returns the number of variables of the given kind in the current scope.

        :param varKind: The kind of the variable (from VariableKind enum)
        :return: The number of variables with the given kind
        """
        return self.kindCount.get(varKind, 0)
    
    def kindOf(self, name: str) -> VariableKind:
        """
        Returns the kind of the variable with the given name in the current scope.

        :param name: The name of the variable
        :return: The kind of the variable (from VariableKind enum)
        """
        return self.symbols.get(name, {}).get("kind", VariableKind.NONE)

    def typeOf(self, name: str) -> str|None:
        """
        Returns the type of the variable with the given name in the current scope.

        :param name: The name of the variable
        :return: The type of the variable (as a string)
        """
        return self.symbols.get(name, {}).get("type", None)
        
    def indexOf(self, name: str) -> int:
        """
        Returns the index of the variable with the given name in the current scope.

        :param name: The name of the variable
        :return: The index of the variable (as an integer)
        """
        return self.symbols.get(name, {}).get("index", -1)

    def __repr__(self):
        """
        Returns a string representation of the symbol table.
        
        :return: A string showing the symbols in the table.
        """
        return "\n".join(f"{name}: {info['type']} {info['kind'].value} {info['index']}" for name, info in self.symbols.items())


class VMWriter:
    """
    A class to write VM commands to a file.
    """
    
    def __init__(self, filepath: Path) -> None:
        self.classname = filepath.stem
        self.content = []
        self.filepath = filepath

    def writePush(self, segment: VMSegment, index: int):
        """
        Writes a push command to the VM file.
        
        :param segment: The segment to push from (from VMSegment enum)
        :param index: The index in the segment
        """
        self.content.append(f"push {segment.value} {index}")
        
    def writePop(self, segment: VMSegment, index: int):
        """
        Writes a pop command to the VM file.

        :param segment: The segment to pop from (from VMSegment enum)
        :param index: The index in the segment
        """
        self.content.append(f"pop {segment.value} {index}")
    
    def writeArithmetic(self, command: VMCommand):
        """
        Writes an arithmetic command to the VM file.
        
        :param command: The arithmetic command to write (from VMCommand enum)
        """
        self.content.append(f"{command.value}")

    def writeLabel(self, label: str):
        """
        Writes a label command to the VM file.
        
        :param label: The label to write
        """
        self.content.append(f"label {label}")
    
    def writeGoto(self, label: str):
        """
        Writes a goto command to the VM file.
        
        :param label: The label to go to
        """
        self.content.append(f"goto {label}")
    
    def writeIf(self, label: str):
        """
        Writes an if-goto command to the VM file.
        
        :param label: The label to go to if the top of the stack is true
        """
        self.content.append(f"if-goto {label}")
    
    def writeCall(self, name: str, nArgs: int):
        """
        Writes a call command to the VM file.
        
        :param name: The name of the subroutine to call
        :param nArgs: The number of arguments for the subroutine
        """
        self.content.append(f"call {name} {nArgs}")
    
    def writeFunction(self, name: str, nVars: int):
        """
        Writes a function command to the VM file.
        
        :param name: The name of the function
        :param nVars: The number of local variables for the function
        """
        self.content.append(f"function {self.classname}.{name} {nVars}")

    def writeReturn(self):
        """
        Writes a return command to the VM file.
        """
        self.content.append("return")

    def flush(self):
        """
        Writes the accumulated VM commands to the file.
        """
        with open(self.filepath, 'w') as vm_file:
            for line in self.content:
                vm_file.write(line + "\n")
        self.content.clear()
    

class JackTokenizer:
    """
    A class to tokenize Jack source code.
    """
    keywords = {
        "class", "constructor", "function", "method", "field", "static",
        "var", "int", "char", "boolean", "void", "true", "false", "null",
        "this", "let", "do", "if", "else", "while", "return"
    }
    symbols = "{}()[];,.+-*/&|<>=~"


    def __init__(self, filepath: Path):
        """
        Initializes the tokenizer with the given source code.

        :param file_path: The path to the Jack source code file.
        """
        self.tokens: list[Token] = []
        self.current_token_index = 0
        self.tokenize(filepath)


    def tokenize(self, filepath: Path):
        """
        Tokenizes the source code into a list of tokens.
        Assumes that the file is a valid Jack source code file.

        :param file_path: The path to the Jack source code file.
        """
        with open(filepath, 'r') as JackFile:
            self.content = JackFile.read()
        
        # Reset the tokens list
        self.tokens = []
        
        # Iterate over each character of content
        self.pos = 0
        self.length = len(self.content)
        while self.pos < self.length:
            # Skip whitespace
            if self.content[self.pos].isspace():
                self.pos += 1
                continue
                
            # Check for single line comment
            if self.pos < self.length - 1 and self.content[self.pos:self.pos+2] == '//':
                self._skip_single_line_comment()
                continue
            
            # Check for block comment
            if self.pos < self.length - 1 and self.content[self.pos:self.pos+2] == '/*':
                self._skip_multi_line_comment()
                continue
                
            # Check for string literals SECOND
            if self.content[self.pos] == '"':
                self._parse_string_literal()
                continue
                
            # Check for numbers
            if self.content[self.pos].isdigit():
                self._parse_number()
                continue
                
            # Check for symbols
            if self.content[self.pos] in self.symbols:
                self.tokens.append(Token(TokenType.SYMBOL, self.content[self.pos]))
                self.pos += 1
                continue
                
            # Check for identifiers/keywords
            if self.content[self.pos].isalnum() or self.content[self.pos] == '_':
                self._parse_identifier()
                continue
                
            # Invalid character
            raise ValueError(f"Unexpected character '{self.content[self.pos]}' at position {self.pos}")
        
        # Clean up to free memory
        self.content = ""
        self.pos = 0
        self.length = 0

    def _skip_single_line_comment(self) -> None:
        """Skip single line comment and return new position."""
        # Skip // 
        self.pos += 2
        # Search for end of comment
        while self.pos < self.length and self.content[self.pos] != '\n':
            self.pos += 1
        # Skip \n if exist
        if self.pos < self.length:
            self.pos += 1   

    def _skip_multi_line_comment(self) -> None:
        """Skip multi-line comment and return new position."""
        # Skip /*
        self.pos += 2
        # Search for end of comment
        while self.pos < self.length - 1:
            if self.content[self.pos:self.pos+2] == '*/':
                # Skip */
                self.pos += 2 
                return
            self.pos += 1
        raise ValueError("Unterminated multi-line comment")

    def _parse_string_literal(self) -> None:
        # Skip opening quote "
        self.pos += 1
        start = self.pos
        # Search for end of string literal
        while self.pos < self.length and self.content[self.pos] != '"':
            if self.content[self.pos] == '\\':
                # Skip escape sequence that may contain "
                self.pos += 2
            else:
                self.pos += 1
                    
        # No string literal found
        if self.pos >= self.length:
            raise ValueError("Unterminated string literal")
        
        # Extract the raw string (including escape sequences)
        string_value = self.content[start:self.pos]
        self.tokens.append(Token(TokenType.STRING_CONST, string_value))
        # Skip closing quote
        self.pos += 1  

    def _parse_number(self) -> None:
        """Parse integer literal and add token."""
        start = self.pos
        while self.pos < self.length and self.content[self.pos].isdigit():
            self.pos += 1
        # Check no mix between numbers and characters
        if self.pos < self.length and self.content[self.pos].isalpha():
            raise ValueError("Invalid character in number literal")
        
        # Extract the raw number
        number_value = self.content[start:self.pos]
        
        # Check range of parsed integer
        if len(number_value) > 5:
            raise ValueError("Integer literal too long")
        elif len(number_value) == 5 and int(number_value) > 32767:
            raise ValueError("Integer literal too large")
        self.tokens.append(Token(TokenType.INT_CONST, number_value))

    def _parse_identifier(self) -> None:
        """Parse identifier/keyword and add token."""
        start = self.pos
        while self.pos < self.length and (self.content[self.pos].isalnum() or self.content[self.pos] == '_'):
            self.pos += 1

        # Extract raw identifier/keyword
        identifier_value = self.content[start:self.pos]
        token_type = TokenType.KEYWORD if identifier_value in self.keywords else TokenType.IDENTIFIER
        self.tokens.append(Token(token_type, identifier_value))

    def hasMoreTokens(self):
        """
        Checks if there are more tokens to process.
        
        :return: True if there are more tokens, False otherwise.
        """
        return self.current_token_index < len(self.tokens)

    def advance(self) -> None:
        """
        Advances to the next token.
                
        :raises IndexError: If there are no more tokens to advance to.
        """
        if not self.hasMoreTokens():
            raise IndexError("No more tokens to advance to.")

        self.current_token_index += 1

    def currentToken(self) -> Token:
        if self.current_token_index == 0:
            raise IndexError("No current token available. Call advance() first.")
        return self.tokens[self.current_token_index - 1]
    
    def nextToken(self) -> Token:
        """
        Returns the next token without advancing the tokenizer.
        
        :raises IndexError: If there are no more tokens.
        :return: The next token.
        """
        if not self.hasMoreTokens():
            raise IndexError("No more tokens available.")
        return self.tokens[self.current_token_index]


class CompilationEngine:
    """
    A class to handle the compilation of Jack source code.
    This class is a placeholder for future compilation logic.
    """
    ops = "+-*/&|<>="
    unary_ops = "-~"

    def __init__(self, tokenizer: JackTokenizer, output_file: Path):
        """
        Initializes the compilation engine with a tokenizer and an optional output file.
        """ 
        self.tokenizer = tokenizer
        self.classTable = SymbolTable()
        self.content = []
        self.tablevel = 0
        self.classname = output_file.stem
        self.output_file = output_file.with_name(f"my{output_file.stem}.xml")
        self.writer = VMWriter(output_file)
        self.curRetType = None
        self.curInclRet = False
        self.if_count = 0
        self.while_count = 0

    def run(self):
        """
        Compiles the Jack source code using the tokenizer.
        """
        # The first valid token should be a class keyword
        self.compileClass()
        if self.tokenizer.hasMoreTokens():
            raise ValueError("Unexpected tokens after class definition.")
        self.writer.flush()
        
    def addSimpleTag(self):
        """
        Adds a simple tag with a value to the compilation engine's content list.
        
        :param token: The token to add as XML.
        """
        self.content.append(f"{'  ' * self.tablevel}{self.tokenizer.currentToken().xml()}")

    def compileClass(self):
        """
        Compiles a class from the Jack source code.
        The valid structure for a class is:
            'class' className '{' classVarDec* subroutineDec* '}'
        """
        if self.tokenizer.hasMoreTokens():
            # Expecting a 'class' keyword
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "class":
                raise ValueError(f"Expected 'class' but got {self.tokenizer.currentToken().value}")

            # Expecting a class name (identifier) after 'class'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected class name but got {self.tokenizer.currentToken().value}")
            if self.tokenizer.currentToken().value != self.classname:
                raise ValueError(f"Expected class name '{self.classname}' but got {self.tokenizer.currentToken().value}")

            # Expecting an opening brace '{' after the class name
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "{":
                raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")

            # Process class variable declarations and subroutines until we reach the closing brace '}'
            endVarDec = False
            while self.tokenizer.nextToken().value != "}":
                if self.tokenizer.nextToken().value in {"static", "field"}:
                    if endVarDec:
                        raise ValueError("Variable declaration must only be placed at the beginning of the class.")
                    self.compileClassVarDec()
                elif self.tokenizer.nextToken().value in {"constructor", "function", "method"}:
                    # Subroutine declaration must come after variable declarations (if any)
                    endVarDec = True
                    self.compileSubroutine()
                else:
                    raise ValueError(f"Unexpected token in class body: {self.tokenizer.nextToken().value}")

            # Expecting a closing brace '}' at the end of the class body
            self.tokenizer.advance()


    def compileClassVarDec(self):
        """
        Compiles a class variable declaration from the Jack source code.
        The valid structure for a class variable declaration is:
            'static' | 'field' type varName (',' varName)* ';'
        """
        self.tokenizer.advance()
        # Expecting a keyword 'static' or 'field'
        if self.tokenizer.currentToken().value == "static":
            varKind = VariableKind.STATIC
        elif self.tokenizer.currentToken().value == "field":
            varKind = VariableKind.FIELD
        else:
            raise ValueError(f"Expected 'static' or 'field' but got {self.tokenizer.currentToken().value}")

        # Expecting a type (int, char, boolean, or identifier)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value in {"int", "char", "boolean"} or self.tokenizer.currentToken().token_type == TokenType.IDENTIFIER:
            varType = self.tokenizer.currentToken().value
        else:
            raise ValueError(f"Expected type but got {self.tokenizer.currentToken().value}")
        
        # Expecting an identifier (variable name)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
        varName = self.tokenizer.currentToken().value

        # Add new variable to the symbol table
        self.classTable.define(varName, varType, varKind)

        # Check for additional variable names (optional)
        self.tokenizer.advance()
        while self.tokenizer.currentToken().value == ",":
            # Expecting a comma ',' followed by another identifier
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
            varName = self.tokenizer.currentToken().value
            # Add new variable to the symbol table
            self.classTable.define(varName, varType, varKind)
            self.tokenizer.advance()

        # Expecting a semicolon ';' at the end of the declaration
        if self.tokenizer.currentToken().value != ";":  
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")
        
        print(f"Symbol table for class {self.classname}:")
        print(self.classTable)

    def compileSubroutine(self):
        """
        Compiles a subroutine from the Jack source code.
        The valid structure for a subroutine is:
            ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        where parameterList can be empty and subroutineBody contains variable declarations and statements.
        """
        self.subRoutineTable = SymbolTable()
        self.curRetType = None
        self.curInclRet = False

        # Expecting a subroutine kind (constructor | function | method)
        self.tokenizer.advance()
        self.curFuncType = self.tokenizer.currentToken().value
        if self.curFuncType == "constructor":
            self.curRetType = "this"
        elif self.curFuncType not in {"function", "method"}:
            raise ValueError(f"Expected 'constructor', 'function', or 'method' but got {self.curFuncType}")

        # Expecting a return type (void or type)
        if self.tokenizer.nextToken().value == "void":
            self.tokenizer.advance()
            self.curRetType = "void"
        else:
            # Expecting a type (int, char, boolean, or identifier)
            self.tokenizer.advance()
            token = self.tokenizer.currentToken()
            if self.curFuncType == "constructor":
                if token.value != self.classname:
                    raise ValueError("Constructor return type must have the same name as the class")
            else:        
                if token.value in {"int", "char", "boolean"} or token.token_type == TokenType.IDENTIFIER:
                    self.curRetType = token.value
                else:
                    raise ValueError(f"Expected type but got {token.value}")
        
        # Expecting a subroutine name (identifier)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected subroutine name but got {self.tokenizer.currentToken().value}")
        self.curFuncName = self.tokenizer.currentToken().value

        # Expecting an opening parenthesis '(' for the parameter list
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "(":
            raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")

        # If it's a method, add 'this' as the first parameter
        if self.curFuncType == "method":
            self.subRoutineTable.define("this", self.classname, VariableKind.ARGUMENT)
        # Compile the parameter list
        self.compileParameterList()

        # Expecting a closing parenthesis ')' after the parameter list
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ")":
            raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")

        # Compile the subroutine body
        self.compileSubroutineBody()

        print(f"Symbol table for subroutine {self.curFuncName}:")
        print(self.subRoutineTable)

    def compileParameterList(self) -> int:
        """
        Compiles a parameter list from the Jack source code.
        The valid structure for a parameter list is:
            (type varName ("," type varName)*)
    
        """
        numParams = 0
        # If the next token is a closing parenthesis, we have an empty parameter list
        if (self.tokenizer.nextToken().value == ")"):
            return numParams

        # Expecting a type (int, char, boolean, or identifier)
        self.tokenizer.advance()
        token = self.tokenizer.currentToken()
        if token.value in {"int", "char", "boolean"} or token.token_type == TokenType.IDENTIFIER:
            varType = token.value
        else:
            raise ValueError(f"Expected type but got {token.value}")

        # Expecting a parameter name (identifier)
        self.tokenizer.advance()
        token = self.tokenizer.currentToken()
        if token.token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected parameter name but got {token.value}")
        numParams += 1
        varName = token.value
        self.subRoutineTable.define(varName, varType, VariableKind.ARGUMENT)

        # Check for additional parameters (optional)
        while self.tokenizer.nextToken().value == ",":
            self.tokenizer.advance()

            # Expecting a type (int, char, boolean, or identifier)
            self.tokenizer.advance()
            token = self.tokenizer.currentToken()
            if token.value in {"int", "char", "boolean"} or token.token_type == TokenType.IDENTIFIER:
                varType = token.value
            else:
                raise ValueError(f"Expected type but got {token.value}")

            # Expecting a parameter name (identifier)
            self.tokenizer.advance()
            token = self.tokenizer.currentToken()
            if token.token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected parameter name but got {token.value}")
            numParams += 1
            varName = token.value
            self.subRoutineTable.define(varName, varType, VariableKind.ARGUMENT)
        return numParams

    def compileSubroutineBody(self):
        """
        Compiles a subroutine body from the Jack source code.
        The valid structure for a subroutine body is:
            '{' varDec* statements '}'
        """
        # Expecting an opening brace '{' for the subroutine body
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "{":
            raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")

        # Process variable declarations
        while self.tokenizer.nextToken().value == "var":
            self.compileVarDec()
        
        # Write the VM function
        self.writer.writeFunction(self.curFuncName, self.subRoutineTable.varCount(VariableKind.LOCAL))

        # If it's a constructor, allocate memory for the object first
        # and set the pointer to the new object
        if self.curFuncType == "constructor":
            self.writer.writePush(VMSegment.CONSTANT, self.classTable.varCount(VariableKind.FIELD))
            self.writer.writeCall("Memory.alloc", 1)
            self.writer.writePop(VMSegment.POINTER, 0)
        # If it's a method, pass the first argument (this) to the method
        elif self.curFuncType == "method":
            self.writer.writePush(VMSegment.ARGUMENT, 0)
            self.writer.writePop(VMSegment.POINTER, 0)
            
        # Compile the statements within the subroutine body
        self.compileStatements()
        
        # Check if at least one return statement is included
        if not self.curInclRet:
            raise ValueError("Missing return statement in function.")

        # Expecting a closing brace '}' for the subroutine body
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "}":
            raise ValueError(f"Expected '}}' but got {self.tokenizer.currentToken().value}")

    def compileVarDec(self):
        """
        Compiles a variable declaration from the Jack source code.
        Pre-condition: Need to advance tokenizer before calling this method.
        The valid structure for a variable declaration is:
            'var' type varName (',' varName)* ';'
        """
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "var":
            raise ValueError(f"Expected 'var' but got {self.tokenizer.currentToken().value}")
        
        # Expecting a type (int, char, boolean, or identifier)
        self.tokenizer.advance()
        token = self.tokenizer.currentToken()
        if token.value in {"int", "char", "boolean"} or token.token_type == TokenType.IDENTIFIER:
            varType = token.value
        else:
            raise ValueError(f"Expected type but got {token.value}")

        # Expecting a variable name (identifier)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
        varName = self.tokenizer.currentToken().value
        # Add new variable to the symbol table
        self.subRoutineTable.define(varName, varType, VariableKind.LOCAL)

        # Check for additional variable names
        self.tokenizer.advance()
        while self.tokenizer.currentToken().value == ",":
            # Expecting a comma ',' followed by another identifier
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
            varName = self.tokenizer.currentToken().value
            # Add new variable to the symbol table
            self.subRoutineTable.define(varName, varType, VariableKind.LOCAL)
            self.tokenizer.advance()

        # Expecting a semicolon ';' at the end of the declaration
        if self.tokenizer.currentToken().value != ";":
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")

    def compileStatements(self):
        """
        Compiles statements from the Jack source code.\n
        The valid structure for statements is:\n
            statement*\n
        """
        while self.tokenizer.nextToken().value in {"let", "if", "while", "do", "return"}:
            if self.tokenizer.nextToken().value == "let":
                self.compileLet()
            elif self.tokenizer.nextToken().value == "if":
                self.compileIf()
            elif self.tokenizer.nextToken().value == "while":
                self.compileWhile()
            elif self.tokenizer.nextToken().value == "do":
                self.compileDo()
            elif self.tokenizer.nextToken().value == "return":
                self.curInclRet = True
                self.compileReturn()
            else:
                raise ValueError(f"Unexpected statement type: {self.tokenizer.nextToken().value}")

    def compileLet(self):
        """
        Compiles a 'let' statement from the Jack source code.  
        The valid structure for a 'let' statement is:
            'let' varName ('[' expression ']')? '=' expression ';'
        """
        isArrayAssignment = False

        # Expecting a 'let' keyword
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "let":
            raise ValueError(f"Expected 'let' but got {self.tokenizer.currentToken().value}")

        # Expecting a variable name (identifier)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
        varName = self.tokenizer.currentToken().value
        # Check for array access (optional)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value == "[":
            isArrayAssignment = True
            if self.subRoutineTable.indexOf(varName) == -1:
                # If the variable is not defined in the current subroutine, check the class table
                if self.classTable.indexOf(varName) == -1:
                    raise ValueError(f"Variable '{varName}' is not defined.")
                else:
                    # If the variable is defined in the class table, push it onto the stack
                    self.writer.writePush(self.classTable.kindOf(varName), 
                                            self.classTable.indexOf(varName))
            else:
                # If the variable is defined in the current subroutine, use its type
                self.writer.writePush(self.subRoutineTable.kindOf(varName), 
                                        self.subRoutineTable.indexOf(varName))
            # Expecting an expression inside the brackets
            self.compileExpression()

            # Add offset to base address of the array
            self.writer.writeArithmetic(VMCommand.ADD)

            # Expecting a closing bracket ']'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "]":
                raise ValueError(f"Expected ']' but got {self.tokenizer.currentToken().value}")
            self.tokenizer.advance()
        elif self.tokenizer.currentToken().value != "=":
            # If we are not accessing an array, we should be at the assignment operator
            raise ValueError(f"Expected '[' or '=' but got {self.tokenizer.currentToken().value}")

        # Expecting an expression after the '='
        self.compileExpression()

        if isArrayAssignment:
            # Pop the value to be assigned to temporary storage
            self.writer.writePop(VMSegment.TEMP, 0)
            # Pop the base address of the array element
            self.writer.writePop(VMSegment.POINTER, 1)
            # Push the value from temporary storage back to the stack
            self.writer.writePush(VMSegment.TEMP, 0)
            # Store the value at the calculated address
            self.writer.writePop(VMSegment.THAT, 0)
        else:
            # If it's not an array assignment, we can directly pop the value to the variable
            if self.subRoutineTable.indexOf(varName) != -1:
                # If the variable is defined in the current subroutine, use its type
                self.writer.writePop(self.subRoutineTable.kindOf(varName), 
                                        self.subRoutineTable.indexOf(varName))
            elif self.classTable.indexOf(varName) != -1:
                # If the variable is defined in the class table, push it onto the stack
                self.writer.writePop(self.classTable.kindOf(varName), 
                                        self.classTable.indexOf(varName))
            else:
                raise ValueError(f"Variable '{varName}' is not defined.")

        # Expecting a semicolon ';'
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ";":
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")

    def compileIf(self):
        """
        Compiles an 'if' statement from the Jack source code.
        The valid structure for an 'if' statement is:
            'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        # Store the current if count to create unique labels during nested if statements
        if_count = self.if_count
        self.if_count += 1
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "if":
            raise ValueError(f"Expected 'if' but got {self.tokenizer.currentToken().value}")

        # Expecting an opening parenthesis '('
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "(":
            raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")

        # Expecting an expression inside the parentheses
        self.compileExpression()
         # Negate the expression for the if condition
        self.writer.writeArithmetic(VMCommand.NOT) 
        self.writer.writeIf(f"IF_ELSE{if_count}")

        # Expecting a closing parenthesis ')'
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ")":
            raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")

        # Expecting an opening brace '{' for the statements block
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "{":
            raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")

        # Compile the statements inside the 'if' block
        self.compileStatements()

        # Write to the VM writer to handle the end of the 'if' block
        self.writer.writeGoto(f"IF_END{if_count}")

        # Write the label for else condition
        self.writer.writeLabel(f"IF_ELSE{if_count}")

        # Expecting a closing brace '}' for the 'if' block
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "}":
            raise ValueError(f"Expected '}}' but got {self.tokenizer.currentToken().value}")

        # Check for an optional 'else' clause
        if self.tokenizer.nextToken().value == "else":
            self.tokenizer.advance()
            # Expecting an opening brace '{' for the 'else' block
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "{":
                raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")

            # Compile the statements inside the 'else' block
            self.compileStatements()

            # Expecting a closing brace '}' for the 'else' block
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "}":
                raise ValueError(f"Expected '}}' but got {self.tokenizer.currentToken().value}")
        
        # Write the end label for the 'if' statement
        self.writer.writeLabel(f"IF_END{if_count}")

    def compileWhile(self):
        """
        Compiles a 'while' statement from the Jack source code.
        The valid structure for a 'while' statement is:
            'while' '(' expression ')' '{' statements '}'
        """
        # Store the current while count to create unique labels during nested loops
        while_count = self.while_count
        self.while_count += 1
        # Expecting a 'while' keyword
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "while":
            raise ValueError(f"Expected 'while' but got {self.tokenizer.currentToken().value}")
        # Write the label for the start of the while loop
        self.writer.writeLabel(f"WHILE_START{while_count}")

        # Expecting an opening parenthesis '('
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "(":
            raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")
  
        # Expecting an expression inside the parentheses
        self.compileExpression()

        # Expecting a closing parenthesis ')'
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ")":
            raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")

        # Negate the expression for the while condition
        self.writer.writeArithmetic(VMCommand.NOT)
        # Write the if-goto command to jump out of the loop if the condition is false
        self.writer.writeIf(f"WHILE_END{while_count}")

        # Expecting an opening brace '{' for the statements block
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "{":
            raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")

        # Compile the statements inside the 'while' block
        self.compileStatements()

        # Write the goto command to jump back to the start of the loop
        self.writer.writeGoto(f"WHILE_START{while_count}")

        # Expecting a closing brace '}' for the 'while' block
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "}":
            raise ValueError(f"Expected '}}' but got {self.tokenizer.currentToken().value}")
        # Write the end label for the 'while' statement
        self.writer.writeLabel(f"WHILE_END{while_count}")

    def compileDo(self):
        """
        Compiles a 'do' statement from the Jack source code.
        The valid structure for a 'do' statement is:
            'do' subroutineCall ';'
        """
        numArgs = 0
        # Expecting a 'do' keyword
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "do":
            raise ValueError(f"Expected 'do' but got {self.tokenizer.currentToken().value}")

        # Expecting a subroutine call
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected subroutine name but got {self.tokenizer.currentToken().value}")
        
        # Check for subroutine call structure
        token = self.tokenizer.nextToken()
        if token.value == "(":
            funcName = self.tokenizer.currentToken().value
            # Subroutine call without class or variable name
            self.tokenizer.advance()

            # Compile the expression list
            self.writer.writePush(VMSegment.POINTER, 0)
            numArgs = self.compileExpressionList() + 1
            
            # Write the VM call command
            self.writer.writeCall(f"{self.classname}.{funcName}", numArgs)

            # Expecting a closing parenthesis ')'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != ")":
                raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
        elif token.value == ".":
            token = self.tokenizer.currentToken()
            # Check if it's a subroutine call with class or variable name
            if self.subRoutineTable.indexOf(token.value) == -1:
                # If the variable is not defined in the current subroutine, check the class table
                if self.classTable.indexOf(token.value) == -1:
                    # Then the subroutine call must be a class method
                    className = token.value
                    numArgs = 0
                else:
                    # Otherwise, it's a variable method
                    className = self.classTable.typeOf(token.value)
                    numArgs = 1
                    self.writer.writePush(self.classTable.kindOf(token.value),
                                            self.classTable.indexOf(token.value))
            else:
                # If the variable is defined in the current subroutine, use its type
                className = self.subRoutineTable.typeOf(token.value)
                numArgs = 1
                self.writer.writePush(self.subRoutineTable.kindOf(token.value),
                                        self.subRoutineTable.indexOf(token.value))

            # Skip the dot
            self.tokenizer.advance()

            # Expecting a subroutine name (identifier) after the dot
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected subroutine name but got {self.tokenizer.currentToken().value}")
            subName = self.tokenizer.currentToken().value    

            # Expecting an opening parenthesis '(' for the expression list
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "(":
                raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")

            # Compile the expression list
            numArgs += self.compileExpressionList()

            # Write the VM call command
            self.writer.writeCall(f"{className}.{subName}", numArgs)

            # Expecting a closing parenthesis ')'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != ")":
                raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")

        # No need to take the return value from a 'do' statement, so we must ignore it
        self.writer.writePop(VMSegment.TEMP, 0)

        # Expecting a semicolon ';' at the end
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ";":
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")

    def compileReturn(self):
        """
        Compiles a 'return' statement from the Jack source code.
        The valid structure for a 'return' statement is:
            'return' (expression)? ';'
        """
        # Expecting a 'return' keyword
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "return":
            raise ValueError(f"Expected 'return' but got {self.tokenizer.currentToken().value}")

        # Check if there is an expression
        has_expression = self.tokenizer.nextToken().value != ";"

        # Check return type
        if self.curRetType == "void":
            if has_expression:
                raise ValueError("Cannot return a value from a void function")
            # Push a dummy return constant 0 onto the stack
            self.writer.writePush(VMSegment.CONSTANT, 0)
        elif self.curRetType == "this":
            if self.tokenizer.nextToken().value != "this":
                raise ValueError(f"Constructor return type must be 'this' instead of {self.tokenizer.nextToken().value}")
        else:
            if not has_expression:
                raise ValueError(f"Expected expression but got {self.tokenizer.currentToken().value}")
        
        # Expecting an expression after 'return' (optional)
        if has_expression:
            self.compileExpression() 

        # Write the return value to the VM writer
        self.writer.writeReturn()

        # Expecting a semicolon ';' at the end
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ";":
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")

    def compileExpression(self):
        """
        Compiles an expression from the Jack source code.
        The valid structure for an expression is:
            term (op term)*
        """
        # Expecting a term as the first part of the expression
        self.compileTerm()

        # Check for additional terms with operators (optional)
        while self.tokenizer.nextToken().value in self.ops:
            self.tokenizer.advance()
            operator = self.tokenizer.currentToken().value
            # Advance to the next token which should be a term
            self.compileTerm()

            if operator == "+":
                self.writer.writeArithmetic(VMCommand.ADD)
            elif operator == "-":
                self.writer.writeArithmetic(VMCommand.SUB)
            elif operator == "*":
                self.writer.writeCall("Math.multiply", 2)
            elif operator == "/":
                self.writer.writeCall("Math.divide", 2)
            elif operator == "&":
                self.writer.writeArithmetic(VMCommand.AND)
            elif operator == "|":
                self.writer.writeArithmetic(VMCommand.OR)
            elif operator == "<":
                self.writer.writeArithmetic(VMCommand.LT)
            elif operator == ">":
                self.writer.writeArithmetic(VMCommand.GT)
            else:
                self.writer.writeArithmetic(VMCommand.EQ)

    def compileTerm(self):
        """
        Compiles a term from the Jack source code.
        The valid structure for a term is:\n
            integerConstant | stringConstant | keywordConstant | varName |
            varName '[' expression ']' | subroutineCall | '(' expression ')')? | unaryOp term\n
        The valid structure for a subroutine call is:\n
            subroutineName '(' expressionList ')' | 
            (className|varName) '.' subroutineName '(' expressionList ')

        """
        self.tokenizer.advance()
        token = self.tokenizer.currentToken()
        if token.token_type == TokenType.INT_CONST:
            # Integer constant
            self.writer.writePush(VMSegment.CONSTANT, token.value)
        elif token.token_type == TokenType.STRING_CONST:
            # String constant
            # Allocate memory for the string
            self.writer.writePush(VMSegment.CONSTANT, len(token.value))
            self.writer.writeCall("String.new", 1)
            # Push each character of the string onto the stack
            for char in token.value:
                self.writer.writePush(VMSegment.CONSTANT, ord(char))
                # Take newly created string address and each char as arguments 
                self.writer.writeCall("String.appendChar", 2)
        elif token.value in {"true", "false", "null", "this"}:
            # Keyword constant
            if token.value == "true":
                self.writer.writePush(VMSegment.CONSTANT, 1)
                self.writer.writeArithmetic(VMCommand.NEG)
            elif token.value == "false" or token.value == "null":
                self.writer.writePush(VMSegment.CONSTANT, 0)
            else:  # 'this'
                # 'this' refers to the current object, push the pointer onto the stack
                self.writer.writePush(VMSegment.POINTER, 0)
        elif token.value == "(":
            # Expression in parentheses
            self.compileExpression()

            # Expecting a closing parenthesis ')'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != ")":
                raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
        elif token.value in self.unary_ops:
            # Unary operation
            # Expecting a term after the unary operator
            self.compileTerm()
            if token.value == "-":
                self.writer.writeArithmetic(VMCommand.NEG)
            elif token.value == "~":
                self.writer.writeArithmetic(VMCommand.NOT)
        elif token.token_type == TokenType.IDENTIFIER:
            # Variable name or subroutine call
            token = self.tokenizer.nextToken()
            if token.value == "[":
                varName = self.tokenizer.currentToken().value
                # Variable name (array access)
                if self.subRoutineTable.indexOf(varName) == -1:
                    # If the variable is not defined in the current subroutine, check the class table
                    if self.classTable.indexOf(varName) == -1:
                        raise ValueError(f"Variable '{varName}' is not defined.")
                    else:
                        # If the variable is defined in the class table, push it onto the stack
                        self.writer.writePush(self.classTable.kindOf(varName), 
                                              self.classTable.indexOf(varName))
                else:
                    # If the variable is defined in the current subroutine, use its type
                    self.writer.writePush(self.subRoutineTable.kindOf(varName), 
                                          self.subRoutineTable.indexOf(varName))

                # Skip the opening bracket '['
                self.tokenizer.advance()
                
                # Expecting an expression inside the brackets
                self.compileExpression()

                # Write the VM command to add the base address of the array
                self.writer.writeArithmetic(VMCommand.ADD)
                # Set pointer to the array base address
                self.writer.writePop(VMSegment.POINTER, 1)
                # Push the value at the computed address onto the stack
                self.writer.writePush(VMSegment.THAT, 0)

                # Expecting a closing bracket ']'
                self.tokenizer.advance()
                if self.tokenizer.currentToken().value != "]":
                    raise ValueError(f"Expected ']' but got {self.tokenizer.currentToken().value}")
            elif token.value == ".":
                token = self.tokenizer.currentToken()
                # Check if it's a subroutine call with class or variable name
                if self.subRoutineTable.indexOf(token.value) == -1:
                    # If the variable is not defined in the current subroutine, check the class table
                    if self.classTable.indexOf(token.value) == -1:
                        # Then the subroutine call must be a class method
                        className = token.value
                        numArgs = 0
                    else:
                        # Otherwise, it's a variable method
                        className = self.classTable.typeOf(token.value)
                        numArgs = 1
                        self.writer.writePush(self.classTable.kindOf(token.value),
                                                self.classTable.indexOf(token.value))
                else:
                    # If the variable is defined in the current subroutine, use its type
                    className = self.subRoutineTable.typeOf(token.value)
                    numArgs = 1
                    self.writer.writePush(self.subRoutineTable.kindOf(token.value),
                                            self.subRoutineTable.indexOf(token.value))

                # Skip the dot
                self.tokenizer.advance()

                # Expecting a subroutine name (identifier) after the dot
                self.tokenizer.advance()
                if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                    raise ValueError(f"Expected subroutine name but got {self.tokenizer.currentToken().value}")
                subName = self.tokenizer.currentToken().value    

                # Expecting an opening parenthesis '(' for the expression list
                self.tokenizer.advance()
                if self.tokenizer.currentToken().value != "(":
                    raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")

                # Compile the expression list
                numArgs += self.compileExpressionList()

                # Write the VM call command
                self.writer.writeCall(f"{className}.{subName}", numArgs)
                
                # Expecting a closing parenthesis ')'
                self.tokenizer.advance()
                if self.tokenizer.currentToken().value != ")":
                    raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
            elif token.value == "(":
                # Subroutine call without class or variable name
                funcName = self.tokenizer.currentToken().value
                self.tokenizer.advance()
                numArgs = 0

                # Compile the expression list
                self.writer.writePush(VMSegment.POINTER, 0)
                numArgs += self.compileExpressionList()

                # Write the VM call command
                self.writer.writeCall(f"{self.classname}.{funcName}", numArgs)

                # Expecting a closing parenthesis ')'
                self.tokenizer.advance()
                if self.tokenizer.currentToken().value != ")":
                    raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
            else:
                varName = self.tokenizer.currentToken().value
                # Variable name 
                if self.subRoutineTable.indexOf(varName) == -1:
                    # If the variable is not defined in the current subroutine, check the class table
                    if self.classTable.indexOf(varName) == -1:
                        raise ValueError(f"Variable '{varName}' is not defined.")
                    elif self.classTable.kindOf(varName) == VariableKind.STATIC:
                        self.writer.writePush(self.classTable.kindOf(varName), self.classTable.indexOf(varName))
                    elif self.classTable.kindOf(varName) == VariableKind.FIELD:
                        # Check if this is pass as an argument to a method
                        if self.curFuncType in ["constructor", "method"]:
                            # If subroutine is a constructor or method, we can access the field directly
                            self.writer.writePush(VMSegment.THIS, self.classTable.indexOf(varName))
                        else:
                            # If 'this' is not defined, we cannot access the field
                            raise ValueError(f"Field '{varName}' cannot be accessed without object.")
                else:
                    # If the variable is defined in the current subroutine, use its type
                    self.writer.writePush(self.subRoutineTable.kindOf(varName), self.subRoutineTable.indexOf(varName))
        else:
            raise ValueError(f"Unexpected token in term: {token.value}")

    def compileExpressionList(self) -> int:
        """
        Compiles an expression list from the Jack source code.
        An expression list can be empty or contain multiple expressions separated by commas.

        :return: The number of expressions in the list.
        """
        numExpr = 0
        # If the next token is a closing parenthesis, we have an empty expression list
        if self.tokenizer.nextToken().value == ")":
            return numExpr

        # Expecting at least one expression
        self.compileExpression()
        numExpr += 1

        # Check for additional expressions separated by commas
        while self.tokenizer.nextToken().value == ",":
            self.tokenizer.advance()
            # Expecting another expression after the comma
            self.compileExpression()
            numExpr += 1
        return numExpr

class JackCompiler:
    """
    A class to analyze and compile Jack source code files.
    This class uses the JackTokenizer and CompilationEngine to process the source code.
    """
    
    def __init__(self, inputpath: str):
        """
        Initializes the JackAnalyzer with a input path.

        :param inputpath: The path to the Jack source code file or folder.
        """
        if Path(inputpath).is_dir():
            # If the input is a directory, process all .jack files in it
            self.files = list(Path(inputpath).glob("*.jack"))
        else:
            self.files = [Path(inputpath)]

    def compile(self):
        """
        Analyzes the Jack source code by compiling it.
        """
        for filepath in self.files:
            if not filepath.suffix == ".jack":
                raise ValueError(f"File {filepath} is not a Jack source code file.")
            tokenizer = JackTokenizer(filepath)
            engine = CompilationEngine(tokenizer, output_file=filepath.with_suffix(".vm"))
            engine.run()

if __name__ == "__main__":
    # Example usage
    filepath = sys.argv[1] 
    JackCompiler(filepath).compile()

        