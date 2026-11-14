################################################################################
# dasm: DasmPrinter.py
################################################################################

import os
from typing import List

from AsmFormatter import NumType, immString, instrString
from ImageParser import RawImage, WORD_SIZE_BITS
from InstrParser import InstrFields
from MyLog  import LogLvl, MyLog

################################################################################

# File Parameters.
__FOUT_DIV   = '=' * 80
__FOUT_LF    = '\n'
__FOUT_DROW  = 8

################################################################################
# Prints translated contents of the image into a file.
def printDasm(fname: str, inFile: str, immType: NumType, image: 
              RawImage, instrs) -> List[InstrFields]:
    # Begin writing to file.
    MyLog.log(LogLvl.DEBUG, f"Opening '{fname}' file")
    with open(fname, "w") as f:
        # Header.
        MyLog.log(LogLvl.DEBUG, f"Writing file header")
        hdr = [__FOUT_DIV, f"dasm: {inFile} ({image.origSize} bytes) -> {fname}", __FOUT_DIV]
        for l in hdr: f.write(l + __FOUT_LF)

        # Text section.
        MyLog.log(LogLvl.DEBUG, f"Writing text section")
        txtHdr = [f"TEXT SECTION ({len(image.text)} words)", __FOUT_DIV]
        for l in txtHdr: f.write(l + __FOUT_LF)
        for i in instrs:
            f.write(instrString(i, immType, True) + __FOUT_LF)

        # Data section.
        MyLog.log(LogLvl.DEBUG, f"Writing data section")
        dataHdr = [__FOUT_DIV, f"DATA SECTION ({len(image.data)} words)", __FOUT_DIV]
        for l in dataHdr: f.write(l + __FOUT_LF)
        for i in range(0, len(image.data), __FOUT_DROW):
            for j in range(min(__FOUT_DROW, len(image.data[i:]))):
                data = image.data[i + j]
                if j > 0: f.write(" ")
                f.write(immString(data, WORD_SIZE_BITS, immType, True))
            f.write(__FOUT_LF)
        f.write(__FOUT_DIV + __FOUT_LF)
    MyLog.log(LogLvl.DEBUG, f"Closed '{fname}' file")
