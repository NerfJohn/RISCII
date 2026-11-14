################################################################################
# dasm: DasmPrinter.py
################################################################################

from enum import Enum
from typing import List

from AsmFormatter import NumType, immString, instrString
from ImageParser import RawImage, WORD_SIZE_BITS, WORD_SIZE_BYTES
from InstrParser import InstrFields
from MyLog  import LogLvl, MyLog

"""
Note: This file's interpretation addresses is based on doc PR2000.
"""

################################################################################

# File Parameters.
__FOUT_DIV     = '=' * 80
__FOUT_LF      = '\n'
__FOUT_DROW    = 8
__FOUT_COL_SEP = '|'
__FOUT_ROW_SEP = " "

################################################################################
# Helpers to format prefix for lines.
def genHeaderLabel(useAddr, useOrig) -> str:
    # Result.
    res = ""

    # Generate columns.
    if useAddr: 
        addr = immString(0, WORD_SIZE_BITS, NumType.HEX16, True)
        res += f"{'Addr'.ljust(len(addr)+2)} {__FOUT_COL_SEP}"
    if useOrig:
        val = immString(0, WORD_SIZE_BITS, NumType.HEX16, True)
        res += f"{'Raw'.ljust(len(val))} {__FOUT_COL_SEP}"

    # Return.
    return res
def genHeaderText(addrIdx: int = None, origVal: int = None) -> str:
    # Result.
    res = ""

    # Generate columns.
    if addrIdx != None: 
        addr = immString((addrIdx * WORD_SIZE_BYTES), WORD_SIZE_BITS, NumType.HEX16, True)
        res += f"T+{addr} {__FOUT_COL_SEP}"
    if origVal != None:
        val = immString(origVal, WORD_SIZE_BITS, NumType.HEX16, True)
        res += f"{val} {__FOUT_COL_SEP}"

    # Return.
    return res
def genHeaderData(addrIdx: int = None, origCol: bool = False) -> str:
    # Result.
    res = ""

    # Generate columns.
    if addrIdx != None: 
        addr = immString((addrIdx * WORD_SIZE_BYTES), WORD_SIZE_BITS, NumType.HEX16, True)
        res += f"D+{addr} {__FOUT_COL_SEP}"
    if origCol:
        val = immString(0, WORD_SIZE_BITS, NumType.HEX16, True)
        res += f"{'-' * len(val)} {__FOUT_COL_SEP}"

    # Return.
    return res

################################################################################
# Prints translated contents of the image into a file.
def printDasm(fname: str, inFile: str, image: RawImage, instrs: List[InstrFields],
              immType: NumType, doAddr: bool, doRaw: bool):
    # Begin writing to file.
    MyLog.log(LogLvl.DEBUG, f"Opening '{fname}' file")
    with open(fname, "w") as f:
        # Header.
        MyLog.log(LogLvl.DEBUG, f"Writing file header")
        hdr = [__FOUT_DIV, f"dasm: {inFile} ({image.origSize} bytes) -> {fname}", __FOUT_DIV]
        for l in hdr: f.write(l + __FOUT_LF)

        # Text section.
        MyLog.log(LogLvl.DEBUG, f"Writing text section")
        txtHdr = [f"{genHeaderLabel(doAddr, doRaw)}TEXT SECTION ({len(image.text)} words)", __FOUT_DIV]
        for l in txtHdr: f.write(l + __FOUT_LF)
        for i in range(len(instrs)):
            instr = instrs[i]
            prefix = genHeaderText(i if doAddr else None, image.text[i] if doRaw else None)
            f.write(prefix + instrString(instr, immType, True) + __FOUT_LF)

        # Data section.
        MyLog.log(LogLvl.DEBUG, f"Writing data section")
        dataHdr = [__FOUT_DIV, f"{genHeaderLabel(doAddr, doRaw)}DATA SECTION ({len(image.data)} words)", __FOUT_DIV]
        for l in dataHdr: f.write(l + __FOUT_LF)
        for i in range(0, len(image.data), __FOUT_DROW):
            for j in range(min(__FOUT_DROW, len(image.data[i:]))):
                data = image.data[i + j]
                if j > 0: f.write(__FOUT_ROW_SEP)
                else:
                    f.write(genHeaderData(i+j if doAddr else None, doRaw))
                f.write(immString(data, WORD_SIZE_BITS, immType, True))
            f.write(__FOUT_LF)
        f.write(__FOUT_DIV + __FOUT_LF)
    MyLog.log(LogLvl.DEBUG, f"Closed '{fname}' file")
