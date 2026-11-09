################################################################################
# dasm: InstrParser.py
################################################################################

from collections import deque
from enum import Enum
from typing import List

from MyLog import LogLvl, MyLog

"""
Note: This file's interpretation of instructions is based on doc PR2000.
"""

################################################################################
# Broken up version of an instruction.
class InstrFields():
    # Consts.
    NUM_REGS = 3

    # Values.
    opcode: str       # instruction type            - should always be populated
    flags:  str       # instruction specific flags  - set to None if unused
    regs:   List[int] # 3 possible register operands- each set to None if unused
    imm:    int       # immediate value             - set to None if unused

    # Funcs.
    def __init__(self, opcode: str):
        self.opcode = opcode
        self.flags  = None
        self.regs   = []
        for i in range(self.NUM_REGS): self.regs.append(None)
        self.imm    = None

################################################################################
# Opcodes of the ISA.
class __Op(Enum):
    NOP = 0
    SWP = 1
    BRC = 2
    HLT = 3
    STR = 4
    LDR = 5
    JPR = RTI = 6 # distinguished by flag bit
    JLR = 7
    ADD = 8
    SUB = 9
    LBI = 10
    XOR = 11
    SHL = 12
    SHR = 13
    ORR = 14
    AND = 15

################################################################################
# Converts 16-bit integer into an opcode.
def __asOpcodeStr(instr: int) -> str:
    # Result.
    res = ""

    # Std opcodes (based on first 4 bits).
    stdOps = [
        "NOP", "SWP", "BRC", "HLT",
        "STR", "LDR", "JPR", "JLR",
        "ADD", "SUB", "LBI", "XOR",
        "SHL", "SHR", "ORR", "AND"
    ]

    # Determine opcode (including JPR/RTI detail).
    res = stdOps[(instr & 0xF000) >> 12]
    if (res == "JPR") and (instr & 0x0020):
        res = "RTI"

    # Return.
    return res

################################################################################
# Converts 16-bit integer into flags (or None if not applicable).
def __asFlagStr(instr: int) -> str:
    # Result.
    res = None

    # Determine flags by opcode.
    opcode = __Op((instr & 0xF000) >> 12)
    if   (opcode == __Op.SHR) and (instr & 0x0020):
        res = "%a"
    elif (opcode == __Op.LBI) and (instr & 0x0100):
        res = "%s"
    elif (opcode == __Op.BRC) and (instr & 0x0F00):
        res = "%"
        if instr & 0x0800: res += "n"
        if instr & 0x0400: res += "z"
        if instr & 0x0200: res += "p"
        if instr & 0x0100: res += "c"

    # Return.
    return res

################################################################################
# Converts instruction into registers (given offset of each- None for N/A).
def __asRegs(instr: int, offsets: List[int] = None) -> List[int]:
    # Result.
    res = [None, None, None]
    
    # Validate.
    if offsets == None or len(offsets) != 3:
        MyLog.log(LogLvl.ERROR, "TOOL ERROR: __asRegs given bad offsets")
        return res

    # Get regs.
    for i in range(len(offsets)):
        if offsets[i] != None:
            res[i] = (instr >> offsets[i]) & 0x0007

    # Return.
    return res

################################################################################
# Converts instruction into immediate (starting from offset, filtered to bit length).
def __asImmInt(instr: int, bitLen: int, offset: int = 0) -> int:
    mask = ~(0xFFFF << bitLen) & 0xFFFF
    return (instr >> offset) & mask

################################################################################
# Check/warn about unused bits (indicated by set bits).
def __warnUnuseds(instr: int, mask: int):
    if instr & mask: MyLog.log(LogLvl.WARNING, f"Instruction 0x{instr:04X} has unused bits")

################################################################################
# Breaks out 16-bit instruction into separate parts. Logs own errors.
def parseAsInstr(instr: int) -> InstrFields:
    # Result (+ determine opcode).
    res = InstrFields(__asOpcodeStr(instr))

    # Determine flags.
    res.flags = __asFlagStr(instr)

    # Determine register/immediate args + unused bits based on format.
    opcode = __Op((instr & 0xF000) >> 12)
    if opcode in [__Op.AND, __Op.ORR, __Op.XOR, __Op.ADD, __Op.SUB]:
        # Data reg-imm5 vs Data reg-reg formats.
        if instr & 0x0020:
            res.regs = __asRegs(instr, [9,6, None])
            res.imm  = __asImmInt(instr, 5, 0)
            # All bits used as is
        else:
            res.regs = __asRegs(instr, [9, 6, 0])
            __warnUnuseds(instr, 0x0038)
    elif opcode == __Op.SHL:
        # Data reg-imm4 vs Data reg-reg formats.
        if instr & 0x0020:
            res.regs = __asRegs(instr, [9, 6, None])
            res.imm  = __asImmInt(instr, 4, 0)
            __warnUnuseds(instr, 0x0010)
        else:
            res.regs = __asRegs(instr, [9, 6, 0])
            __warnUnuseds(instr, 0x0010)
    elif opcode == __Op.SHR:
        # Data reg-imm4 w/ flag vs Data reg-reg w/ flag formats.
        if instr & 0x0020:
            res.regs = __asRegs(instr, [9, 6, None])
            res.imm  = __asImmInt(instr, 4, 0)
            # All bits used as is
        else:
            res.regs = __asRegs(instr, [9, 6, 0])
            __warnUnuseds(instr, 0x0028)
    elif opcode == __Op.LBI:
        res.regs = __asRegs(instr, [9, None, None])
        res.imm  = __asImmInt(instr, 8, 0)
        # All bits used as is
    elif opcode in [__Op.LDR, __Op.STR, __Op.SWP]:
        res.regs = __asRegs(instr, [9, 6, None])
        res.imm  = __asImmInt(instr, 6, 0)
        # All bits used as is
    elif opcode == __Op.BRC:
        res.imm  = __asImmInt(instr, 8, 0)
        # All bits used as is
    elif opcode == __Op.JLR:
        res.regs = __asRegs(instr, [9, 6, None])
        res.imm  = __asImmInt(instr, 5, 0)
        __warnUnuseds(instr, 0x0020)      
    elif opcode == __Op.JPR:
        # RTI vs JPR formats.
        if instr & 0x0020:
            __warnUnuseds(instr, 0x0FDF)
        else:
            res.regs = __asRegs(instr, [None, 6, None])
            res.imm  = __asImmInt(instr, 5, 0)
            __warnUnuseds(instr, 0x0020)
    elif opcode in [__Op.NOP, __Op.HLT]:
        __warnUnuseds(instr, 0x0FFF)
    else:
        MyLog.log(LogLvl.ERROR, "TOOL ERROR: Bad opcode generated")

    # Return
    return res
