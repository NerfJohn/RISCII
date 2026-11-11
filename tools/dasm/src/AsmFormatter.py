################################################################################
# dasm: AsmFormatter.py
################################################################################

from enum import Enum

from InstrParser import InstrFields

################################################################################

# String Params.
__OP_LEN   = 4
__FLAG_LEN = 6
__REG_LEN  = 4
__IMM_LEN  = 6

################################################################################
# Enum for defining representations of numbers.
class NumType(Enum):
    INT16  = "int"
    UINT16 = "uint"
    HEX16  = "hex"

################################################################################
# Format 16-bit integer (or immediate) into string.
def immString(imm: int, immLen = 16, immType: NumType = NumType.HEX16, with0x = True) -> str:
    if immType == NumType.HEX16: 
        if with0x: return f"0x{imm:04X}".ljust(__IMM_LEN)
        else:      return f"{imm:04X}".ljust(__IMM_LEN)
    elif immType == NumType.INT16:
        if 2**(immLen-1) > imm: return str(imm).ljust(__IMM_LEN)
        else:                   return str(-(2**(immLen) - imm)).ljust(__IMM_LEN)
    return str(imm).ljust(__IMM_LEN)

################################################################################
# Format instruction into string.
def instrString(fields: InstrFields, immType: NumType = NumType.HEX16, withOx = True) -> str:
    # Result.
    res = ""

    # Add fields.
    res += fields.opcode.ljust(__OP_LEN)
    if fields.flags != None: res += fields.flags.ljust(__FLAG_LEN)
    else:                    res += "".ljust(__FLAG_LEN)
    for r in fields.regs:
        if r != None: res += f"${r}".ljust(__REG_LEN)
        else        : res += "".ljust(__REG_LEN)
    if fields.imm != None: res += immString(fields.imm, fields.immLen, immType, withOx)

    # Return.
    return res.strip()
    