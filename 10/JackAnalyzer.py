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
        self.content = []
        self.tablevel = 0
        self.name = output_file.stem
        self.output_file = output_file.with_name(f"my{output_file.stem}.xml")
        

    def compile(self):
        """
        Compiles the Jack source code using the tokenizer.
        """
        # The first valid token should be a class keyword
        self.compileClass()
        if self.tokenizer.hasMoreTokens():
            raise ValueError("Unexpected tokens after class definition.")
        if self.output_file:
            with open(self.output_file, 'w') as f:
                f.write("\n".join(self.content))
                f.write("\n")

    def addOpenTag(self, tag: str):
        """
        Adds an opening tag to the compilation engine's content list.
        
        :param tag: The tag to add.
        """
        self.content.append(f"{'  ' * self.tablevel}<{tag}>")
        self.tablevel += 1

    def addCloseTag(self, tag: str):
        """
        Adds a closing tag to the compilation engine's content list.
        
        :param tag: The tag to close.
        """
        self.tablevel -= 1
        self.content.append(f"{'  ' * self.tablevel}</{tag}>")
        
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

            self.addOpenTag("class")
            self.addSimpleTag()

            # Expecting a class name (identifier) after 'class'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected class name but got {self.tokenizer.currentToken().value}")
            if self.tokenizer.currentToken().value != self.name:
                raise ValueError(f"Expected class name '{self.name}' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()

            # Expecting an opening brace '{' after the class name
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "{":
                raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()
           

            # Process class variable declarations and subroutines until we reach the closing brace '}'
            endVarDec = False
            while self.tokenizer.nextToken().value != "}":
                if self.tokenizer.nextToken().value in {"static", "field"}:
                    if endVarDec:
                        raise ValueError("Variable declaration must only be placed at the beginning of the class.")
                    self.compileClassVarDec()
                elif self.tokenizer.nextToken().value in {"constructor", "function", "method"}:
                    # Subroutine declaration must come after variable declarations
                    endVarDec = True
                    self.compileSubroutine()
                else:
                    raise ValueError(f"Unexpected token in class body: {self.tokenizer.nextToken().value}")

            # Expecting a closing brace '}' at the end of the class body
            self.tokenizer.advance()
            self.addSimpleTag()
            self.addCloseTag("class")

    def compileClassVarDec(self):
        """
        Compiles a class variable declaration from the Jack source code.
        The valid structure for a class variable declaration is:
            'static' | 'field' type varName (',' varName)* ';'
        """
        self.tokenizer.advance()
        # Expecting a keyword 'static' or 'field'
        if self.tokenizer.currentToken().value not in {"static", "field"}:
            raise ValueError(f"Expected 'static' or 'field' but got {self.tokenizer.currentToken().value}")
        
        self.addOpenTag("classVarDec")
        self.addSimpleTag()

        # Expecting a type (int, char, boolean, or identifier)
        self.compileType()
        
        # Expecting an identifier (variable name)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        self.tokenizer.advance()
        while self.tokenizer.currentToken().value == ",":
            # Expecting a comma ',' followed by another identifier
            self.addSimpleTag()
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()
            self.tokenizer.advance()

        # Expecting a semicolon ';' at the end of the declaration
        if self.tokenizer.currentToken().value != ";":  
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()
        self.addCloseTag("classVarDec")

    def compileSubroutine(self):
        """
        Compiles a subroutine from the Jack source code.
        The valid structure for a subroutine is:
            ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        where parameterList can be empty and subroutineBody contains variable declarations and statements.
        """
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value not in {"constructor", "function", "method"}:
            raise ValueError(f"Expected 'constructor', 'function', or 'method' but got {self.tokenizer.currentToken().value}")
        self.addOpenTag("subroutineDec")
        self.addSimpleTag()

        # Expecting a return type (void or type)
        if self.tokenizer.nextToken().value == "void":
            self.tokenizer.advance()
            self.addSimpleTag()
        else:
            self.compileType()
        
        # Expecting a subroutine name (identifier)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected subroutine name but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting an opening parenthesis '(' for the parameter list
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "(":
            raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Compile the parameter list
        self.compileParameterList()

        # Expecting a closing parenthesis ')' after the parameter list
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ")":
            raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()
        
        # Compile the subroutine body
        self.compileSubroutineBody()

        # Expecting the end of the subroutine declaration
        self.addCloseTag("subroutineDec")

    def compileType(self):
        """
        Compiles a type from the Jack source code.
        The valid types are 'int', 'char', 'boolean', or an identifier.
        
        :raises ValueError: If the current token is not a valid type.
        """
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value in {"int", "char", "boolean"}:
            self.addSimpleTag()
        elif self.tokenizer.currentToken().token_type == TokenType.IDENTIFIER:
            self.addSimpleTag()
        else:
            raise ValueError(f"Expected type but got {self.tokenizer.currentToken().value}")

    def compileParameterList(self):
        """
        Compiles a parameter list from the Jack source code.
        The valid structure for a parameter list is:
            (type varName ("," type varName)*)
        """
        self.addOpenTag("parameterList")
        # If the next token is a closing parenthesis, we have an empty parameter list
        if (self.tokenizer.nextToken().value == ")"):
            self.addCloseTag("parameterList")
            return  # Empty parameter list
        
        # Expecting a type for the first parameter
        self.compileType()

        # Expecting a parameter name (identifier)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected parameter name but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Check for additional parameters (optional)
        while self.tokenizer.nextToken().value == ",":
            self.tokenizer.advance()
            self.addSimpleTag()

            # Expecting a comma ',' followed by another type
            self.compileType()

            # Expecting a parameter name (identifier)
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected parameter name but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()

        # After processing all parameters, we should be at the closing parenthesis
        self.addCloseTag("parameterList")           

    def compileSubroutineBody(self):
        """
        Compiles a subroutine body from the Jack source code.
        The valid structure for a subroutine body is:
            '{' varDec* statements '}'
        """
        self.addOpenTag("subroutineBody")

        # Expecting an opening brace '{' for the subroutine body
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "{":
            raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Process variable declarations
        while self.tokenizer.nextToken().value == "var":
            self.tokenizer.advance()
            self.compileVarDec()
            
        # Compile the statements within the subroutine body
        self.compileStatements()

        # Expecting a closing brace '}' for the subroutine body
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "}":
            raise ValueError(f"Expected '}}' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()
        self.addCloseTag("subroutineBody")

    def compileVarDec(self):
        """
        Compiles a variable declaration from the Jack source code.
        Pre-condition: Need to advance tokenizer before calling this method.
        The valid structure for a variable declaration is:
            'var' type varName (',' varName)* ';'
        """
        if self.tokenizer.currentToken().value != "var":
            raise ValueError(f"Expected 'var' but got {self.tokenizer.currentToken().value}")
        
        self.addOpenTag("varDec")
        self.addSimpleTag()

        # Expecting a type (int, char, boolean, or identifier)
        self.compileType()

        # Expecting a variable name (identifier)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Check for additional variable names
        self.tokenizer.advance()
        while self.tokenizer.currentToken().value == ",":
            self.addSimpleTag()
            # Expecting a comma ',' followed by another identifier
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()
            self.tokenizer.advance()

        # Expecting a semicolon ';' at the end of the declaration
        if self.tokenizer.currentToken().value != ";":
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()
        self.addCloseTag("varDec")

    def compileStatements(self):
        """
        Compiles statements from the Jack source code.\n
        The valid structure for statements is:\n
            statement*\n
        """
        self.addOpenTag("statements")
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
                self.compileReturn()
            else:
                raise ValueError(f"Unexpected statement type: {self.tokenizer.nextToken().value}")
        self.addCloseTag("statements")

    def compileLet(self):
        """
        Compiles a 'let' statement from the Jack source code.  
        The valid structure for a 'let' statement is:
            'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.addOpenTag("letStatement")

        # Expecting a 'let' keyword
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "let":
            raise ValueError(f"Expected 'let' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting a variable name (identifier)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected variable name but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Check for array access (optional)
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value == "[":
            self.addSimpleTag()
            # Expecting an expression inside the brackets
            self.compileExpression()

            # Expecting a closing bracket ']'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "]":
                raise ValueError(f"Expected ']' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()
            self.tokenizer.advance()
        elif self.tokenizer.currentToken().value != "=":
            # If we are not accessing an array, we should be at the assignment operator
            raise ValueError(f"Expected '[' or '=' but got {self.tokenizer.currentToken().value}")
        
        # Now we should be at the assignment operator '='
        self.addSimpleTag()

        # Expecting an expression after the '='
        self.compileExpression()

        # Expecting a semicolon ';'
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ";":
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()
        self.addCloseTag("letStatement")

    def compileIf(self):
        """
        Compiles an 'if' statement from the Jack source code.
        The valid structure for an 'if' statement is:
            'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.addOpenTag("ifStatement")

        # Expecting a 'if' keyword
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "if":
            raise ValueError(f"Expected 'if' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting an opening parenthesis '('
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "(":
            raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting an expression inside the parentheses
        self.compileExpression()

        # Expecting a closing parenthesis ')'
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ")":
            raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting an opening brace '{' for the statements block
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "{":
            raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Compile the statements inside the 'if' block
        self.compileStatements()

        # Expecting a closing brace '}' for the 'if' block
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "}":
            raise ValueError(f"Expected '}}' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Check for an optional 'else' clause
        if self.tokenizer.nextToken().value == "else":
            self.tokenizer.advance()
            self.addSimpleTag()
            # Expecting an opening brace '{' for the 'else' block
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "{":
                raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()

            # Compile the statements inside the 'else' block
            self.compileStatements()

            # Expecting a closing brace '}' for the 'else' block
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "}":
                raise ValueError(f"Expected '}}' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()

        self.addCloseTag("ifStatement")

    def compileWhile(self):
        """
        Compiles a 'while' statement from the Jack source code.
        The valid structure for a 'while' statement is:
            'while' '(' expression ')' '{' statements '}'
        """
        self.addOpenTag("whileStatement")

        # Expecting a 'while' keyword
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "while":
            raise ValueError(f"Expected 'while' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting an opening parenthesis '('
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "(":
            raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting an expression inside the parentheses
        self.compileExpression()

        # Expecting a closing parenthesis ')'
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ")":
            raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting an opening brace '{' for the statements block
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "{":
            raise ValueError(f"Expected '{{' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Compile the statements inside the 'while' block
        self.compileStatements()

        # Expecting a closing brace '}' for the 'while' block
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "}":
            raise ValueError(f"Expected '}}' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        self.addCloseTag("whileStatement")    

    def compileDo(self):
        """
        Compiles a 'do' statement from the Jack source code.
        The valid structure for a 'do' statement is:
            'do' subroutineCall ';'
        """
        self.addOpenTag("doStatement")

        # Expecting a 'do' keyword
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != "do":
            raise ValueError(f"Expected 'do' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        # Expecting a subroutine call
        self.tokenizer.advance()
        if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
            raise ValueError(f"Expected subroutine name but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()
        
        # Check for subroutine call structure
        token = self.tokenizer.nextToken()
        if token.value == "(":
            # Subroutine call without class or variable name
            self.tokenizer.advance()
            self.addSimpleTag()

            # Compile the expression list
            self.compileExpressionList()

            # Expecting a closing parenthesis ')'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != ")":
                raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()
        elif token.value == ".":
            # Subroutine call with class or variable name
            self.tokenizer.advance()
            self.addSimpleTag()

            # Expecting a subroutine name (identifier) after the dot
            self.tokenizer.advance()
            if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                raise ValueError(f"Expected subroutine name but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()

            # Expecting an opening parenthesis '(' for the expression list
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != "(":
                raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()

            # Compile the expression list
            self.compileExpressionList()
            
            # Expecting a closing parenthesis ')'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != ")":
                raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()

        # Expecting a semicolon ';' at the end
        self.tokenizer.advance()
        if self.tokenizer.currentToken().value != ";":
            raise ValueError(f"Expected ';' but got {self.tokenizer.currentToken().value}")
        self.addSimpleTag()

        self.addCloseTag("doStatement")

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

        self.addOpenTag("returnStatement")
        self.addSimpleTag()

        # Expecting an expression after 'return' (optional)
        if self.tokenizer.nextToken().value != ";":
            self.compileExpression()

        # Expecting a semicolon ';' at the end
        self.tokenizer.advance()
        self.addSimpleTag()

        self.addCloseTag("returnStatement")

    def compileExpression(self):
        """
        Compiles an expression from the Jack source code.
        The valid structure for an expression is:
            term (op term)*
        """
        self.addOpenTag("expression")
        # Expecting a term as the first part of the expression
        self.compileTerm()

        # Check for additional terms with operators (optional)
        while self.tokenizer.nextToken().value in self.ops:
            self.tokenizer.advance()
            self.addSimpleTag()
            # Advance to the next token which should be a term
            self.compileTerm()
        self.addCloseTag("expression")

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
        self.addOpenTag("term")
        self.tokenizer.advance()
        token = self.tokenizer.currentToken()
        if token.token_type == TokenType.INT_CONST:
            # Integer constant
            self.addSimpleTag()
        elif token.token_type == TokenType.STRING_CONST:
            # String constant
            self.addSimpleTag()
        elif token.value in {"true", "false", "null", "this"}:
            # Keyword constant
            self.addSimpleTag()
        elif token.value == "(":
            self.addSimpleTag()
            # Expression in parentheses
            self.compileExpression()

            # Expecting a closing parenthesis ')'
            self.tokenizer.advance()
            if self.tokenizer.currentToken().value != ")":
                raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
            self.addSimpleTag()
        elif token.value in self.unary_ops:
            # Unary operation
            self.addSimpleTag()
            # Expecting a term after the unary operator
            self.compileTerm()
        elif token.token_type == TokenType.IDENTIFIER:
            # Variable name or subroutine call
            self.addSimpleTag()
            token = self.tokenizer.nextToken()
            if token.value == "[":
                # Array access
                self.tokenizer.advance()
                self.addSimpleTag()
                
                # Expecting an expression inside the brackets
                self.compileExpression()

                # Expecting a closing bracket ']'
                self.tokenizer.advance()
                if self.tokenizer.currentToken().value != "]":
                    raise ValueError(f"Expected ']' but got {self.tokenizer.currentToken().value}")
                self.addSimpleTag()
            elif token.value == ".":
                # Subroutine call with class or variable name
                self.tokenizer.advance()
                self.addSimpleTag()

                # Expecting a subroutine name (identifier) after the dot
                self.tokenizer.advance()
                if self.tokenizer.currentToken().token_type != TokenType.IDENTIFIER:
                    raise ValueError(f"Expected subroutine name but got {self.tokenizer.currentToken().value}")
                self.addSimpleTag()

                # Expecting an opening parenthesis '(' for the expression list
                self.tokenizer.advance()
                if self.tokenizer.currentToken().value != "(":
                    raise ValueError(f"Expected '(' but got {self.tokenizer.currentToken().value}")
                self.addSimpleTag()

                # Compile the expression list
                self.compileExpressionList()
                
                # Expecting a closing parenthesis ')'
                self.tokenizer.advance()
                if self.tokenizer.currentToken().value != ")":
                    raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
                self.addSimpleTag()
            elif token.value == "(":
                # Subroutine call without class or variable name
                self.tokenizer.advance()
                self.addSimpleTag()

                # Compile the expression list
                self.compileExpressionList()

                # Expecting a closing parenthesis ')'
                self.tokenizer.advance()
                if self.tokenizer.currentToken().value != ")":
                    raise ValueError(f"Expected ')' but got {self.tokenizer.currentToken().value}")
                self.addSimpleTag()
        else:
            raise ValueError(f"Unexpected token in term: {token.value}")
        self.addCloseTag("term")

    def compileExpressionList(self):
        """
        Compiles an expression list from the Jack source code.
        An expression list can be empty or contain multiple expressions separated by commas.
        """
        self.addOpenTag("expressionList")
        # If the next token is a closing parenthesis, we have an empty expression list
        if self.tokenizer.nextToken().value == ")":
            self.addCloseTag("expressionList")
            return
        
        # Expecting at least one expression
        self.compileExpression()

        # Check for additional expressions separated by commas
        while self.tokenizer.nextToken().value == ",":
            self.tokenizer.advance()
            self.addSimpleTag()
            # Expecting another expression after the comma
            self.compileExpression()

        self.addCloseTag("expressionList")

class JackAnalyzer:
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

    def analyze(self):
        """
        Analyzes the Jack source code by compiling it.
        """
        for filepath in self.files:
            if not filepath.suffix == ".jack":
                raise ValueError(f"File {filepath} is not a Jack source code file.")
            tokenizer = JackTokenizer(filepath)
            engine = CompilationEngine(tokenizer, output_file=filepath.with_suffix(".xml"))
            engine.compile()

if __name__ == "__main__":
    # Example usage
    filepath = sys.argv[1] 
    JackAnalyzer(filepath).analyze()

  
        