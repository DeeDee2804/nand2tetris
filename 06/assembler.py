import re

class PureAsm():
    predefined_symbol_table = {
        'SP': 0,
        'LCL': 1,
        'ARG': 2,
        'THIS': 3,
        'THAT': 4,
    		'R0': 0,
    		'R1': 1,
    		'R2': 2,
    		'R3': 3,
    		'R4': 4,
    		'R5': 5,
    		'R6': 6,
    		'R7': 7,
    		'R8': 8,
    		'R9': 9,
    		'R10': 10,
    		'R11': 11,
    		'R12': 12,
    		'R13': 13,
    		'R14': 14,
    		'R15': 15,
        'SCREEN': 16384,
        'KBD': 24567
    }
    
    def __init__(self) -> None:
        self.symbolic_content: list[str] = []
        self.bin_content: list[str] = []
        self.symbol_table = PureAsm.predefined_symbol_table
        self.length = 0
        self.next_mem_loc = 16
    
    def parse(self, filename: str):
        with open(filename, 'r') as asm:
            for line in asm.readlines():
                line = line.strip()
                line = self.removeSpace(line)
                line = self.removeComment(line)
                if self.isEmpty(line):
                    continue    
                self.symbolic_content.append(line)
    
    def scan_label(self):
        count = 0
        for line in self.symbolic_content:
            if match:= re.match(r"^\((.*?)\)$", line):
                self.symbol_table[f'{match[1]}'] = count
            else:
                count += 1
    
    def convert2bin(self):
        for line in self.symbolic_content:
            if line.startswith('@'):
                command = self.parseAtype(line)
            elif line.startswith('('):
                continue
            else:
                command = self.parseCtype(line)
            self.bin_content.append(command)

    def parseAtype(self, line) -> str:
        if match:= re.match('@(\d+)', line):
            mem_loc = int(match[1])
        elif match:= re.match('@(.+)', line):
            if match[1] not in self.symbol_table:
                self.symbol_table[match[1]] = self.next_mem_loc
                self.next_mem_loc += 1
            mem_loc = self.symbol_table[match[1]]
        return f"{mem_loc:016b}"
    
    def parseCtype(self, line) -> str:
        field = re.match(r'(?:(?P<dest>[MAD]{0,3})=)?(?P<comp>[01MAD\+\-\&\|\!]+)(?:;(?P<jump>JGT|JEQ|JGE|JLT|JNE|JLE|JMP|))?', line)
        # print(field['dest'], field['comp'], field['jump'])

        # Parsing the a value
        if 'M' in field['comp']:
            a=1
            symbol='M'
        else:
            a=0
            symbol='A'

        # Parsing the computation part
        match field['comp']:
            case '0': comp='101010'
            case '1': comp='111111'
            case '-1': comp='111010'
            case 'D': comp='001100'
            case '!D': comp='001101'
            case '-D': comp='001111'
            case 'D+1': comp='011111'
            case 'D-1': comp='001110'
            case x if x==symbol: comp='110000'
            case x if x==f'!{symbol}': comp='110001'
            case x if x==f'-{symbol}': comp='110011'
            case x if x==f'{symbol}+1': comp='110111'
            case x if x==f'{symbol}-1': comp='110010'
            case x if x==f'D+{symbol}': comp='000010'
            case x if x==f'D-{symbol}': comp='010011'
            case x if x==f'{symbol}-D': comp='000111'
            case x if x==f'D&{symbol}': comp='000000'
            case x if x==f'D|{symbol}': comp='010101'

        # Parsing the destination part
        d1=0
        d2=0
        d3=0
        if field['dest']:
            if 'M' in field['dest']:
                d3=1
            if 'D' in field['dest']:
                d2=1
            if 'A' in field['dest']:
                d1=1
                
        # Parsing the jump part
        j1=0
        j2=0
        j3=0
        if field['jump'] in ['JGT', 'JMP', 'JGE', 'JNE']:
            j3 = 1
        if field['jump'] in ['JEQ', 'JGE', 'JLE', 'JMP']:
            j2 = 1
        if field['jump'] in ['JLT', 'JNE', 'JLE', 'JMP']:
            j1 = 1
        return f"111{a}{comp}{d1}{d2}{d3}{j1}{j2}{j3}"
            
    @staticmethod
    def isEmpty(line: str) -> bool:
        return not line
    
    @staticmethod
    def removeComment(line: str) -> str:
        return re.sub(r"//.*", "", line)
    
    @staticmethod
    def removeSpace(line: str) -> str:
        return re.sub(r"\s+", "", line)
    
    def show(self):
        print('\n'.join(self.symbolic_content))
        print('\n'.join(self.bin_content))
    
    def export2bin(self, fileasm: str):
        self.parse(fileasm)
        self.scan_label()
        self.convert2bin()
        filehack = fileasm[:-4] + '.hack'
        with open(filehack, 'w') as f:
            f.write('\n'.join(self.bin_content))

filenames=['pong.asm', 'add.asm', 'max.asm', 'rect.asm']
for filename in filenames:
    asm = PureAsm()
    asm.export2bin(filename)
